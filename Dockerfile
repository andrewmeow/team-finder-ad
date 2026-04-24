# syntax=docker/dockerfile:1
FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /code

RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /code/

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

CMD ["gunicorn", "team_finder.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]