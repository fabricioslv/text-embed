# Dockerfile para aplicação Streamlit
FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código da aplicação
COPY . .

# Alterar permissões para o usuário não-root
RUN chown -R appuser:appuser /home/appuser/app

# Usuário não-root
USER appuser

# Expõe a porta que o Streamlit usa
EXPOSE 8501

# Comando para rodar a aplicação
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]