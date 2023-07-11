# Dockerfile
# pull the official base image
FROM python:3.10.10

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

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

# run gunicorn
CMD gunicorn your_project.wsgi:application --bind 0.0.0.0:$PORT