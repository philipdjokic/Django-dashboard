FROM ubuntu
RUN apt update
ENV TZ=Europe/Lisbon
ENV DEBIAN_FRONTEND=noninteractive
RUN  apt install python3 python3-pip nginx postgresql postgresql-contrib libpq-dev -y
WORKDIR /myfolder
COPY ./requirements.txt /myfolder
RUN python3 -m pip install -r requirements.txt
COPY ./docker/script.sh /myfolder
COPY ./dashboard /var/www/dashboard
COPY ./manage.py /var/www/manage.py
COPY ./data /var/www/data
COPY ./customize /var/www/customize
COPY ./authentication /var/www/authentication
COPY ./docker/nginx.conf /etc/nginx/nginx.conf
WORKDIR /var/www/
CMD ["bash", "/myfolder/script.sh"]