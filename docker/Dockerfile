FROM python:3.12-slim AS requirements-stage

WORKDIR /tmp

RUN pip install poetry==2.1.1
RUN poetry self add poetry-plugin-export

COPY ./pyproject.toml ./poetry.lock /tmp/

RUN poetry export -f requirements.txt -o requirements.txt --without-hashes --with=dev

FROM python:3.12-slim

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install --no-install-recommends --no-install-suggests -y \
        bash \
        docker.io \
        docker-cli \
        g++ \
        fp-compiler \
        libc6-dev \
        openjdk-21-jdk-headless \
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/* \
    && command -v docker >/dev/null

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app
