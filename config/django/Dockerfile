FROM python:3.11-bullseye

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app/freelance_exchange

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


RUN which celery || echo "celery NOT FOUND"
RUN pip show celery || echo "celery package missing"

COPY ./freelance_exchange /app/freelance_exchange
COPY ./freelance_exchange/init-commands.sh /app/freelance_exchange
COPY ./freelance_exchange/wait-for-it.sh /app/freelance_exchange
COPY ./freelance_exchange/celery-entrypoint.sh /app/freelance_exchange
COPY ./freelance_exchange/celery_beat_entrypoint.sh /app/freelance_exchange


RUN chmod +x /app/freelance_exchange/init-commands.sh
RUN chmod +x /app/freelance_exchange/wait-for-it.sh
RUN chmod +x /app/freelance_exchange/celery-entrypoint.sh
RUN chmod +x /app/freelance_exchange/celery_beat_entrypoint.sh

WORKDIR /app/freelance_exchange
ENTRYPOINT ["/app/freelance_exchange/init-commands.sh"]
