#!/bin/bash
# Script de inicialização para Railway

# Verificar se há variáveis de ambiente problemáticas
echo "=== Verificando variáveis de ambiente ==="
echo "PORT: $PORT"
echo "PYTHONPATH: $PYTHONPATH"
env | grep -i streamlit || echo "Nenhuma variável STREAMLIT encontrada"

# Verificar conteúdo do diretório
echo "=== Conteúdo do diretório ==="
ls -la

# Verificar se app.py existe e é executável
if [ -f "app.py" ]; then
    echo "app.py encontrado:"
    ls -l app.py
else
    echo "ERRO: app.py não encontrado!"
    exit 1
fi

# Iniciar a aplicação diretamente
echo "=== Iniciando aplicação Flask ==="
exec python app.py