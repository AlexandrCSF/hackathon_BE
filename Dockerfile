FROM python:3.11.1-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get  upgrade && apt-get update
RUN apt-get install -y --no-install-recommends git
RUN apt-get install -y --no-install-recommends gcc

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./hackathon /app


CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
#CMD ["uwsgi", "--http", ":8000", "--ini", "/uwsgi.ini"]