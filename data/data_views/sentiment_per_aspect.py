from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

import data.models as data_models
from data.helpers import get_where_clauses

@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def sentiment_per_aspect(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    limit = request.GET.get("limit", "10")

    query_args = [project_id]
    limit_clause = " limit %s"
    if limit == "all":
        limit = ""
        limit_clause = ""
    else:
        query_args.append(limit)
    
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    
    where_clause = [
        'dd.source_id = ds.id ',
        'da.data_id = dd.id',
        'dd.project_id = %s',
    ]
    
    
    response = []
    with connection.cursor() as cursor:
        cursor.execute("""select da."label", count( da."label"),sum(case when dd.sentiment > 0 then 1 else 0 end) as PosCount, sum(case when dd.sentiment < 0 then 1 else 0 end) as NegCount, sum(case when dd.sentiment = 0 then 1 else 0 end) from data_aspect da inner join data_data dd on dd.id = da.data_id  inner join data_source ds on ds.id = dd.source_id where """+ get_where_clauses(request, where_clause) + """group by (da."label") order by count(da."label") desc """ + limit_clause , query_args)
        rows = cursor.fetchall()
    
    for row in rows:
        response.append({
            'aspectLabel':row[0],
            'count':row[1],
            'positiveCount': row[2],
            'negativeCount': row[3],
            'neutralCount': row[4],
        })
    
    return JsonResponse(response, safe=False)
