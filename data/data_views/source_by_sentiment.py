from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def source_by_sentiment(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    where_clause = [
        'dd.source_id = ds.id ',
        'dd.project_id = %s',
    ]
    response = []
    limit = request.GET.get("limit", "5")
    with connection.cursor() as cursor:
        cursor.execute("""select ds."label" , count(ds.id),sum(case when dd.sentiment > 0 then 1 else 0 end) as PosCount, sum(case when dd.sentiment < 0 then 1 else 0 end) as NegCount, sum(case when dd.sentiment = 0 then 1 else 0 end) as NeutCount, ds.id from data_data dd inner join data_source ds on ds.id = dd.source_id where """+ get_where_clauses(request, where_clause) + """ group by (ds.id) order by count(ds.id) desc limit %s""" , [project_id, limit])
        rows = cursor.fetchall()
    
    for row in rows:
        response.append({
            'sourceLabel':row[0],
            'count':row[1],
            'positiveCount': row[2],
            'negativeCount': row[3],
            'neutralCount': row[4],
            "sourceID": row[5]
        })
    return JsonResponse(response, safe=False)
