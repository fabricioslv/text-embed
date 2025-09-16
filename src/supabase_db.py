import json
from datetime import datetime
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class SupabaseDBManager:
    def __init__(self):
        # Obter URL e chave do Supabase das variáveis de ambiente
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")
        
        # Criar cliente Supabase
        self.supabase: Client = create_client(url, key)

    def save_document(self, nome, texto, embedding):
        """Salva um documento no Supabase"""
        # Converter embedding para lista se for um array numpy
        if hasattr(embedding, 'tolist'):
            embedding_data = embedding.tolist()
        else:
            embedding_data = embedding
            
        # Inserir documento na tabela
        documento = {
            "nome": nome,
            "texto": texto,
            "embedding": embedding_data,
            "data": datetime.now().isoformat()
        }
        
        response = self.supabase.table("documentos").insert(documento).execute()
        return response

    def load_documents(self):
        """Carrega todos os documentos do Supabase"""
        response = self.supabase.table("documentos").select("*").execute()
        documentos = []
        
        for row in response.data:
            documentos.append({
                "nome": row["nome"],
                "texto": row["texto"],
                "embedding": row["embedding"]
            })
            
        return documentos

    def delete_document(self, doc_id):
        """Deleta um documento do Supabase pelo ID"""
        response = self.supabase.table("documentos").delete().eq("id", doc_id).execute()
        return response

    def search_documents(self, name_pattern):
        """Busca documentos pelo padrão de nome"""
        # O Supabase usa '%' como caractere curinga para LIKE
        pattern = f"%{name_pattern}%"
        response = self.supabase.table("documentos").select("id,nome,data,texto").ilike("nome", pattern).execute()
        
        documents = []
        for row in response.data:
            # Calcular tamanho do texto (simulando LENGTH(texto))
            text_length = len(row["texto"]) if row["texto"] else 0
            documents.append((
                row["id"],
                row["nome"],
                row["data"],
                text_length
            ))
            
        return documents

    def get_document_stats(self):
        """Obtém estatísticas dos documentos"""
        # Obter contagem de documentos
        count_response = self.supabase.table("documentos").select("*", count="exact").execute()
        total_docs = count_response.count
        
        # Obter tamanho total dos textos
        response = self.supabase.table("documentos").select("texto").execute()
        total_bytes = sum(len(row["texto"]) for row in response.data if row["texto"])
        
        return (total_docs, total_bytes)

    def get_recent_documents(self, limit=5):
        """Obtém os documentos mais recentes"""
        response = self.supabase.table("documentos").select("nome,data").order("data", desc=True).limit(limit).execute()
        return [(row["nome"], row["data"]) for row in response.data]

    def get_all_documents_for_chart(self):
        """Obtém todos os documentos para o gráfico"""
        response = self.supabase.table("documentos").select("nome,data").execute()
        return [(row["nome"], row["data"]) for row in response.data]