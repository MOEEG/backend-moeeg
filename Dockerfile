# Usa una imagen de Ubuntu como base
FROM ubuntu:20.04

# Actualiza el índice de paquetes e instala las dependencias necesarias
RUN apt-get update 

# Instala Python 3.8 y las herramientas de desarrollo necesarias
RUN apt-get install -y \
    && python3.8 \
    && python3.8-dev \
    && python3-pip \
    && build-essential


# Actualiza pip y setuptools
RUN python3.8 -m pip install --upgrade pip setuptools

WORKDIR /app

COPY . /app

RUN pip3 install -r requirements.txt

CMD ["python3", "src/app.py"]