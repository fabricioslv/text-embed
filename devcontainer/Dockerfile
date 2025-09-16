FROM python:3.10

# Instala dependências básicas
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1-mesa-glx \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório de trabalho
WORKDIR /workspace

# Copia os arquivos do projeto
COPY . /workspace