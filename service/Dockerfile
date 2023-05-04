#################################################
# BUILD FRONTEND
#################################################

FROM node:16.14.2 AS builder

# Create the app environment
RUN mkdir -p /usr/src/portal
RUN mkdir -p /usr/src/service
WORKDIR /usr/src/portal

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
RUN groupadd -r app -g 1001 && useradd app -u 1001 -r -m -g app
# Give access to app user
RUN chown -R app:app /usr/src
# Become app user to prevent attacks during install (possibly from hijacked npm packages)
USER app:app

COPY --chown=app portal/package.json /usr/src/portal/package.json
COPY --chown=app portal/package-lock.json /usr/src/portal/package-lock.json
RUN npm ci --no-optional

COPY --chown=app portal /usr/src/portal
RUN npm run build

#################################################
# SERVICE
#################################################

FROM python:3.10-slim

RUN apt-get update && apt-get install -y less vim build-essential gettext git

# Create the app environment
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/static
RUN mkdir -p /usr/src/media
RUN mkdir -p /usr/src/environments
WORKDIR /usr/src/app

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
# We also add default Python user path to PATH so installed binaries get found
RUN groupadd -r app -g 1000 && useradd app -u 1000 -r -m -g app
ENV PATH="/home/app/.local/bin:${PATH}"
ENV PYTHONPATH="/usr/src/app"
# Give access to app user
RUN chown app:app /usr/src/app
RUN chown app:app /usr/src/static
RUN chown app:app /usr/src/media
RUN chown app:app /usr/src/environments
# Become app user to prevent attacks during install (possibly from hijacked PyPi packages)
USER app:app

# Python dependencies
COPY service/requirements.txt /usr/src/app/
COPY service/dependencies.txt /usr/src/app/
RUN pip install -U --no-cache-dir --user pip
RUN pip install wheel
RUN pip install --no-cache-dir --user uwsgi==2.0.21
RUN pip install --no-cache-dir --user -r requirements.txt
RUN pip install --no-cache-dir --user git+https://github.com/surfedushare/search-client.git@v0.3.0

# Copy application and frontend build
COPY --chown=app service /usr/src/app
COPY --from=builder /usr/src/service/surf /usr/src/app/surf
# Copy environment configurations
# The default environment mode is production, but during image build we use the localhost mode
# This allows to run setup commands locally without loading secrets
COPY environments /usr/src/environments

# We're serving static files through Whitenoise
# See: http://whitenoise.evans.io/en/stable/index.html#
# If you doubt this decision then read the "infrequently asked question" section for details
# Here we gather static files that get served through uWSGI if they don't exist
RUN export APPLICATION_MODE=localhost && python manage.py collectstatic --noinput

# There are some translations of Django packages that we want to use
RUN export APPLICATION_MODE=localhost && python manage.py compilemessages

# Entrypoint sets sites-enabled correctly
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi/emperor.ini"]

# EXPOSE ports to allow communication to/from server
EXPOSE 8080 8000 8001
