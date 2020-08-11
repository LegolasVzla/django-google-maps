VENV_NAME?=env
HOST=127.0.0.1
DPORT=8000

help:
	@echo "make execute"
	@echo "	Run server."
	@echo "make setup"
	@echo "	Install packages and some default things needed in your system."
	@echo "make install"
	@echo "	By setting previously a virtual env, generate db with default data and install python requirements."

execute:
	python manage.py runserver ${HOST}:${DPORT}

setup:
	# Install PostgreSQL
	sudo apt-get update
	sudo apt install python3-dev postgresql postgresql-contrib python3-psycopg2 libpq-dev -y
	# Install PostGIS
	sudo apt-get install -y postgis postgresql-10-postgis-2.4 python-psycopg2
	sudo -u postgres psql -c "CREATE EXTENSION postgis;"
	# Generate log folder 
	mkdir logs
	# Generate config file for environment variables
	touch settings.ini
	# install pip
	sudo apt-get install python-pip python-dev build-essential -y
	sudo pip install --upgrade pip
	# install virtualenv
	sudo apt-get install python-virtualenv virtualenv -y
	pip install --upgrade virtualenv
	#apt --fix-broken install
	virtualenv $(VENV_NAME) --python=python3

install:
	pip install -r requirements.txt
	sudo apt-get install python3-tk
	python manage.py makemigrations
	python manage.py migrate
	# load default system data
	python manage.py insert_fixtures
