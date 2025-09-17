#!/bin/bash
# Script de inicialização simplificado

echo "=== Iniciando aplicação Flask ==="
echo "Data/Hora: $(date)"
echo "Usuário: $(whoami)"
echo "Diretório: $(pwd)"
echo "PORT: $PORT"
echo "PATH: $PATH"

# Verificar se app.py existe
if [ -f "app.py" ]; then
    echo "app.py encontrado"
    ls -l app.py
else
    echo "ERRO: app.py não encontrado!"
    exit 1
fi

# Verificar dependências
echo "=== Verificando dependências ==="
python -c "import flask; print('Flask OK')" || exit 1
python -c "import sentence_transformers; print('Sentence Transformers OK')" || exit 1

# Iniciar aplicação
echo "=== Iniciando servidor Flask ==="
exec python app.py