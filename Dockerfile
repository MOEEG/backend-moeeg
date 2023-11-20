FROM alpine:3.10

RUN apt-get update && apt-get install -y \
    python3-dev \
    build-essential \
    libnumpy-dev \
    libopenblas-dev \
    libblas-dev \
    liblapack-dev \
    libatlas-base-dev \
    libhdf5-dev \
    libhdf5-serial-dev \
    libprotobuf-dev \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip

WORKDIR /app

COPY . /app

RUN pip3 --no-cache-dir install -r requirements.txt

CMD ["python3", "src/app.py"]