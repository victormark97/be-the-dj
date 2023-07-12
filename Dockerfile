# Dockerfile
# pull the official base image
FROM python:3.10.10

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SUPERUSER_EMAIL admin@example.com
ENV DJANGO_SUPERUSER_PASSWORD test123
ENV DJANGO_SUPERUSER_EMAIL admin@example.com

# install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project
COPY . /code/.

# collect static files
# RUN python manage.py collectstatic --noinput

# add and run as non-root user
RUN adduser --disabled-password --gecos '' myuser
USER myuser

WORKDIR /code

# run gunicorn
CMD gunicorn your_project.wsgi:application --bind 0.0.0.0:$PORT