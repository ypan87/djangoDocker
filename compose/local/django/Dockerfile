FROM python:3.7

ENV PYTHONUNBUFFERED 1

WORKDIR /turboselection

COPY ./requirements.txt ./

COPY ./compose/local/django/start.sh /

RUN chmod +x /start.sh && pip install -r ./requirements.txt