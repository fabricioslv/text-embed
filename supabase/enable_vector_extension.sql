-- Este script habilita a extensão vector no Supabase
-- Execute este SQL no painel do Supabase no SQL Editor

-- Habilitar a extensão vector (necessária para embeddings)
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar se a extensão foi habilitada
SELECT name FROM pg_available_extensions WHERE name = 'vector';

-- Verificar se está instalada
SELECT extname FROM pg_extension WHERE extname = 'vector';