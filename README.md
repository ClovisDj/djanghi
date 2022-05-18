# Djanghi
Djanghi is a project to help communities manage their membership and have a centralized place to manage payments and gatherings.
This is build with `Python`, `Django` and `Django Rest Framework`

## Installation an initialization

Prerequisite to run this project is having `docker` and docker-compose` installed on your machine and being able to run `Make` command.

To pull and build the required containers just run the following command in the root directory:

```
make build
```

To install the required packages run

```
make install-package
```

To start the local server run:

```
make runserver
```

To run migration run:

```
make migrate
```
This repository comes with some fixtures that can be loaded with:

```
make load-data
```
## Sample .env values

```dotenv
# Django
ENVIRONMENT=local
SECRET_KEY=dummpy-secret-key
DEBUG=True
DJANGO_LOG_LEVEL=DEBUG
ALLOWED_HOSTS=localhost,0.0.0.0
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
API_HOST=http://localhost:8000
FRONT_END_HOST=http://localhost:3000
# Postgres
POSTGRES_USER=psql-user
POSTGRES_PASSWORD=password
POSTGRES_HOST=psql
POSTGRES_DB=djanghi-db
DB_PORT=5432
# Simple jwt & drf
ACCESS_TOKEN_LIFETIME=5
REFRESH_TOKEN_LIFETIME=360
JWT_SECRET_KEY=super-secret-key!
AUTH_HEADER_TYPES=JWT
PAGE_SIZE=15
# Anymail
SENDGRID_API_KEY=hahahaahahhaha
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```