# Образ backend-сервісу: FastAPI запускається всередині Python-контейнера.
FROM python:3.11-slim
WORKDIR /app

# Спочатку копіюємо requirements, щоб Docker міг кешувати встановлення залежностей.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Після залежностей копіюємо код застосунку.
COPY . .

# Uvicorn відкриває FastAPI на порту 8000 всередині контейнера.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
