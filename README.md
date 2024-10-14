# Recipe Master

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/-Django-092E20?style=flat&logo=django&logoColor=white)
![Django REST framework](https://img.shields.io/badge/-Django%20REST%20framework-ff9900?style=flat&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat&logo=docker&logoColor=white)

# Russian version
*Note: The English version of this document is also available [here](https://github.com/Khryashoff/recipe_master#english-version).*

## Описание

Recipe Master — это продвинутая онлайн-платформа, где пользователи могут делиться своими уникальными рецептами, находить новые идеи и систематизировать свой кулинарный опыт. Платформа предоставляет удобные инструменты для создания, организации и публикации рецептов, а также возможность сохранять избранные блюда и формировать списки покупок.

## Запуск проекта в режиме разработки

1. Клонируйте репозиторий и перейдите в него через командную строку:
```bash
git clone git@github.com:Khryashoff/recipe_master.git
```
2. Установите и активируйте виртуальное окружение для проекта:
```bash
python -m venv venv
```
```bash
# для ОС Windows
. venv/Scripts/activate
```
3. Обновите pip и установите зависимости из файла requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
4. Выполните миграции на уровне проекта:
```bash
python manage.py migrate
```
5. Создайте суперпользователя:
```bash
python manage.py createsuperuser
```
6. Запустите проект:
```bash
python manage.py runserver
```

## Получение токена авторизации

- Перейдите по адресу http://127.0.0.1:8000/api/auth/token/login/ и передайте следующий JSON-запрос:
```
{
  "password": "<your_password>",
  "email": "<your_email>"
}
```

## Запуск проекта на сервере
1. Сделайте форк репозитория.

2. Клонируйте репозиторий и перейдите в него через командную строку:
```bash
git clone git@github.com:"<your_github_username>"/recipe_master.git
```
2. Если вы не собираетесь запускать проект локально, выполните развёртывание на сервере:
```bash
# Подключение к удалённому серверу
sch -i path_file_SSH_key/file_name_SSH_key user_name@ip_adreserver
```
```bash
# Установка docker-compose на сервере:
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
Создайте файл .env и заполните его своими данными. Список данных указан в корневом каталоге проекта в файле .env.example.
3.  Создайте Docker-образы и загрузите их на DockerHub:
```bash
# Замените 'username' на свой логин на DockerHub:
cd ../frontend
docker build -t username/foodgram_frontend .
cd ../backend
docker build -t username/foodgram_backend .
```
```bash
# Замените 'username' на свой логин на DockerHub:
docker push username/foodgram_frontend
docker push username/foodgram_backend
```
```bash
# Копирование файлов docker-compose.production.yml и .env в каталог foodgram/:
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```
4. Замените в файлах **docker-composer.yml** и **docker-composer.production.yml** все доступные ``image`` данные на свои собственные ```<your_user name>/<image name>:latest```:
5. В каталоге **foodgram** создайте папку **infra**. В каталоге foodgram/infra directory, поместите ``docker-composer.production.yml`` и ``nginx.conf``.
6. Запустите docker-compose в режиме демона:
```bash
sudo docker compose -f docker-compose.production.yml up -d
```
7. Подготовительные работы с файлами проекта:
```bash
# На сервере откройте конфигурацию Nginx в редакторе nano:
sudo nano /etc/nginx/sites-enabled/default
```
```bash
# Измените настройки location в секции server:
sudo nano /etc/nginx/sites-enabled/default
server {

	server_name <example.com>;
	
	location / {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000;
	}

	location /admin/ {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000/admin/;
	}
}
```
```bash
# Проверьте работоспособность конфигурации Nginx:
sudo nginx -t
```
```bash
# Перезапустите Nginx:
sudo service nginx reload
```
```bash
# Выполните миграции, соберите статические файлы бекенда и скопируйте их в /backend_static/static/:
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
docker compose -f docker-compose.production.yml exec backend python manage.py ingrs_loader 
```
8. Адаптируйте файл под себя, настроив секреты с использованием GitHub Actions:

```
SECRET_KEY                     # Секретный ключ Django-проекта
DEBUG                          # True или False
ALLOWED_HOSTS                  # можно указать звёздочку *

DOCKER_USERNAME                # имя пользователя в Docker Pub
DOCKER_PASSWORD                # пароль пользователя в Docker Pub

HOST                           # ip-адрес сервера
USER                           # имя пользователя
SSH_KEY                        # приватный SSH-ключ (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # пароль для SSH-ключа

POSTGRES_DB                    # foodgram 
POSTGRES_USER                  # foodgram_user
POSTGRES_PASSWORD              # foodgram_password
DB_NAME                        # foodgram
DB_HOST                        # db
DB_PORT                        # 5432

TELEGRAM_TO                    # id аккаунта в Telegram
TELEGRAM_TOKEN                 # токен бота
```

## Участники разработки

Сергей Хрящев [(Khryashoff)](https://github.com/Khryashoff)

---

# English version

## Description

Recipe Master is an advanced online platform where users can share their unique recipes, find new ideas and organize their culinary experience. The platform provides convenient tools for creating, organizing and publishing recipes, as well as the ability to save favorite dishes and create shopping lists.

## Launching a project in dev mode
1. Clone the repository and go to it on the command line:
```bash
git clone git@github.com:Khryashoff/recipe_master.git
```
2. Install and activate the virtual environment for the project:
```bash
python -m venv venv
```
```bash
# for OS Windows
. venv/Scripts/activate
```
3. Update pip and install dependencies from the file requirements.txt:
```bash
python -m pip install --upgrade pip
```
```bash
pip install -r requirements.txt
```
4. Perform migrations at the project level:
```bash
python manage.py migrate
```
5. Create a superuser:
```bash
python manage.py createsuperuser
```
6. Start the project:
```bash
python manage.py runserver
```

## Getting an authorization token

- Transfer to the endpoint http://127.0.0.1:8000/api/auth/token/login/
```
{
  "password": "<your_password>",
  "email": "<your_email>"
}
```

## Launching a project in local machine
1. Fork the repository

2. Clone the repository and go to it on the command line:
```bash
git clone git@github.com:"<your_github_username>"/recipe_master.git
```
2. Make a deployment to the server if you are not going to run locally:
```bash
# Connect to a remote server
sch -i path_file_SSH_key/file_name_SSH_key user_name@ip_adreserver
```
```bash
# Install docker-compose on the server:
sudo apt update
sudo apt install curl
curl -fSL https://get.docker.com -o get-docker.sh
sudo sh ./get-docker.sh
sudo apt-get install docker-compose-plugin
```
Create a .env file and fill it with your data. The list of data is specified in the root directory of the project in the .env.example file.
3. Create Docker images and upload them to DockerHub:
```bash
# Replace 'username' with your login on DockerHub:
cd ../frontend
docker build -t username/foodgram_frontend .
cd ../backend
docker build -t username/foodgram_backend .
```
```bash
# Replace 'username' with your login on DockerHub:
docker push username/foodgram_frontend
docker push username/foodgram_backend
```
```bash
# Copy the docker-compose.production.yml and .env files to the foodgram/ directory:
scp -i path_to_SSH/SSH_name docker-compose.production.yml username@server_ip:/home/username/foodgram/docker-compose.production.yml
```
4. Replace in the files **docker-composer.yml** and **docker-composer.production.yml** all available ``image`` data with your own ```<your_user name>/<image name>:latest```. 
5. In the directory **foodgram** create folders **infra**. In the foodgram/infra directory, place ``docker-composer.production.yml`` and ``nginx.conf``
6. Run docker compose in daemon mode:
```bash
sudo docker compose -f docker-compose.production.yml up -d
```
7. Make preparatory work with the project files:
```bash
# On the server, open the Nginx config in the nano editor:
sudo nano /etc/nginx/sites-enabled/default
```
```bash
# Change the location settings in the server section:
sudo nano /etc/nginx/sites-enabled/default
server {

	server_name <example.com>;
	
	location / {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000;
	}

	location /admin/ {
	   proxy_set_header Host $http_host;
	   proxy_pass http://127.0.0.1:8000/admin/;
	}
}
```
```bash
# Check the operability of the Nginx configuration:
sudo nginx -t
```
```bash
# Restart Nginx:
sudo service nginx reload
```
```bash
# Perform migrations, collect static backend files and copy them to /backend_static/static/:
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic --noinput
docker compose -f docker-compose.production.yml exec backend python manage.py ingrs_loader 
```
8. Adapt the file to suit yourself by setting up secrets using GitHub Actions:

```
SECRET_KEY                     # Secret key Django-project
DEBUG                          # True or False
ALLOWED_HOSTS                  # you can specify an asterisk *

DOCKER_USERNAME                # user name in Docker Pub
DOCKER_PASSWORD                # user password in Docker Pub

HOST                           # server ip-address
USER                           # username
SSH_KEY                        # private SSH key (cat ~/.ssh/id_rsa)
SSH_PASSPHRASE                 # passphrase for the SSH key

POSTGRES_DB                    # foodgram 
POSTGRES_USER                  # foodgram_user
POSTGRES_PASSWORD              # foodgram_password
DB_NAME                        # foodgram
DB_HOST                        # db
DB_PORT                        # 5432

TELEGRAM_TO                    # telegram account id
TELEGRAM_TOKEN                 # bot token
```

## Participants

Sergey Khryashchev [(Khryashoff)](https://github.com/Khryashoff)
