import csv
import os
import psycopg2
from urllib.parse import urlparse

from data.models import *

dsn = open(os.environ['PIPELINE_CONFIG']).read()
conn = psycopg2.connect(dsn)
cache = {}

traffic_stats = {}

def load_traffic_stats():
    with open('scripts/traffic_stats.csv') as fd:
        r = csv.reader(fd)
        for row in r:
            url, t = row[1], row[2]
            if t == 'N/A':
                continue
            domain = urlparse(url).netloc
            traffic_stats[domain] = t
    
def web_traffic(url):
    domain = urlparse(url).netloc
    return traffic_stats.get(domain, 0)

def to_english(label, lang):
    # First make sure all of our english titles are in the interlanguage links table.
    if lang == 'en':
        return label

    key = '{}-{}'.format(label, lang)
    val = cache.get(key)
    if val:
        return val

    with conn.cursor() as cur:
        query = "SELECT englishpagetitle FROM interlanguagelinks_en WHERE pagetitle = %s and languagecode = %s"
        cur.execute(query, (label.replace(' ', '_'), lang))
        try:
            val = cur.fetchall()[0][0]
        except:
            return label

        cache[key] = val
        return val

def xrun():
    with open('entity_export.csv', 'w') as entity_out:
        w3 = csv.writer(entity_out)
        w3.writerow(['data_id', 'entity', 'english', 'classifications'])

        for d in Data.objects.filter(project__id=3155):
            for e in d.entities.prefetch_related('classifications'):
                w3.writerow([
                    d.id, 
                    e.label, 
                    to_english(e.label, d.language), 
                    ','.join(e.classifications.values_list('label', flat=True))
                ])


def run():
    
    load_traffic_stats()

    with open('data_export.csv', 'w', encoding='utf-8') as data_out:
        w = csv.writer(data_out)
        w.writerow(['id', 'date_created', 'text', 'url', 'language', 
            'country', 'source', 'raw sentiment', 'weighted_sentiment', 'relevance', 'web traffic'])
        
        with open('aspect_export.csv', 'w', encoding='utf-8') as aspect_out:
            w2 = csv.writer(aspect_out)
            w2.writerow(['data_id', 'label', 'sentiment', 'chunk', 'topic', 'sentiment text'])
            
            with open('entity_export.csv', 'w', encoding='utf-8') as entity_out:
                w3 = csv.writer(entity_out)
                w3.writerow(['data_id', 'entity', 'english', 'classifications'])

                for d in Data.objects.filter(project__id=3155, date_created__gt='2021-04-07').prefetch_related('entities'):
                    
                    w.writerow([
                        d.id, 
                        d.date_created, 
                        d.text,
                        d.url,
                        d.language,
                        d.country and d.country.label or '', 
                        d.source.label, 
                        d.sentiment, 
                        d.weighted_score,
                        d.relevance,
                        web_traffic(d.url)])
                    
                    for a in d.aspect_set.values():
                        if a['sentiment_text']:
                            st = a['sentiment_text'][0]
                        else:
                            st = ''
                        w2.writerow([d.id, a['label'], a['sentiment'], a['chunk'], a['topic'], st])
                    
                    for e in d.entities.all():
                        w3.writerow([
                            d.id, 
                            e.label, 
                            to_english(e.label, d.language), 
                            ','.join(e.classifications.values_list('label', flat=True))
                        ])

