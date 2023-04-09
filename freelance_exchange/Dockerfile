FROM python:3.11-bullseye
EXPOSE 8181

# Buildtime
WORKDIR /app/freelance_exchange
COPY . /app/freelance_exchange
RUN ["pip3", "install", "-r", "requirements.txt"]

# Runtime
WORKDIR /app/freelance_exchange
ENTRYPOINT ["./docker-entrypoint.sh"]
