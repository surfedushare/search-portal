#################################################
# BUILD FRONTEND
#################################################

FROM node:12.13 AS builder

# Create the app environment
RUN mkdir -p /usr/src/portal
WORKDIR /usr/src/portal

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
RUN groupadd -r app -g 1001 && useradd app -u 1001 -r -m -g app
# Give access to app user
RUN chown app:app /usr/src/portal
# Become app user to prevent attacks during install (possibly from hijacked npm packages)
USER app:app

COPY --chown=app portal /usr/src/portal

RUN npm install && npm run build


#################################################
# SERVICE
#################################################

FROM python:3.6-stretch

RUN apt-get update && apt-get install -y less vim build-essential gettext

# Create the app environment
RUN mkdir -p /usr/src/app
RUN mkdir -p /usr/src/static
RUN mkdir -p /usr/src/media
RUN mkdir -p /usr/src/environments
RUN mkdir -p /usr/local/aws-cli
WORKDIR /usr/src/app

# Adding an app user to prevent container access as root
# Most options speak for itself.
# The -r options make it a system user and group.
# The -m option forces a home folder (which Python tools rely upon rather heavily)
# We also add default Python user path to PATH so installed binaries get found
RUN groupadd -r app -g 1001 && useradd app -u 1001 -r -m -g app
ENV PATH="/home/app/.local/bin:${PATH}"
# Give access to app user
RUN chown app:app /usr/src/app
RUN chown app:app /usr/src/static
RUN chown app:app /usr/src/media
RUN chown app:app /usr/src/environments
RUN chown app:app /usr/local/aws-cli
# Become app user to prevent attacks during install (possibly from hijacked PyPi packages)
USER app:app

# install AWS CLI version 2
RUN curl https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip -o awscliv2.zip \
&& unzip awscliv2.zip \
&& aws/install \
&& rm awscliv2.zip

# Python dependencies
COPY service/requirements.txt /usr/src/app/
RUN pip install -U --no-cache-dir --user --quiet pip && pip install --no-cache-dir --user uwsgi==2.0.18
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application and frontend build
COPY service /usr/src/app
COPY --from=builder /usr/src/portal/dist /usr/src/app/surf/apps/materials/static/portal
COPY --from=builder /usr/src/portal/dist/index.html /usr/src/app/surf/apps/materials/templates/portal/
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

# The default command is to start a uWSGI server
CMD ["uwsgi", "--ini", "/usr/src/app/uwsgi.ini"]

# EXPOSE port 8080 to allow communication to/from server
EXPOSE 8080
