FROM python:3.11-slim

WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект внутрь контейнера
COPY . .

# Создаем папку для отчетов, если её нет
RUN mkdir -p /app/output

# ВОТ ОНА - МАГИЧЕСКАЯ СТРОКА! Запускаем сервер на 0.0.0.0
CMD ["uvicorn", "app.gateway:app", "--host", "0.0.0.0", "--port", "8000"]