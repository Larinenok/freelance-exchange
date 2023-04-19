FROM python:3.11-bullseye

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# RUN mkdir /sock
# RUN chmod -R 666 /sock
WORKDIR /app/freelance_exchange
COPY ./freelance_exchange /app/freelance_exchange
ADD ./config/uwsgi/uwsgi.ini /etc
RUN ["pip3", "install", "-r", "requirements.txt"]

# Runtime
WORKDIR /app/freelance_exchange
ENTRYPOINT ["./init-commands.sh"]
