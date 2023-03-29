FROM python:3.11-bullseye
EXPOSE 8000

# Buildtime
WORKDIR /app
COPY . .
RUN ["pip3", "install", "-r", "requirements.txt"]

# Runtime
WORKDIR /app/freelance_exchange
ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8000"]