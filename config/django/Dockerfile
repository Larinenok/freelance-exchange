FROM python:3.11-bullseye

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# RUN mkdir /sock
# RUN chmod -R 666 /sock
WORKDIR /app/freelance_exchange
ADD ./config/uwsgi/uwsgi.ini /etc
COPY ./freelance_exchange/requirements.txt /app/freelance_exchange
RUN ["pip3", "install", "-r", "requirements.txt"]

# Runtime
RUN chmod -R o+rw /app/freelance_exchange/init-commands.sh
WORKDIR /app/freelance_exchange
ENTRYPOINT ["./init-commands.sh"]
