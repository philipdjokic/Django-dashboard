from datetime import datetime, timedelta
import json

from django import template
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_admins
from django.core.paginator import Paginator
from django.db import connection
from django.db.models import Sum, Case, When, IntegerField
from django.db.models.functions import Coalesce
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from natsort import natsorted
import requests

from data import models as data_models
from data import server_api
from data.forms import AlertRuleForm
import data.helpers as data_helpers

MAX_METADATA_UNIQUE_VALUES = 250


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def index(request):
    """
    List the projects a user has, if any
    """
    return redirect(reverse('project'))


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def alert_rule_toggle(request, aspect_rule_id):
    aspect_rule = data_models.AlertRule.objects.filter(
        pk=aspect_rule_id, project__users=request.user.id)
    if aspect_rule.count() == 0:
        raise PermissionDenied
    aspect_rule_obj = aspect_rule.get()
    aspect_rule_obj.active = not aspect_rule_obj.active
    aspect_rule_obj.save()
    return redirect("alerts")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def pages(request):
    context = {}

    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:
        load_template = request.path.split('/')[-1]
        html_template = loader.get_template(load_template)
        return HttpResponse(html_template.render(context, request))
    except template.TemplateDoesNotExist:
        html_template = loader.get_template('page-404.html')
        return HttpResponse(html_template.render(context, request))
    except Exception as e:
        html_template = loader.get_template('page-500.html')
        return HttpResponse(html_template.render(context, request))


class Projects(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        
        if len(projects) == 0 and 'welcome' not in request.GET:
            # Redirect to the ?welcome=1 URL so we show the UserGuiding walkthrough.
            return HttpResponseRedirect(reverse("project") + "?welcome=1")

        for project in projects:
            data = data_models.Data.objects.filter(project=project["id"]).aggregate(
                positive_count=Coalesce(Sum(Case(When(sentiment__gt=0, then=1)), output_field=IntegerField()), 0),
                negative_count=Coalesce(Sum(Case(When(sentiment__lt=0, then=1)), output_field=IntegerField()), 0),
                neutral_count=Coalesce(Sum(Case(When(sentiment=0, then=1)), output_field=IntegerField()), 0))
            project.update(data)

        context = {}
        context["projects_data"] = projects
        context["projects_count"] = len(projects)
        context["user"] = user

        context["all_aspects"] = []
        all_aspects = data_models.AspectModel.objects.filter(users=user).order_by("label")
        for aspect in all_aspects:
            context["all_aspects"].append({"id": aspect.id, "label": aspect.label})

        return render(request, "projects.html", context)

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        project_name = request.POST.get("project-name")
        aspect_id = request.POST.get("aspect-id")
        api_key = request.POST.get("api-key")

        if aspect_id != "-1":
            aspect = data_models.AspectModel.objects.get(pk=aspect_id)
            project = data_models.Project(aspect_model=aspect, name=project_name)
        else:
            project = data_models.Project(name=project_name)

        project.api_key = api_key
        project.save()
        project.users.add(user)
        project.save()

        return redirect("project", project.id)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def delete_project_details(request, project_id):
    p = get_object_or_404(data_models.Project, pk=project_id)
    p.delete()
    return redirect("project")


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def project_details(request, project_id):
    user = request.user
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))

    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied

    context = {}

    context["projects_data"] = projects
    context["project"] = this_project
    context["user"] = user
    context["sources"] = []
    context["sourceID"] = []
    context["languages"] = []

    source_query = """
        select distinct (ds.id) , ds."label", count(ds.id), ds.id 
        from data_source ds inner join data_data dd on ds.id = dd.source_id 
        where dd.project_id = %s group by ds.id order by count(ds.id) desc;"""

    with connection.cursor() as cursor:
        cursor.execute(source_query, [project_id])
        rows = cursor.fetchall()

    for row in rows:
        context["sources"].append({"sourceLabel": row[1], "sourceID": row[3]})

    context["languages"] = []
    languages = data_models.Data.objects.filter(
        project_id=project_id
    ).distinct('language').values_list("language", flat=True)

    for code, label in settings.LANGUAGES:
        if code in languages:
            context["languages"].append((code, label))

    if data_models.Data.objects.filter(project=project_id).count() != 0:
        d = data_models.Data.objects.filter(project=project_id).latest()
        latest = d.date_created
        earliest = data_models.Data.objects.filter(project=project_id).earliest().date_created

        context["default_date_to"] = latest.strftime("%Y-%m-%d")
        context["default_date_from"] = earliest.strftime("%Y-%m-%d")

    # Populate the metadata filters dropdowns.
    context["more_filters"] = []
    with connection.cursor() as cursor:
        cursor.execute(""" select distinct (jsonb_object_keys(dd.metadata))
        from data_data as dd where dd.metadata <> '""' and
        dd.project_id = %s """, [project_id])

        rows = cursor.fetchall()
        context["more_filters_with_many_values"] = []
        for row in rows:
            with connection.cursor() as metadata_cursor:
                metadata_cursor.execute("""
                select count (distinct (dd.metadata ->> %s))
                from data_data as dd where dd.project_id = %s """, 
                [row[0], project_id])

                possible_metadata_values = metadata_cursor.fetchone()[0]
                if possible_metadata_values > MAX_METADATA_UNIQUE_VALUES:
                    # Too many values to put in a dropdown.
                    context["more_filters_with_many_values"].append({"name": row[0]})
                    continue

                metadata_cursor.execute("""
                select distinct (dd.metadata ->> %s)
                from data_data as dd where dd.project_id = %s """, [row[0], project_id])
                metadata_rows = metadata_cursor.fetchall()
                metadata_values = []
                for metadata_row in metadata_rows:
                    metadata_values.append(metadata_row[0])
            context["more_filters"].append({"name": row[0], "values": natsorted(metadata_values)})

    # Fetch my teammates too.
    context['teammates'] = data_helpers.get_teammates(user)['teammates']
    context['access'] = this_project.users.all().values_list('username', flat=True)

    return render(request, "project-details.html", context)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    aspect_label = request.GET.get('aspect', '')
    sentiment = request.GET.get('sentiment', '')
    with connection.cursor() as cursor:
        if sentiment == 'neutral':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from
                data_aspect da inner join data_data dd on da.data_id = dd.id
                where dd.project_id = %s and dd.sentiment = 0 and da."label" =
                %s""", [this_project.id, aspect_label])
        elif sentiment == 'negative':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from
                data_aspect da inner join data_data dd on da.data_id = dd.id
                where dd.project_id = %s and dd.sentiment < 0 and da."label" =
                %s""", [this_project.id, aspect_label])
        elif sentiment == 'positive':
            cursor.execute("""
                select distinct dd.sentiment , dd."text", da."label" from
                data_aspect da inner join data_data dd on da.data_id = dd.id
                where dd.project_id = %s and dd.sentiment > 0 and da."label" =
                %s""", [this_project.id, aspect_label])
        rows = cursor.fetchall()
    return JsonResponse(rows, safe=False)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_per_entity(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()
    entities_limit = request.GET.get("max-entities", 8)
    with connection.cursor() as cursor:
        cursor.execute("""
        select dde.entity_id, de."label" , count(dde.entity_id) from
        data_data_entities dde inner join data_data dd on dd.id = dde.data_id
        inner join data_entity de on dde.entity_id = de.id where dd.project_id
        = %s group by (dde.entity_id, de."label") order by count(dde.entity_id)
        desc limit %s; """, [this_project.id, entities_limit])
        rows = cursor.fetchall()
    response = []
    for row in rows:
        data = data_models.Data.objects.filter(entities__pk=row[0], project_id=project_id)
        negative_count = data.filter(sentiment__lt=0).count()
        positive_count = data.filter(sentiment__gt=0).count()
        neutral_count = data.filter(sentiment=0).count()
        data_response = data.values("sentiment", "text")
        response.append({
            "positive_count": positive_count,
            "neutral_count": neutral_count,
            "negative_count": negative_count,
            "entity_label": row[1],
            "data": list(data_response)
        })

    return JsonResponse(response, safe=False)


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def topics_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)

    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()
    response_data = {'aspects': {}}
    with connection.cursor() as cursor:

        cursor.execute("""
            select da."label" ,da.topic, count(*) from data_aspect da inner
            join data_data dd on dd.id = da.data_id where dd.project_id = %s
            group by (da.topic, da."label") order by  da."label" ,count(*)
            desc;""", [project_id])
        rows = cursor.fetchall()
    for row in rows:
        if row[0] not in response_data['aspects']:
            response_data['aspects'][row[0]] = {}
            response_data['aspects'][row[0]]['topics'] = list()
        else:
            aux = {'topic': row[1], 'count': row[2]}
            response_data['aspects'][row[0]]['topics'].append(aux)
    return JsonResponse(response_data, safe=False)


class AlertRuleList(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user

        context = {}
        context["projects_data"] = data_models.Project.objects.filter(users=user).values("name", "id")
        context['alerts'] = data_models.AlertRule.objects.filter(project__users=user)

        return render(request, "alertrule-list.html", context)

    @method_decorator(login_required)
    def post(self, request):
        form = AlertRuleForm(data=request.POST)
        if form.is_valid():
            form.save()
        return redirect("alerts")


@method_decorator(csrf_exempt, name='dispatch')
class AlertRule(View):

    @method_decorator(login_required)
    def delete(self, request, alert_id):
        user = request.user
        rule = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rule.count() == 0:
            return HttpResponse(status=403)

        rule.delete()
        return HttpResponse(status=200)

    @method_decorator(login_required)
    def get(self, request, alert_id):
        user = request.user

        rules = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rules.count() == 0:
            return HttpResponse(status=403)

        rule = rules.get()
        response = {
            'name': rule.name,
            'project': rule.project_id,
            'aspect': rule.aspect,
            'frequency': rule.frequency,
            'period': rule.period,
            'keywords': rule.keywords,
            'emails': rule.emails,
            'sms': rule.sms,
        }

        return JsonResponse(response, safe=False)

    @method_decorator(login_required)
    def post(self, request, alert_id):
        user = request.user

        rule = data_models.AlertRule.objects.filter(project__users=user, pk=alert_id)
        if rule.count() == 0:
            return HttpResponse(status=403)

        form = AlertRuleForm(instance=rule.get(), data=request.POST)
        if form.is_valid():
            form.save()
        return redirect("alerts")


class AspectsList(View):

    @method_decorator(login_required)
    def get(self, request):
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        user = request.user
        aspect_list = data_models.AspectModel.objects.filter(users=user).order_by("label", "id")

        context = {}
        context["aspects"] = []

        p = Paginator(aspect_list, page_size)
        page = p.page(page_number)

        for aspect in page.object_list:
            rules_list = []
            rules = data_models.AspectRule.objects.filter(aspect_model=aspect)
            for rule in rules:
                rules_list.append(rule.__dict__)
            projects = data_models.Project.objects.filter(users=user, aspect_model=aspect).values("name", "id")
            context["aspects"].append({
                "id": aspect.id,
                "label": aspect.label,
                "lang": aspect.language,
                "rules": rules_list,
                "api_key": aspect.api_key,
                "managed": aspect.managed,
                "projects": projects,
            })

        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        context["projects_data"] = projects
        context["page"] = p.get_page(page_number)
        context["paginator"] = p
        context["meta"] = {}
        context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1
        context["meta"]["page_items_to"] = page_number * 10

        apikeys = data_helpers.get_api_keys(request.user)
        if apikeys.get("apikeys"):
            req = requests.get("{0}/v4/{1}/classifications.json".format(settings.API_HOST, 
                apikeys["apikeys"][0]['key']))
            context["classifications"] = json.loads(req.text)

        context["languages"] = settings.LANGUAGES
        context["predefined_aspect_rules"] = list(data_models.PredefinedAspectRule.objects.all().values())

        return render(request, "aspect-list.html", context)

    @method_decorator(login_required)
    def post(self, request):

        aspect_label = request.POST.get("aspect-label", "")
        aspect_lang = request.POST.get("aspect-lang", "")
        rule_names = request.POST.getlist("rule-name")
        rule_definitions = request.POST.getlist("rule-definition", "")
        rule_classifications = request.POST.getlist("rule-classification", "")
        predefined_aspect_rules = request.POST.getlist("predefined-rule", "")
        api_key = request.POST.get("api-key", "")

        aspect_model = data_models.AspectModel.objects.create(
            label=aspect_label.strip(),
            language=aspect_lang,
            api_key=api_key)

        aspect_model.users.add(request.user)

        count = 0
        for rule_name in rule_names:
            aspect_definition = data_models.AspectRule(
                rule_name=rule_name,
                definition=rule_definitions[count],
                aspect_model=aspect_model,
                classifications=rule_classifications[count],
            )
            aspect_definition.save()
            count += 1

        for predefined_aspect_rule in predefined_aspect_rules:
            aspect_rule = data_models.AspectRule(
                rule_name=predefined_aspect_rule,
                aspect_model=aspect_model,
                predefined=True
            )
            aspect_rule.save()

        # Sync with the API.
        result, resp = server_api.save_aspect_model(aspect_model)
        if not result:
            messages.error(request, resp['description'])
        else:
            messages.success(request, 'New aspect model added')

        return redirect('/aspect/')


@method_decorator(csrf_exempt, name='dispatch')
class Aspect(View):

    @method_decorator(login_required)
    def delete(self, request, aspect_id):
        user = request.user
        aspect = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        if aspect.count() == 0:
            return HttpResponse(status=404)

        result, resp = server_api.delete_aspect_model(aspect.get())
        if result:
            aspect.delete()
            return HttpResponse(status=200)
        else:
            messages.error(request, resp['description'])
            return HttpResponse(status=400)

    @method_decorator(login_required)
    def get(self, request, aspect_id):
        user = request.user

        aspect = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        if aspect.count() == 0:
            return HttpResponse(status=403)
        aspect = aspect.get()
        rules = data_models.AspectRule.objects.filter(aspect_model=aspect)
        response = {}
        response["aspect_id"] = aspect.id
        response["aspect_label"] = aspect.label
        response["aspect_lang"] = aspect.language
        response["aspect_api_key"] = aspect.api_key
        response["rules"] = []
        for rule in rules:
            response["rules"].append({
                "rule_label": rule.rule_name,
                "rule_definitions": rule.definition,
                "rule_id": rule.id,
                "rule_classifications": rule.classifications,
                "predefined": rule.predefined,
            })
        return JsonResponse(response, safe=False)

    @method_decorator(login_required)
    def post(self, request, aspect_id):
        method = request.POST.get("_method", "")
        if method == "PUT":
            return self.put(request, aspect_id)
        return HttpResponse(status=400)

    @method_decorator(login_required)
    def put(self, request, aspect_id):
        user = request.user
        aspect = data_models.AspectModel.objects.filter(users=user, pk=aspect_id)
        aspect_label = request.POST.get("aspect-label", "")
        aspect_lang = request.POST.get("aspect-lang", "")
        rule_names = request.POST.getlist("rule-name")
        rule_definitions = request.POST.getlist("rule-definition")
        rule_classifications = request.POST.getlist("rule-classification", "")
        rules_id = request.POST.getlist("rule-id", "")
        predefined_rules = request.POST.getlist("predefined-rules", "")

        if aspect.count() == 0:
            return HttpResponse(status=403)

        aspect = aspect.get()
        aspect.label = aspect_label
        aspect.language = aspect_lang
        aspect.save()

        # get all no predefined rules for aspect model
        rules = data_models.AspectRule.objects.filter(aspect_model=aspect, predefined=False)

        # If request does not contain the rule id that was already defined then
        # delete it.
        for rule in rules:
            rule_name = rule.rule_name
            if rule_name not in rule_names:
                rule.delete()

        rules_len = len(rules_id)
        count = 0
        for rule_name in rule_names:
            rule_name_query = data_models.AspectRule.objects.filter(aspect_model=aspect, rule_name=rule_name)
            if rule_name_query.count() == 0:
                data_models.AspectRule.objects.create(
                    rule_name=rule_names[count],
                    definition=rule_definitions[count],
                    aspect_model=aspect,
                    classifications=rule_classifications[count])
            else:
                rule_name_object = rule_name_query.get()
                rule_name_object.definition = rule_definitions[count]
                rule_name_object.label = rule_names[count]
                rule_name_object.classifications = rule_classifications[count]
                rule_name_object.save()
            count = count + 1

        aspect_predefined_rules = data_models.AspectRule.objects.filter(aspect_model=aspect, predefined=True)
        for predefined_rule in aspect_predefined_rules:
            if predefined_rule.rule_name not in predefined_rules:
                predefined_rule.delete()
        for predefined_rule in predefined_rules:
            if data_models.AspectRule.objects.filter(aspect_model=aspect,
                                                     rule_name=predefined_rule, predefined=True).count() == 0:
                data_models.AspectRule.objects.create(
                    aspect_model=aspect,
                    rule_name=predefined_rule, predefined=True)

        result, resp = server_api.save_aspect_model(aspect)
        if result:
            messages.success(request, 'Changes to aspect model saved')
            return HttpResponse(status=200)
        else:
            messages.error(request, resp['description'])
            return HttpResponse(status=400)

class EntitiesList(View):

    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        entity_list = data_models.Entity.objects.filter(users=user).order_by("label", "id")

        context = {}

        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        p = Paginator(entity_list, page_size)
        page = p.page(page_number)

        context["entities"] = page.object_list

        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        context["projects_data"] = projects
        context["page"] = p.get_page(page_number)
        context["paginator"] = p
        context["meta"] = {}
        context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1
        context["meta"]["page_items_to"] = page_number * 10

        apikeys = data_helpers.get_api_keys(request.user)
        if apikeys.get("apikeys"):
            req = requests.get("{0}/v4/{1}/classifications.json".format(settings.API_HOST,
                apikeys["apikeys"][0]['key']))
            context["classifications"] = json.loads(req.text)

        context["languages"] = settings.LANGUAGES
        return render(request, "entity-list.html", context)

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        entity_name = request.POST.get("entity-name", "")
        entity_lang = request.POST.get("entity-lang", "")
        entity_classifications = request.POST.get("entity-classifications", "")
        entity_aliases = request.POST.get("entity-aliases", "")
        api_key = request.POST.get("api-key", "")
        
        entity_model, _ = data_models.Entity.objects.get_or_create(
            label=entity_name,
            language=entity_lang,
            api_key=api_key,
        )

        entity_model.users.add(user)

        entity_classifications = entity_classifications.split(",")
        for entity_classification in entity_classifications:
            c, _ = data_models.Classification.objects.get_or_create(label=entity_classification)
            entity_model.classifications.add(c)

        entity_model.aliases = entity_aliases
        entity_model.save()

        result, resp = server_api.add_entity_model(entity_model)
        if not result:
            # Delete the newly created instance. Probably should rollback here instead?
            entity_model.delete()
            messages.error(request, resp['description'])
        else:
            messages.success(request, 'New entity added')
        
        return redirect('/entity/')


@method_decorator(csrf_exempt, name='dispatch')
class Entity(View):

    @method_decorator(login_required)
    def delete(self, request, entity_id):
        user = request.user
        entity = data_models.Entity.objects.filter(users=user, pk=entity_id)
        if entity.count() == 0:
            return JsonResponse({'description':'Entity not found'}, status=400)

        result, resp = server_api.delete_entity_model(entity.get())
        if not result:
            return JsonResponse(resp, status=400)

        entity.delete()
        return JsonResponse({'status':'OK'}, status=200)

    @method_decorator(login_required)
    def get(self, request, entity_id):
        user = request.user

        entity = data_models.Entity.objects.filter(users=user, pk=entity_id)
        if entity.count() == 0:
            return HttpResponse(status=403)
        entity = entity.get()
        classifications = data_models.Classification.objects.filter(entity=entity)

        response = {}

        response["entity_id"] = entity.id
        response["entity_label"] = entity.label
        response["entity_lang"] = entity.language
        response["entity_api_key"] = entity.api_key
        response["entity_aliases"] = entity.aliases
        response["classifications"] = []

        for classification in classifications:
            response["classifications"].append({
                "label": classification.label,
            })

        return JsonResponse(response, safe=False)

    @method_decorator(login_required)
    def post(self, request, entity_id):
        user = request.user

        entity = data_models.Entity.objects.filter(users=user, pk=entity_id)
        if entity.count() == 0:
            return JsonResponse({'status':'Fail', 'description':'Entity not found'}, status=404)

        server_api.delete_entity_model(entity.get())
        entity.delete()
        entity_name = request.POST.get("entity-name", "")
        entity_lang = request.POST.get("entity-lang", "")
        entity_classifications = request.POST.get("entity-classifications", "")
        entity_aliases = request.POST.get("entity-aliases", "")
        api_key = request.POST.get("api-key", "")
        
        entity_model = data_models.Entity.objects.create(
            label=entity_name,
            language=entity_lang,
            api_key=api_key)

        entity_model.users.add(user)

        entity_classifications = entity_classifications.split(",")
        for entity_classification in entity_classifications:
            c, _ = data_models.Classification.objects.get_or_create(label=entity_classification)
            entity_model.classifications.add(c)

        entity_model.aliases = entity_aliases
        entity_model.save()

        result, resp = server_api.add_entity_model(entity_model)
        if not result:
            messages.error(request, resp['description'])
        else:
            messages.success(request, 'Changes to entity saved')

        return redirect("entities")


class SentimentList(View):

    @method_decorator(login_required)
    def get(self, request):
        
        page_number = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))
        user = request.user
        sentiment_list = data_models.Sentiment.objects.filter(users=user).order_by('-id')
        context = {}
        context['sentiments'] = []
        p = Paginator(sentiment_list, page_size)
        page = p.page(page_number)
        for sentiment in page.object_list:
            context['sentiments'].append({
                "label": sentiment.label,
                "text": sentiment.definition,
                "language": sentiment.language,
                "sentiment": sentiment.sentiment,
                "rule_id": sentiment.rule_id,
                "api_key": sentiment.api_key,
                "id": sentiment.id,
            })

        p = Paginator(sentiment_list, page_size)
        projects = list(data_models.Project.objects.filter(users=user).values("name", "id"))
        context["projects_data"] = projects
        context["page"] = p.get_page(page_number)
        context["paginator"] = p
        context["meta"] = {}
        context["meta"]["page_items_from"] = (page_number - 1) * 10 + 1
        context["meta"]["page_items_to"] = page_number * 10
        context["languages"] = settings.LANGUAGES
        
        return render(request, "sentiment-list.html", context)

    @method_decorator(login_required)
    def post(self, request):
        user = request.user

        sentiment_label = request.POST.get("sentiment-label")
        text_definition = request.POST.get("sentiment-definition")
        sentiment = request.POST.get("sentiment")
        sentiment_language = request.POST.get("sentiment-language")
        api_key = request.POST.get("api-key")

        if sentiment == "positive":
            sentiment_value = "pos"
        elif sentiment == "negative":
            sentiment_value = "neg"
        elif sentiment == "neutral":
            sentiment_value = "neu"

        data = {
            "text": text_definition,
            "sentiment": sentiment_value,
            "lang": sentiment_language
        }
    
        result, resp = server_api.add_sentiment_rule(api_key, data)
        if not result:
            return JsonResponse(resp, status=400)

        s = data_models.Sentiment.objects.create(
            label=sentiment_label,
            definition=text_definition,
            sentiment=sentiment,
            language=sentiment_language,
            rule_id=resp["rule_id"],
            api_key=api_key,
        )
        s.users.add(user)

        messages.success(request, "New sentiment rule added")

        return JsonResponse(resp, status=200)


@method_decorator(csrf_exempt, name='dispatch')
class Sentiment(View):
    @method_decorator(login_required)
    def delete(self, request, sentiment_id):
        user = request.user

        sentiment = get_object_or_404(data_models.Sentiment, pk=sentiment_id, users=user)
        result, resp = server_api.delete_sentiment_rule(sentiment)
        if not result:
            return JsonResponse(resp, status=400)
        
        sentiment.delete()
        return JsonResponse(resp)

    @method_decorator(login_required)
    def post(self, request, sentiment_id):
        """
        We're editing a rule. We don't actually support editing a rule so what
        we do is delete the old version and re-create a new one.
        """
        user = request.user
        sentiment_label = request.POST.get("sentiment-label", "")
        text_definition = request.POST.get("sentiment-definition", "")
        sentiment_value = request.POST.get("sentiment", "")
        sentiment_language = request.POST.get("sentiment-language", "")
        
        sentiment = get_object_or_404(data_models.Sentiment, pk=sentiment_id, users=user)
        api_key = sentiment.api_key
        
        result, resp = server_api.delete_sentiment_rule(sentiment)
        if not result:
            return JsonResponse(resp, status=400)

        sentiment.delete()

        data = {
            "text": text_definition,
            "sentiment": sentiment_value,
            "lang": sentiment_language
        }

        result, resp = server_api.add_sentiment_rule(api_key, data)
        if not result:
            return JsonResponse(resp, status=400)
        
        s = data_models.Sentiment.objects.create(
            label=sentiment_label,
            definition=text_definition,
            sentiment=sentiment_value,
            language=sentiment_language,
            rule_id=resp["rule_id"],
            api_key=api_key,
        )
        s.users.add(request.user)

        messages.success(request, "Changes to sentiment rule saved")
        
        return JsonResponse(resp)

def support(request):
    """
    Accepts support requests and forwards them to zendesk.
    """
    projects = data_models.Project.objects.filter(users=request.user).values("name", "id")
    html_template = loader.get_template('support.html')
    context = {'projects_data': projects}

    if request.method == 'POST':
        # Create zendesk ticket.
        # Package the data in a dictionary matching the expected JSONdata = 
        ticket = {'ticket': {
            'subject': 'New ticket from {}'.format(request.user.username),
            'comment': {'body': request.POST['question']}
        }
        }
        url = 'https://repustatehelp.zendesk.com/api/v2/tickets.json'
        user = settings.ZENDESK_USER
        pwd = settings.ZENDESK_PASSWORD
        headers = {'content-type': 'application/json'}

        response = requests.post(
            url,
            data=json.dumps(ticket),
            auth=(user, pwd),
            headers=headers,
        )

        if response.status != 201:
            mail_admins(
                'Zendesk ticket not issued',
                'There was an error in creating a zendesk ticket: User: {}\n\n Issue:{}\n\nResponse: {}'.format(
                    request.user, request.POST['question'], response.content),
            )

        context['success'] = True

    return HttpResponse(html_template.render(context, request))


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def save_users(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        # This user does not have permission to view this project.
        return HttpResponseForbidden()

    # Remove all users then add back the new values.
    this_project.users.clear()
    this_project.users.add(request.user)
    emails = request.POST.getlist('users')
    for email in emails:
        # We use get_or_create here because the User might not exist in this
        # database yet, only in the website's database. So we lazily add it.
        u, _ = User.objects.get_or_create(username__iexact=email)
        this_project.users.add(u)

    return redirect("project", this_project.id)
