# Dockerfile para aplicação Streamlit
FROM python:3.13-slim

# Definir variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Criar ambiente virtual
RUN python -m venv $VIRTUAL_ENV

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser/app

# Copiar requirements e instalar dependências no ambiente virtual
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

# Healthcheck
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8501/_stcore/health

# Comando para rodar a aplicação
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]