FROM python:3-slim

WORKDIR /fastapi_app

COPY fastapi_app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY fastapi_app/ .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]