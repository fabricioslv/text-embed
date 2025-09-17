#!/bin/bash
# Script para verificar variáveis de ambiente no Railway

echo "=== Variáveis de Ambiente ==="
echo "PORT: $PORT"
echo "STREAMLIT_SERVER_PORT: $STREAMLIT_SERVER_PORT"
echo "============================"

# Executar a aplicação Streamlit
exec streamlit run app.py