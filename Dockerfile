FROM python:3.6

ENV FLASK_APP run.py

COPY manage.py gunicorn-cfg.py requirements.txt .env ./
COPY data data
COPY authentication authentication
COPY dashboard dashboard

RUN pip install -r requirements.txt

CMD python manage.py makemigrations
CMD command python manage.py migrate

EXPOSE 5005
CMD ["gunicorn", "--config", "gunicorn-cfg.py", "dashboard.wsgi"]
ENV DOCKER YES