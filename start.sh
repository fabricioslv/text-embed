#!/bin/bash
# Script de inicialização simplificado

echo "=== Iniciando aplicação Flask ==="
echo "Data/Hora: $(date)"
echo "PORT: ${PORT:-8080}"

# Iniciar aplicação diretamente
exec python app.py