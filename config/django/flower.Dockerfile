FROM python:3.11-bullseye

WORKDIR /app
COPY ./freelance_exchange/requirements.txt .

RUN pip install --upgrade pip setuptools wheel build
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    python3-dev \
    libffi-dev \
    libssl-dev \
    netcat-openbsd \
    curl

RUN pip install --upgrade --upgrade-strategy eager --use-feature=fast-deps --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app/freelance_exchange

CMD ["celery", "-A", "freelance_exchange", "flower", "--port=5555", "--url-prefix=/flower"]