from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from data.helpers import get_where_clauses
import data.models as data_models


@login_required(login_url=settings.LOGIN_REDIRECT_URL)
def entity_by_sentiment(request, project_id):
    this_project = get_object_or_404(data_models.Project, pk=project_id)
    if this_project.users.filter(pk=request.user.id).count() == 0:
        raise PermissionDenied
    where_clause = [
        'dd.project_id = %s',
    ]
    response = []
    limit = request.GET.get("limit", "5")
    with connection.cursor() as cursor:
        cursor.execute("""select de."label" , sum(case when dd.sentiment > 0 then 1 else 0 end) as PosCount, sum(case when dd.sentiment < 0 then 1 else 0 end) as NegCount, sum(case when dd.sentiment = 0 then 1 else 0 end) as NeutCount, de.id, count(de.id) from data_data dd inner join data_data_entities dde on dde.data_id = dd.id inner join data_entity de on de.id = dde.entity_id inner join data_source ds on ds.id = dd.source_id where """ + get_where_clauses(request, where_clause) + """ group by (de.id ) order by count(de.id) desc limit %s; """, [project_id, limit])
        rows = cursor.fetchall()
    
    for row in rows:
        response.append({
            'entityLabel':row[0],
            'positiveCount': row[1],
            'negativeCount': row[2],
            'neutralCount': row[3],
            "entityID": row[4]
        })
    return JsonResponse(response, safe=False)
