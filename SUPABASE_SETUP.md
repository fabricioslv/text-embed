# Configuração do Supabase para o Projeto

## 1. Criando a Tabela "documentos"

Após criar seu projeto no Supabase, execute o seguinte SQL no Editor SQL:

```sql
CREATE TABLE documentos (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nome TEXT,
    texto TEXT,
    embedding JSONB,
    data TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 2. Tipos de Dados no PostgreSQL

| Campo SQLite     | Tipo PostgreSQL           | Justificativa |
|------------------|---------------------------|---------------|
| id (INTEGER)     | uuid                      | Melhor prática para distribuição |
| nome (TEXT)      | text                      | Equivalente direto |
| texto (TEXT)     | text                      | Equivalente direto |
| embedding (TEXT) | jsonb                     | Armazena JSON de forma eficiente |
| data (TEXT)      | timestamp with time zone  | Tipo apropriado para datas |

## 3. Obtendo Credenciais de Conexão

1. No painel do Supabase, clique em "Project Settings"
2. Vá para "API"
3. Anote:
   - Project URL: `https://<project-ref>.supabase.co`
   - anon key ou service_role key

## 4. Instalando o Cliente Supabase

Adicione ao `requirements.txt`:
```
supabase>=2.0.0
```

Instale com:
```bash
pip install supabase
```

## 5. Configuração de Variáveis de Ambiente

Crie um arquivo `.env`:
```
SUPABASE_URL=sua_url_do_projeto
SUPABASE_KEY=sua_chave
```