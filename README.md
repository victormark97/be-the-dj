# Django Application

This is a Django application that has been dockerized for easy setup and deployment.

## Requirements

 - Docker
 - Docker Compose

## Setup

Clone the repository:

```bash
git clone https://github.com/victormark97/be-the-dj.git
cd be-the-dj
```

## Docker Compose

This project uses Docker Compose to manage Docker containers.

To start the application, navigate to the directory that contains the docker-compose.yml file and run the following command:

```bash
docker-compose up --build -d
```

After running this command, you should be able to see your application by navigating to http://localhost:8000 in a web browser. If you've changed the port in your Docker Compose configuration, replace 8000 with the port you've chosen.

## Create a Django superuser
A new superuser will automatically be created if none exists. Credentials:
 - admin
 - test123

License
This project is licensed under the terms of the MIT license.