# FoodGram project

![FoodGram Workflow](https://github.com/Ilia-Pringless/foodgram-project-react/actions/workflows/main.yml/badge.svg)

Cервис для публикаций и обмена рецептами.

Авторизованным пользователям доступны функции создания рецепта, добавление понравившихся рецептов в избраннное, добавление рецептов в список покупок. В список покупок записываются необходимые ингредиенты для приготовления, есть возможность скачать список продуктов в формате PDF. Авторизованным пользователям доступна подписка на других авторов. 
Неавторизованным пользователям доступна регистрация, авторизация, просмотр рецептов других пользователей.

- Сервис расположен по адресу: 
```
http://158.160.1.73/
```

- Страница администрирования
```
158.160.1.73/admin/
```
- Авторизация Django
> login:
>> ```ilia-admin```

> password:
>> ```my-best-pass```


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
### Добавление нового рецепта. 

*POST* ```158.160.1.73/api/recipes/```
```
{
  "ingredients": [
    {
      "id": 1123,
      "amount": 10
    }
  ],
  "tags": [
    1,
    2
  ],
  "image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJggg==",
  "name": "string",
  "text": "string",
  "cooking_time": 1
}
```
*Ответ*

```
{
  "id": 0,
  "tags": [
    {
      "id": 0,
      "name": "Завтрак",
      "color": "#E26C2D",
      "slug": "breakfast"
    }
  ],
  "author": {
    "email": "user@example.com",
    "id": 0,
    "username": "string",
    "first_name": "Ваня",
    "last_name": "Иванов",
    "is_subscribed": false
  },
  "ingredients": [
    {
      "id": 0,
      "name": "Картофель отварной",
      "measurement_unit": "г",
      "amount": 1
    } 
  ],
  "is_favorited": true,
  "is_in_shopping_cart": true,
  "name": "string",
  "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
  "text": "string",
  "cooking_time": 1
}
```
### Подписка на пользователя {id}

*POST*  ```158.160.1.73/api/users/{id}/subscribe/```
*Ответ*
```
{
  "email": "user@example.com",
  "id": 0,
  "username": "string",
  "first_name": "Вася",
  "last_name": "Пупкин",
  "is_subscribed": true,
  "recipes": [
    {
      "id": 0,
      "name": "string",
      "image": "http://foodgram.example.org/media/recipes/images/image.jpeg",
      "cooking_time": 1
    }
  ],
  "recipes_count": 0
}
```
