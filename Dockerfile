FROM centos:7

# Install system dependencies
RUN yum install -y \
    wget \
    gcc make \
    zlib-dev openssl-devel sqlite-devel bzip2-devel

# Install Python
RUN yum install -y https://centos7.iuscommunity.org/ius-release.rpm
RUN yum install -y python36u python36u-devel python36u-pip

ENV PATH "/usr/local/bin:${PATH}"

# Install Python dependencies
RUN yum install -y gettext git cron binutils libproj-dev gdal-bin \
    && rm -rf /var/lib/apt/lists/*
RUN pip3.6 install --no-cache-dir uWSGI
COPY requirements/requirements.prod.txt /src/requirements/requirements.prod.txt
RUN pip3.6 install --no-cache-dir -r /src/requirements/requirements.prod.txt
RUN rm /usr/bin/python
RUN ln -s /usr/bin/python3.6 /usr/bin/python

# Install source
COPY . /src
WORKDIR /src
RUN python /src/manage.py collectstatic --noinput

EXPOSE 8080
CMD ["uwsgi", "--http", ":8080", "--wsgi-file", "surf/wsgi.py", "--processes", "4", "--static-map", "/static=/src/static"]
