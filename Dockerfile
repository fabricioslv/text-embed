# Dockerfile otimizado para aplica\u00e7\u00e3o Streamlit
FROM python:3.12-slim

# Definir vari\u00e1veis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8

# Instalar depend\u00eancias do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Definir diret\u00f3rio de trabalho
WORKDIR /app

# Copiar requirements primeiro para aproveitar cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o c\u00f3digo da aplica\u00e7\u00e3o
COPY . .

# Criar diret\u00f3rio para modelos (se necess\u00e1rio)
RUN mkdir -p /root/.cache

# Exp\u00f5e a porta que o Streamlit usa
EXPOSE 8501

# Healthcheck otimizado
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Comando para rodar a aplica\u00e7\u00e3o
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]