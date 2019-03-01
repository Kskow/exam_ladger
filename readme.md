EXAM_LADGER PROJECT

Project created on Linux Ubuntu 18.04,
To run project you have to install Docker Compose
**sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o 
/usr/local/bin/docker-compose**

Than run project using single command -> _**make start**_

Project will run with clean db, so you have to create users.

To create user you have to run command **make shell**
It will open django shell, than you have to type:

**from webapps.exam_sheets.models import UserProfile
user1 = UserProfile.objects.create_user(username="", password="", email="", is_examinator=True)
user2 = UserProfile.objects.create_user(username="", password="", email="", is_examinator=False)
user1.save()
user2.save()**

**Login url is 'api/login/'**

To run tests type **make test**