FROM python:3.7-alpine
ADD app /app

RUN apk update apk add --no-cache gcc git python3-dev musl-dev linux-headers libc-dev rsync zsh \
  && findutils wget util-linux grep libxml2-dev libxslt-dev 

RUN pip install --upgrade pip

RUN apk add --no-cache --virtual .build-deps gcc musl-dev \
  && pip install cython \
  && apk del .build-deps gcc musl-dev 

RUN adduser -D worker
USER worker
WORKDIR /home/worker
COPY --chown=worker:worker /app/requirements.txt requirements.txt
RUN pip install --no-cache-dir --user -r requirements.txt
ENV PATH="/home/worker/.local/bin:${PATH}"
COPY app/on_create_update.py /on_create_update.py
COPY app/namespace.yaml /namespace.yaml
COPY app/resourcequota.yaml /resourcequota.yaml
COPY --chown=worker:worker /app /home/worker/app
LABEL maintainer="Krzysztof Pudlwski <djkormo@gmail.com>" version="1.0.0"
CMD kopf run --liveness=http://0.0.0.0:8080/healthz --verbose --standalone /home/worker/app/on_create_update.py

