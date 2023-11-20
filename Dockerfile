# Dockerfile - this is a comment. Delete me if you want.
FROM --platform=linux/amd64 python:3.8-alpine
COPY requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt