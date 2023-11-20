FROM alpine:3.10

RUN apk add --no-cache python3-dev \
    && pip3 install --upgrade pip \
    && apk add build-base \
    && apk add gcc \
    && apk add abuild \
    && apk add python3-dev \
    && apk add musl-dev \
    && apk add linux-headers \
    && apk add bash

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

CMD ["python3", "src/app.py"]