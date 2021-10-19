ARG ALPINE_VERSION=3.14

FROM docker-remote.artifactory.corp.plusnet/python:3.7-alpine${ALPINE_VERSION}

ENV https_proxy=http://artivm1.plusnet:3128
ENV http_proxy=http://artivm1.plusnet:3128

RUN apk --no-cache add  gcc musl-dev curl bash

RUN pip install --upgrade pip

ADD app /app
RUN addgroup -S worker && adduser -D -h /home/worker -s /bin/bash worker -G worker

USER worker

WORKDIR /home/worker

COPY --chown=worker:worker /app/requirements.txt requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt


ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker /app /home/worker/app

RUN chmod u+x /home/worker/app/operator.bash

LABEL maintainer="Krzysztof Pudlowski <kpudlowski@plus.pl>" version="0.1.0"

ENV http_proxy ""
ENV https_proxy ""

#CMD kopf run --liveness=http://0.0.0.0:8080/healthz --standalone  /home/worker/app/kopf_operator.py

ENTRYPOINT ["/bin/bash", "-c", "/home/worker/app/operator.bash"]

