run: sass server

sass:
	sass --watch rbhl/static/css/rbhl.scss:rbhl/static/css/rbhl.css

server:
	python manage.py runserver

