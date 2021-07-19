FROM python:3.7-slim
ADD app /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app/on_create_update.py /on_create_update.py
COPY app/namespace.yaml /namespace.yaml
COPY app/resourcequota.yaml /resourcequota.yaml
CMD kopf run --liveness=http://0.0.0.0:8080/healthz --verbose --standalone /app/on_create_update.py

