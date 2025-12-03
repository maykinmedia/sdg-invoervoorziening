# This is a multi-stage build file, which means a stage is used to build
# the backend (dependencies), the frontend stack and a final production
# stage re-using assets from the build stages. This keeps the final production
# image minimal in size.

# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment
FROM python:3.10-slim-bookworm AS backend-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        libpq-dev \
        build-essential \
        python3-dev \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/src

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Ensure we use the latest version of pip
RUN pip install pip setuptools -U
COPY ./requirements /app/requirements
RUN pip install -r requirements/production.txt


# Stage 2 - Install frontend deps and build assets
FROM node:20-bookworm-slim AS frontend-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# setup for rijkshuisstijl
COPY ./bin/collect.sh /app/bin/collect.sh
COPY --from=backend-build /opt/venv/ /app/venv/
ENV VIRTUAL_ENV=/app/venv

# copy configuration/build files
COPY ./build /app/build/
COPY ./*.json ./*.js ./.babelrc /app/

# prevent caching stage 2 (if there are changes)
COPY src/sdg/scss/ /app/src/sdg/scss/
COPY src/sdg/js/ /app/src/sdg/js/

# install WITH dev tooling
RUN npm ci

# copy source code
COPY ./src /app/src

# build frontend
RUN npm run build


# Stage 3 - Build docker image suitable for production
FROM python:3.10-slim-bookworm

# Stage 3.1 - Set up the needed production dependencies
# install all the dependencies for GeoDjango
RUN apt-get update && apt-get install -y --no-install-recommends \
        procps \
        vim \
        mime-support \
        postgresql-client \
        libxml2 \
        libxmlsec1 \
        libxmlsec1-openssl \
        libexpat1 \
        gettext \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./bin/docker_start.sh /start.sh
COPY ./bin/celery_worker.sh /celery_worker.sh
COPY ./bin/celery_beat.sh /celery_beat.sh
RUN mkdir /app/log
RUN mkdir /app/media

# copy backend build deps
COPY --from=backend-build /opt/venv/lib/python3.10 /usr/local/lib/python3.10
COPY --from=backend-build /opt/venv/bin/uwsgi /usr/local/bin/uwsgi
COPY --from=backend-build /app/src/ /app/src/

# copy frontend build statics
COPY --from=frontend-build /app/src/sdg/static /app/src/sdg/static
COPY --from=frontend-build /app/node_modules/flag-icon-css/ /app/node_modules/flag-icon-css/

# copy source code
COPY ./src /app/src

RUN useradd -M -u 1000 maykin
RUN chown -R maykin /app

# drop privileges
USER maykin

ARG COMMIT_HASH
ARG RELEASE
ENV GIT_SHA=${COMMIT_HASH}
ENV RELEASE=${RELEASE}
ENV DJANGO_SETTINGS_MODULE=sdg.conf.docker

ARG SECRET_KEY=dummy

# Run collectstatic, so the result is already included in the image
RUN python src/manage.py collectstatic --noinput
RUN python src/manage.py compilemessages

LABEL org.label-schema.vcs-ref=$COMMIT_HASH \
      org.label-schema.vcs-url="https://github.com/maykinmedia/sdg-invoervoorziening" \
      org.label-schema.version=$RELEASE \
      org.label-schema.name="Single Digital Gateway Invoervoorziening"

EXPOSE 8000
CMD ["/start.sh"]
