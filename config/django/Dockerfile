FROM python:3.11-bullseye

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /app/freelance_exchange

# Копируем файл requirements.txt
COPY ./freelance_exchange/requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./freelance_exchange /app/freelance_exchange

COPY ./freelance_exchange/init-commands.sh /app/freelance_exchange
RUN chmod +x /app/freelance_exchange/init-commands.sh

WORKDIR /app/freelance_exchange
ENTRYPOINT ["/app/freelance_exchange/init-commands.sh"]
