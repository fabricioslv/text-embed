# Dockerfile para aplicação Streamlit no Railway
FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Definir diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Tornar o entrypoint executável
RUN chmod +x entrypoint.sh

# Criar diretório para modelos (se necessário)
RUN mkdir -p /root/.cache

# Expõe a porta padrão do Streamlit
EXPOSE 8501

# Comando para rodar a aplicação
CMD ["./entrypoint.sh"]