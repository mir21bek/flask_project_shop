# API Документация
## 1. Создание администратора

### URL: /admin-create
### Метод: POST
Описание: Создает нового администратора.

Тело запроса:

json

    {
    "username": "string",
    "email": "string",
    "password": "string"
    }

Ответ:

    Успех: 201 Created

    json

    {
    "Message": "User created successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
    }
    }

Ошибка: 400 Bad Request (если данные неверные)

json

    {
    "error": "Invalid data"
    }

Ошибка: 400 Bad Request (если имя пользователя или email уже существуют)

json

    {
        "message": "This username or email already exists"
    }

    Ошибка: 500 Internal Server Error (в случае внутренней ошибки сервера)

## 2. Создание покупателя

### URL: /buyer-create
### Метод: POST
Описание: Создает нового покупателя.

Тело запроса:

json

    {
    "username": "string",
    "email": "string",
    "password": "string"
    }

Ответ:

    Успех: 201 Created

    json

    {
    "Message": "User created successfully",
    "user": {
        "id": "integer",
        "username": "string",
        "email": "string"
    }
    }

Ошибка: 400 Bad Request (если данные неверные)

json

    {
    "error": "Invalid data"
    }

Ошибка: 400 Bad Request (если имя пользователя или email уже существуют)

json

    {
        "message": "This username or email already exists"
    }

    Ошибка: 500 Internal Server Error (в случае внутренней ошибки сервера)

## 3. Авторизация

### URL: /login
### Метод: POST
Описание: Выполняет авторизацию и возвращает JWT токен.

Тело запроса:

json

    {
    "email": "string",
    "password": "string"
    }

Ответ:

    Успех: 201 Created

    json

    {
    "access_token": "string"
    }

Ошибка: 401 Unauthorized (если email или пароль неверные)

json

    {
        "error": "Bad email or password"
    }

## 4. Получение списка пользователей

### URL: /users
### Метод: GET
Описание: Возвращает список всех пользователей.

Ответ:

    Успех: 200 OK

    json

    [
        {
            "id": "integer",
            "username": "string",
            "email": "string"
        },
        ...
    ]

## 5. Создание категории

### URL: /categories
### Метод: POST
Описание: Создает новую категорию.

Тело запроса:

json

    {
    "name": "string",
    "parent_id": "integer" (опционально)
    }

Ответ:

    Успех: 201 Created

    json

    {
    "Message": "Category created successfully",
    "category": {
        "id": "integer",
        "name": "string",
        "parent_id": "integer" (опционально)
    }
    }

Ошибка: 400 Bad Request (если данные неверные)

json

    {
        "error": "Invalid data"
    }

    Ошибка: 404 Not Found (если родительская категория не найдена)

## 6. Получение списка категорий

### URL: /categories
### Метод: GET
Описание: Возвращает список всех категорий или категорий по родительскому идентификатору.

Параметры запроса:

    parent_id (опционально) - идентификатор родительской категории

Ответ:

    Успех: 200 OK

    json

    [
        {
            "id": "integer",
            "name": "string",
            "parent_id": "integer" (опционально)
        },
        ...
    ]

## 7. Удаление категории

### URL: /categories/<int:cat_id>
### Метод: DELETE
Описание: Удаляет категорию по идентификатору.

Параметры пути:

    cat_id - идентификатор категории

Ответ:

    Успех: 200 OK

    json

    {
    "Message": "Category deleted successfully"
    }

Ошибка: 404 Not Found (если категория не найдена)

json

    {
    "error": "Category not found"
    }

Ошибка: 400 Bad Request (если категория содержит подкатегории)

json

    {
        "error": "Category has child categories. Please remove child categories first"
    }

## 8. Создание продукта

### URL: /product-create
### Метод: POST
Описание: Создает новый продукт. Доступно только для администраторов.

Тело запроса:

json

    {
    "category_id": "integer",
    "name": "string",
    "title": "string",
    "price": "float"
    }

Ответ:

    Успех: 201 Created

    json

    {  
    "Message": "Product create successfully",
    "product": {
        "id": "integer",
        "name": "string",
        "title": "string",
        "price": "float",
        "category_id": "integer" (опционально)
    }
    }

Ошибка: 400 Bad Request (если данные неверные)

json

    {
    "error": "Invalid data"
    }

Ошибка: 404 Not Found (если категория не найдена)

json

    {
        "error": "Category id not found"
    }

    Ошибка: 403 Forbidden (если доступ запрещен)

## 9. Получение списка продуктов

### URL: /product-list
### Метод: GET
Описание: Возвращает список всех продуктов.

Ответ:

    Успех: 200 OK

    json

    [
        {
            "id": "integer",
            "name": "string",
            "title": "string",
            "price": "float",
            "category_id": "integer" (опционально)
        },
        ...
    ]

## 10. Получение продуктов по категории

### URL: /category/<int:category_id>/products
### Метод: GET
Описание: Возвращает список продуктов в заданной категории.

Параметры пути:

    category_id - идентификатор категории

Ответ:

    Успех: 200 OK

    json

    {
    "category": "string",
    "products": [
        {
            "id": "integer",
            "name": "string",
            "title": "string",
            "price": "float",
            "category_id": "integer"
        },
        ...
    ]
    }

Ошибка: 404 Not Found (если категория не найдена или нет продуктов в категории)