FROM python:3.7-slim
ADD app /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app/on_create.py /on_create.py
CMD kopf run --standalone /on_create.py

