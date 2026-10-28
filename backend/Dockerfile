FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt "alembic>=1.13,<2.0" "uvicorn[standard]>=0.30,<1.0"

COPY . ./

EXPOSE 8000
