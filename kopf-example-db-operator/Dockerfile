FROM python:3.7
RUN pip install kopf
COPY app/handlers.py /handlers.py
CMD kopf run --standalone /handlers.py