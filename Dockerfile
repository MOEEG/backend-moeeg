# Dockerfile - this is a comment. Delete me if you want.
FROM python:3.8.18-alpine3.18
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt