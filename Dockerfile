# Usa una imagen de Ubuntu como base
FROM ubuntu:20.04

# Actualiza el índice de paquetes e instala las dependencias necesarias
RUN apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    && python3.8 \
    && python3.8-dev \
    && python3-pip \
    && build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Configura Python para que use UTF-8 y actualiza pip
ENV PYTHONUNBUFFERED=1 \
    PYTHONIOENCODING=UTF-8 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# Crea un enlace simbólico para que python3.8 sea accesible como python
RUN ln -s /usr/bin/python3.8 /usr/local/bin/python

# Actualiza pip y setuptools
RUN python3.8 -m pip install --upgrade pip setuptools

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "src/app.py"]