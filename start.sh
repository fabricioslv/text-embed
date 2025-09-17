#!/bin/bash
# Script de inicialização para Railway

# Verificar se há variáveis de ambiente problemáticas
echo "=== Variáveis de Ambiente ==="
echo "PORT: $PORT"
echo "STREAMLIT_* vars:"
env | grep STREAMLIT

# Iniciar a aplicação
echo "=== Iniciando aplicação Flask ==="
python app.py