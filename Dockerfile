FROM python:3.10-rc-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . /app

RUN pip install -r /app/requirements/development.txt

ENTRYPOINT ./manage.py run