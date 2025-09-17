# Dockerfile simplificado
FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Tornar scripts executáveis
RUN chmod +x *.sh

# Expõe a porta padrão
EXPOSE 8080

# Comando para rodar a aplicação
CMD ["python", "app.py"]