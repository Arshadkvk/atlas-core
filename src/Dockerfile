FROM python:3.12-slim

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Shows Python output immediately
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]