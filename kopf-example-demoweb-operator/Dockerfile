FROM python:3.7
ADD app /app
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt
#COPY app/handlers.py /handlers.py
CMD kopf run --standalone /with_update.py
