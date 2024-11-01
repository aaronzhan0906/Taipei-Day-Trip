FROM python:3-slim

# for aiohttp
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "django_app.asgi:application", "--host", "0.0.0.0", "--port", "8001"]