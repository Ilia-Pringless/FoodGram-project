# praktikum_new_diplom

![workflow](https://github.com/Ilia-Pringless/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

- Страница администрирования
```
130.193.54.148/admin/
```
- Страница просмотра документации о проекте
```
130.193.54.148/redoc/
```

В данном проекте реализованно api сервиса YaMDb.

Проект YaMDb собирает отзывы (Review) пользователей на произведения (Titles). Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Список категорий (Category) может быть расширен администратором (например, можно добавить категорию «Изобразительное искусство» или «Ювелирка»). Также имеется возможность оставлять комментарии (Comments) к отзывам.

## Шаблон заполнения env-файла

- DJANGO_KEY= _здесь указать секретный ключ_
- DB_ENGINE=django.db.backends.postgresql
- DB_NAME=postgres
- POSTGRES_USER=_здесь задать имя пользователя БД_
- POSTGRES_PASSWORD=_здесь написать пароль от БД_
- DB_HOST=db
- DB_PORT=5432


## Запуск проекта в режиме резработчика.
- После скачивания проекта, перейдите в папку проекта и установите виртуальное окружение..

```
python3 -m venv venv
```
- ...и активируйте его

```
source ./venv/bin/activate
```
- Установите зависимости из файла requirements.txt
```
pip install -r requirements.txt
``` 
- И выполните команду:
```
python3 api_yamdb/manage.py runserver
```

## Запуск приложения в контейнерах

- Сборка образов и контейнеров (из папки infra/)

```docker-compose up -d --build ```

## Примеры запросов и ответов от api:
### Добавление нового отзыва. 

POST NAME_OF_YOUR_DOMAIN/api/v1/titles/{title_id}/reviews/
```
{
  "text": "string",
  "score": 1
}
```
Ответ

```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "score": 1,
  "pub_date": "2019-08-24T14:15:22Z"
}
```
### Получение комментария comment_id к отзыву title_id

GET  NAME_OF_YOUR_DOMAIN/api/v1/titles/{title_id}/reviews/{review_id}/comments/{comment_id}
```
{
  "id": 0,
  "text": "string",
  "author": "string",
  "pub_date": "2019-08-24T14:15:22Z"
}
```
