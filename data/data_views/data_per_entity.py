import csv
import math

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses, get_order_by
from data.serialize import serialize_rows

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def data_per_entity(request, project_id):
    project = get_object_or_404(data_models.Project, pk=project_id)
    if project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    
    entity_id = int(request.GET.get("entityID", ""))
    where_clause = [
        "dd.project_id = %s",
        "de.id = %s"
    ]

    sentiment = request.GET.get("sentiment", "")

    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")

    with connection.cursor() as cursor:
        cursor.execute("""
            select count(*) from data_data dd inner join data_source ds on ds.id = dd.source_id inner join data_data_entities dde on dde.data_id = dd.id inner join data_entity de on de.id = dde.entity_id where """ + get_where_clauses(request, where_clause), [project_id, entity_id])
        row = cursor.fetchone()
    total_data = int(row[0])

    where_clause = [
        "dd.project_id = %s",
        "de.id = %s"
    ]
    sentiment = request.GET.get("sentiment", "")

    if sentiment == "positive":
        where_clause.append("dd.sentiment > 0")
    if sentiment == "negative":
        where_clause.append("dd.sentiment < 0")
    if sentiment == "neutral":
        where_clause.append("dd.sentiment = 0")
    
    response_format = request.GET.get("format", "")
    query_args = [
        project_id,
        entity_id
    ]

    if response_format == "word-cloud":
        with connection.cursor() as cursor:
            cursor.execute("""
                with counts as ( SELECT keyword, ct::int from data_data dd CROSS JOIN LATERAL jsonb_each_text(keywords) AS k(keyword, ct) inner join data_source ds on dd.source_id = ds.id inner join data_data_entities dde on dde.data_id = dd.id inner join data_entity de on de.id = dde.entity_id where """ + get_where_clauses(request, where_clause) + """order by date_created desc ) SELECT keyword, SUM(ct)::INT keyword_count FROM counts GROUP BY keyword ORDER BY keyword_count desc limit 50""", query_args)
            rows = cursor.fetchall()
            response = []
            for row in rows:
                response.append({
                    'keyword':row[0],
                    'keywordCount':row[1],
                })
            return JsonResponse(response, safe=False)
    
    sql_query = """
        select dd.date_created, dd."text" , dd."url", ds."label"  , dd.sentiment , dd."language", dd.id
        from data_data dd inner join data_source ds on dd.source_id = ds.id inner join data_data_entities dde on dde.data_id = dd.id inner join data_entity de on de.id = dde.entity_id where """ + get_where_clauses(request, where_clause) + get_order_by(request, "dd.date_created", "desc") 
    
    return serialize_rows(
        request,
        project_id,
        total_data,
        sql_query,
        where_clause,
        query_args,
        response_format,
        "data_items_per_entity.csv",
    )
