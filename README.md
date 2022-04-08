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
