FROM python:3.7-alpine

RUN apk --no-cache add gcc musl-dev curl bash

RUN pip install --upgrade pip

ADD app /app

RUN adduser -D -h /home/worker -s /bin/bash -G users worker

USER worker

WORKDIR /home/worker

COPY --chown=worker:worker /app/requirements.txt requirements.txt

RUN pip install --no-cache-dir --user -r requirements.txt

ENV PATH="/home/worker/.local/bin:${PATH}"

COPY --chown=worker:worker /app /home/worker/app

RUN chmod u+x /home/worker/app/operator.bash

LABEL maintainer="Krzysztof Pudlowski <djkormo@gmail.com>" version="1.0.0"

CMD kopf run --liveness=http://0.0.0.0:8080/healthz --standalone --verbose /home/worker/app/operator.py

#ENTRYPOINT ["/home/worker/app/operator.bash"]
