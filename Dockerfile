# Используем официальный легкий образ Python
FROM python:3.11-slim

WORKDIR /app

# Копируем только requirements.txt сначала для кэширования слоев
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . .

# Папку output лучше тоже создать на этапе сборки
RUN mkdir -p output

EXPOSE 8000

# Убрали --reload (перенесли в docker-compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]