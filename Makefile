build:
	sudo docker-compose build web
up:
	sudo docker-compose up web
bash:
	sudo docker-compose run web bash
flake8:
	sudo docker-compose run --rm web flake8 .
migrate:
	sudo docker-compose run web python manage.py migrate
test:
	sudo docker-compose run web python manage.py test