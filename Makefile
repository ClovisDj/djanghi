
user-shell := docker-compose run --rm -e LOCAL_USER_ID=`id -u $$USER` -e LOCAL_GROUP_ID=`id -g $$USER` \
	--entrypoint /entrypoint.sh django-shell

build:
	docker-compose build "$(S)"

poetry:
	$(user-shell) sh -c "virtualenv .virtualenv && source .virtualenv/bin/activate && poetry $(O)"

poetry-lock:
		$(user-shell) sh -c "virtualenv .virtualenv && source .virtualenv/bin/activate && poetry lock"

poetry-install:
	$(user-shell) sh -c "virtualenv .virtualenv && source .virtualenv/bin/activate && poetry install"

install-package:
	# Ex make install-package O=remove P=celery
	# make install-package O=add P=gdal=~3.4
	$(user-shell) sh -c "poetry $(O) $(P)"

shell:
	$(user-shell) sh -c "./manage.py shell"

runserver:
	docker-compose up --force-recreate psql djanghi-server

bash:
	$(user-shell) bash

migrations:
	$(user-shell) sh -c "./manage.py makemigrations"

migrate:
	$(user-shell) sh -c "./manage.py migrate"