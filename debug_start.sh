#!/bin/bash
# Script de diagnóstico para Railway

echo "=== DIAGNÓSTICO DO CONTAINER ==="
echo "Data/Hora: $(date)"
echo "Usuário: $(whoami)"
echo "Diretório atual: $(pwd)"
echo "Conteúdo do diretório:"
ls -la

echo -e "\n=== VARIÁVEIS DE AMBIENTE ==="
echo "PORT: $PORT"
echo "PATH: $PATH"
echo "PYTHONPATH: $PYTHONPATH"
echo "STREAMLIT*: $(env | grep STREAMLIT)"

echo -e "\n=== PROCURANDO REFERÊNCIAS AO STREAMLIT ==="
find . -type f -name "*.py" -o -name "*.txt" -o -name "*.json" -o -name "*.yml" -o -name "*.yaml" | xargs grep -l -i streamlit 2>/dev/null || echo "Nenhuma referência encontrada"

echo -e "\n=== VERIFICANDO ARQUIVOS DE CONFIGURAÇÃO DO RAILWAY ==="
if [ -f "railway.json" ]; then
    echo "Conteúdo do railway.json:"
    cat railway.json
fi

if [ -f "Procfile" ]; then
    echo -e "\nConteúdo do Procfile:"
    cat Procfile
fi

echo -e "\n=== TENTANDO INICIAR A APLICAÇÃO ==="
python app.py