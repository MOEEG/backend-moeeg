FROM alpine:3.10

RUN apk add python3-dev=3.8.12-r1 \
    && pip3 install --upgrade pip \
    && apk add build-base

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "src/app.py"]