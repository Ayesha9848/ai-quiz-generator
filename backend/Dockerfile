FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y build-essential gcc libpq-dev --no-install-recommends && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
COPY . /app

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
