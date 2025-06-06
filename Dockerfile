# Use official Python image
FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /emgmt

# Install system dependencies (optional: for psycopg2)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy app code
COPY . .

# Load .env if needed
ENV ENV_FILE=.env

# Run Alembic migrations and then start app
CMD ["sh", "-c", "alembic upgrade head && uvicorn src.emgmt.main:app --host 0.0.0.0 --port 8000 --reload"]
# CMD ["sh", "-c", "uvicorn src.emgmt.main:app --host 0.0.0.0 --port 8000 --reload"]
