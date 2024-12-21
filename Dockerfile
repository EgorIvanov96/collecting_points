FROM python:3.10

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем файл .env в контейнер
COPY .env ./

# Запускаем приложение
CMD ["python", "app.py"]