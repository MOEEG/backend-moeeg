FROM alpine:3.10

RUN apk add python3-dev \
    && pip3 install --upgrade pip \
    && apk add build-base

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "src/app.py"]