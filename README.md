# Collecting Points Bot

## Описание

Collecting Points Bot — это Telegram-бот, разработанный с использованием библиотеки `aiogram`. Бот предназначен для сбора баллов пользователей. Он поддерживает взаимодействие с пользователями через команды и хранит данные в базе данных SQLite.

## Установка

### Требования

- Python 3.10 или выше
- Библиотеки:
  - aiogram
  - sqlalchemy
  - aiosqlite
  - python-dotenv

### Установка зависимостей

1. Клонируйте репозиторий:

   ```bash
   git clone git@github.com:EgorIvanov96/collecting_points.git
   cd collecting_points
   ```

2. Создайте виртуальное окружение и активируйте его:

    ```
    python -m venv venv
    source venv/bin/activate  # Для Linux/Mac
    venv\Scripts\activate  # Для Windows
    ```

3. Установите зависимости:

    ```
    pip install -r requirements.txt
    ```

### Настройка

1. Создайте файл .env в корневом каталоге проекта и добавьте следующие переменные:

    ```
    BOT_TOKEN=ВАШ_ТЕЛЕГРАМ_ТОКЕН
    DB_LITE=sqlite+aiosqlite:///db.sqlite
    ```

### Запуск
Для запуска бота используйте следующую команду:
    ```
    python app.py
    ```

Если вы используете Docker, вы можете запустить бота с помощью Docker Compose:
    ```
    docker-compose up --build
    ```