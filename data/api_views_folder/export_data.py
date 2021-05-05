from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from data.helpers import getWhereClauses
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
import data.models as data_models
from urllib import parse
from data.helpers import getWhereClauses, getFiltersSQL
import math
import csv
LOGIN_URL = '/login/'

@login_required(login_url=LOGIN_URL)
def export_data(request):
    project_id = request.GET.get("project-id")
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    languages = request.GET.getlist("languages[]")
    sources = request.GET.getlist("sources[]")
    where_clauses = ['dd.project_id=%s'%(project_id)]
    if date_from:
        where_clauses.append("dd.date_created > '%s'"%(date_from))
    if date_to:
        where_clauses.append("dd.date_created < '%s'"%(date_to))
    where_clauses.append("dd.language in ('%s')"%("','".join(languages)))
    where_clauses.append("ds.id in ('%s')"%("','".join(sources)))
    with connection.cursor() as cursor:
        cursor.execute("""
            select dd.date_created, dd."text" , ds."label" , dd.weighted_score , dd.sentiment , dd."language" from data_data dd inner join data_source ds on dd.source_id = ds.id where """ + " and ".join(where_clauses) + """ order by dd.date_created desc""")
        rows = cursor.fetchall()
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_items.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', "Text", "Source", "Weighted", "Raw", "Language"])
    for row in rows:
        writer.writerow([row[0], row[1], row[2], row[3], row[4], row[5]])
    return response