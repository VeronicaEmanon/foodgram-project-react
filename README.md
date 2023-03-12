# FOODGRAM. Продуктовый помощник
  
![badge](https://github.com/VeronicaEmanon/foodgram-project-react/actions/workflows/main.yml/badge.svg)
---
- <b>Адрес: </b>
- http://158.160.21.134/

- <b> АДМИН: </b>
email: admin@mail.ru
password: practicum

## 1. Описание

  
Проект предоставляет возможность взаимодействовать с базой данных по следующим направлениям:

- регистрироваться

- авторизироваться

- создавать свои рецепты и управлять ими (корректировать\удалять)

- просматривать рецепты других пользователей

- подписываться на публикации других пользователей

- добавлять в избранное рецепты, которые понравятся

- добавлять рецепты в корзину и скачивать список продуктов в .txt формате

  

---
## 1.2. Шаблон переменных файла  .env

Создайте файл .env в папке infra и заполните его:

	DB_ENGINE=django.db.backends.postgresq

	DB_NAME=postgres

	POSTGRES_USER=postgres

	POSTGRES_PASSWORD=postgres

	DB_HOST=db

	DB_PORT=5432

---

## 1.. Команды для запуска локально

  

Перед запуском необходимо склонировать проект:

```bash

HTTPS: git clone https://github.com/VeronicaEmanon/foodgram-project-react.git

SSH: git clone git@github.com:VeronicaEmanon/foodgram-project-react.git

```

  

Cоздать и активировать виртуальное окружение:

```bash

python -m venv venv

```

```bash

source venv/Scripts/activate

```

  

И установить зависимости из файла requirements.txt:

```bash

python3 -m pip install --upgrade pip

```

```bash

pip install -r requirements.txt

```

  

Выполнить миграции:

```bash

python3 manage.py migrate

```

  

Запустить проект:

```bash

python3 manage.py runserver

```

---
## 2. Docker 
Docker — это платформа контейнеризации с открытым исходным кодом, с помощью которой можно автоматизировать создание приложений, их доставку и управление. Платформа позволяет быстрее тестировать и выкладывать приложения, запускать на одной машине требуемое количество контейнеров.

## 2.1. Команды для запуска docker-compose
Собрать контейнеры в папке infra с файлом <b>docker-compose.yaml </b>:
```bash

cd infra

```
```bash

docker-compose up -d --build

```
Выполните команды по-очереди:
1. Выполните миграции
```bash

docker-compose exec backend python manage.py migrate

```
2. Создайте суперюзера
```bash

docker-compose exec backend python manage.py createsuperuser

```
3.  Соберите статику
```bash

docker-compose exec backend python manage.py collectstatic --no-input

```
Проект доступен по адресу:
_[http://localhost/](http://localhost/)_.
Также после создания суперюзера есть возможность авторизоваться по адресу:
_[http://localhost/admin/](http://localhost/admin/)_
Остановить <b>docker-compose</b> можно командой
```bash

docker-compose down -v

```

## 2.2 Работа на сервере
Основные команды:
- Обзор:

```
sudo docker image ls #обзор имеющихся образов
sudo docker container ls -a #обзор ВСЕХ контейнеров
sudo docker container ls #обзор ЗАПУЩЕННЫХ контейнеров
sudo docker container #вызов списка команд для работы с контейнером
sudo docker exec -it <CONTAINER ID> bash #вход в контейнер
sudo docker-compose exec web ls <DIRECTORY> #вход в директорию контейнера
```
- Работа:
```
sudo docker container start <CONTAINER ID> #запуск контейнера
sudo docker container stop <CONTAINER ID> #остановка контейнера
sudo docker container rm <CONTAINER ID> #удаление контейнера
sudo docker image rm <IMAGE ID> #удаление образа
```
Остановка службы NGINX:

`
sudo systemctl stop nginx
`

<b>Адреса: </b>
- http://158.160.21.134/

- АДМИН:
email: admin@mail.ru
password: practicum

## 3. Информация об API (на примере POSTMAN)
Далее все адреса вводятся в приложение <b>POSTMAN</b>.
В проекте используется JWT - аутентификация. Для регистрации придумайте логин и пароль на эндпоинт `api/auth/users/`:
```
{
    "email": "myemail",
    "first_name": "MyName",
    "last_name": "MyLastName",
	"username": "MyNickName",
	"password": "1234qwerty"
}
```
Для получения токена отпавьте <b>POST</b>- запрос на эндпоинт `/auth/token/login/` с действующим логином и паролем в соответствующих полях.

API вернет вам token. Его необходимо добавить в разделе `Headers` в поле `Authorization`. Перед токеном должно стоять ключевое слово `Token` и пробел.

Для дальнейших определенных действий нужно зарегистрироваться и авторизоваться:

Для создания ТЭГА необходимо отправить <b>POST</b>-запрос на эндпоинт `/api/tags/`:
```
{
    "name": "Ужин",
    "color": "#FF4500",
    "slug": "Ujin"
}
```

Для создания ИНГРЕДИЕНТА необходимо отправить <b>POST</b>-запрос на эндпоинт `/api/ingredients/`:
```
{
    "name": "Мясо",
    "measurement_unit": "кг"
}
```

Для создания РЕЦЕПТА необходимо отправить <b>POST</b>-запрос на эндпоинт `/api/recipes/`:
```
{
    "name": "Мясо по-французки",
    "tags": [1, 2],
    "ingredients": [
        {
            "id": 1,
            "amount": 3
        }
    ],
	"text": "Очень вкусно",
    "cooking_time": "120",
}
```
## 4. Техническая информация

  

<b>Стек технологий:</b> Python 3, Django, Django Rest, PostgreSQL, Gunicorn, NGINX, Docker

  

---

## 5. Автор

Никитина Вероника
