FROM ubuntu:22.04

RUN apt-get update && apt-get install -y --no-install-recommends \
    fpc \
    build-essential \
    && useradd --create-home --uid 1000 runner \
    && mkdir -p /runner/work /tmp/home \
    && chown -R runner:runner /runner /tmp/home \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /runner

ENV HOME=/tmp/home

USER runner
CMD ["sleep", "infinity"]
