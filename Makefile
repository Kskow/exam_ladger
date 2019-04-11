build:
	sudo docker-compose build --no-cache web
up:
	sudo docker-compose up web
bash:
	sudo docker-compose run web bash
flake8:
	sudo docker-compose run --rm web flake8 .
migrate:
	sudo docker-compose run web python manage.py makemigrations && sudo docker-compose run web python manage.py migrate
test:
	sudo docker-compose run web python manage.py test webapps.exam_sheets.tests.test_task
shell:
	sudo docker-compose run web python manage.py shell
start:
	sudo docker-compose build web && sudo docker-compose run web python manage.py makemigrations \
	&& sudo docker-compose run web python manage.py migrate && sudo docker-compose up web