FROM python:3.7-slim
ADD app /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
COPY app/with_update.py /with_update.py
CMD kopf run --standalone /with_update.py

