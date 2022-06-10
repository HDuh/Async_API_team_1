FROM elasticsearch:7.14.0 as builder

ARG DISCOVERY_TYPE
ENV "discovery.type"=${DISCOVERY_TYPE}

ADD entrypoint.sh indexes/genres.json indexes/persons.json indexes/movies.json /

RUN chmod +x '/entrypoint.sh' \
    && /usr/local/bin/docker-entrypoint.sh elasticsearch -d -E path.data=/tmp/data \
    && while [[ "$(curl -s -o /dev/null -w '%{http_code}' localhost:9200)" != "200" ]]; do sleep 1; done \
    && /entrypoint.sh

FROM builder
COPY --from=builder /tmp/data/ /usr/share/elasticsearch/data/
