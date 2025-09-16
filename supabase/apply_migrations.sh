#!/bin/bash
# Script para executar migrações no Supabase

# Verificar se o Supabase CLI está instalado
if ! command -v supabase &> /dev/null
then
    echo "Supabase CLI não encontrado. Instalando..."
    npm install -g supabase
fi

# Iniciar o projeto Supabase local (opcional)
# supabase init

# Linkar com o projeto remoto (substitua pela sua URL)
# supabase link --project-ref YOUR_PROJECT_ID

# Aplicar migrações
echo "Aplicando migrações..."
supabase db push

echo "Migrações aplicadas com sucesso!"