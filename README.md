# django-google-maps
Basic example of how to use google maps with django

## Installation

Clone this project:

	git clone https://github.com/LegolasVzla/django-google-maps.git

Create your virtualenv and install the requirements:

	virtualenv env --python=python3
	source env/bin/activate

	pip install -r requirements.txt

Create logs folder:

	mkdir logs

Create a **settings.ini** file, with the structure as below:

	[postgresdbConf]
	DB_ENGINE=django.db.backends.postgresql
	DB_NAME=dbname
	DB_USER=user
	DB_PASS=password
	DB_HOST=host
	DB_PORT=port

	[googleMapsConf]
 	API_KEY=yourGoogleAPIKey

By default, DB_HOST and DB_PORT in PostgreSQL are localhost/5432.

Run the migrations:

	python manage.py makemigrations

	python manage.py migrate

Run the server:

	python manage.py runserver

You could see the home page in:

	http://127.0.0.1:8000/

## Contributions
------------------------

I started this project from [yt-google-maps-1](https://github.com/Klerith/yt-google-maps-1) repository.

All work to improve performance is good

Enjoy it!
