FROM python:3.6
RUN apt-get update \
    && apt-get install -y gettext git cron binutils libproj-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir uWSGI
COPY . /src
COPY entrypoint.sh /
WORKDIR /src
RUN pip install --no-cache-dir -r /src/requirements/requirements.prod.txt
EXPOSE 8080
ENTRYPOINT [ "/entrypoint.sh" ]
CMD ["uwsgi", "--http", ":8080", "--wsgi-file", "surf/wsgi.py", "--processes", "4", "--static-map", "/static=/src/static"]
