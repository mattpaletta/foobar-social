FROM python:3.7
ADD requirements.txt /requirements.txt
RUN pip3 install -r requirements.txt

FROM postgres:9.3
ENV POSTGRES_USER docker
ENV POSTGRES_PASSWORD docker
ENV POSTGRES_DB docker
ADD CreateDB.sql /docker-entrypoint-initdb.d/

# Add the other things
WORKDIR auth
ADD . /.
ENTRYPOINT ["python3", "__main__.py"]