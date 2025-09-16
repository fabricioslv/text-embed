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
        
        # Validar credenciais
        if not url or not key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem ser definidos nas variáveis de ambiente")
        
        # Criar cliente Supabase
        self.supabase: Client = create_client(url, key)

    def save_document(self, nome, texto, embedding, doc_type="txt", metadata=None):
        """Salva um documento no Supabase"""
        try:
            # Converter embedding para lista se for um array numpy
            if hasattr(embedding, 'tolist'):
                embedding_data = embedding.tolist()
            else:
                embedding_data = embedding
                
            # Preparar dados do documento
            documento = {
                "nome": nome,
                "texto": texto,
                "embedding": embedding_data,
                "tamanho": len(texto) if texto else 0,
                "tipo": doc_type,
                "data": datetime.now().isoformat(),
                "metadata": json.dumps(metadata) if metadata else None
            }
            
            response = self.supabase.table("documentos").insert(documento).execute()
            return response
        except Exception as e:
            print(f"Erro ao salvar documento: {e}")
            raise

    def load_documents(self):
        """Carrega todos os documentos do Supabase"""
        try:
            response = self.supabase.table("documentos").select("*").eq("chunk_id", 0).execute()
            documentos = []
            
            for row in response.data:
                # Parse metadata if it exists
                metadata = None
                if row.get("metadata"):
                    try:
                        metadata = json.loads(row["metadata"])
                    except:
                        metadata = row["metadata"]
                
                documentos.append({
                    "id": row["id"],
                    "nome": row["nome"],
                    "texto": row["texto"],
                    "embedding": row["embedding"],
                    "tamanho": row["tamanho"],
                    "tipo": row["tipo"],
                    "data": row["data"],
                    "metadata": metadata
                })
                
            return documentos
        except Exception as e:
            print(f"Erro ao carregar documentos: {e}")
            return []

    def delete_document(self, doc_id):
        """Deleta um documento do Supabase pelo ID"""
        try:
            # Deletar documento principal e todos os seus chunks
            response = self.supabase.table("documentos").delete().eq("id", doc_id).execute()
            # Também deletar chunks associados
            self.supabase.table("documentos").delete().eq("documento_principal_id", doc_id).execute()
            return response
        except Exception as e:
            print(f"Erro ao deletar documento: {e}")
            raise

    def search_documents(self, name_pattern):
        """Busca documentos pelo padrão de nome"""
        try:
            # O Supabase usa '%' como caractere curinga para LIKE
            pattern = f"%{name_pattern}%"
            response = self.supabase.table("documentos").select("id,nome,data,tamanho,tipo").eq("chunk_id", 0).ilike("nome", pattern).execute()
            
            documents = []
            for row in response.data:
                # Calcular tamanho do texto (simulando LENGTH(texto))
                text_length = row["tamanho"] or 0
                documents.append((
                    row["id"],
                    row["nome"],
                    row["data"],
                    text_length,
                    row["tipo"]
                ))
                
            return documents
        except Exception as e:
            print(f"Erro ao buscar documentos: {e}")
            return []

    def get_document_stats(self):
        """Obtém estatísticas dos documentos"""
        try:
            # Obter contagem de documentos
            count_response = self.supabase.table("documentos").select("*", count="exact").eq("chunk_id", 0).execute()
            total_docs = count_response.count
            
            # Obter tamanho total dos textos
            response = self.supabase.table("documentos").select("tamanho").eq("chunk_id", 0).execute()
            total_bytes = sum(row["tamanho"] for row in response.data if row["tamanho"])
            
            return (total_docs, total_bytes)
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return (0, 0)

    def get_recent_documents(self, limit=5):
        """Obtém os documentos mais recentes"""
        try:
            response = self.supabase.table("documentos").select("nome,data").eq("chunk_id", 0).order("data", desc=True).limit(limit).execute()
            return [(row["nome"], row["data"]) for row in response.data]
        except Exception as e:
            print(f"Erro ao obter documentos recentes: {e}")
            return []

    def get_all_documents_for_chart(self):
        """Obtém todos os documentos para o gráfico"""
        try:
            response = self.supabase.table("documentos").select("nome,data").eq("chunk_id", 0).execute()
            return [(row["nome"], row["data"]) for row in response.data]
        except Exception as e:
            print(f"Erro ao obter documentos para gráfico: {e}")
            return []
    
    def get_document_chunks(self, doc_id):
        """Obtém todos os chunks de um documento"""
        try:
            response = self.supabase.table("documentos").select("*").eq("documento_principal_id", doc_id).order("chunk_id").execute()
            return response.data
        except Exception as e:
            print(f"Erro ao obter chunks do documento: {e}")
            return []
    
    def save_document_chunk(self, doc_id, chunk_id, total_chunks, chunk_text, chunk_embedding=None, metadata=None):
        """Salva um chunk de documento"""
        try:
            chunk_data = {
                "nome": f"chunk_{chunk_id}",
                "texto": "",  # Texto completo armazenado no documento principal
                "embedding": None,  # Embedding do documento completo
                "tamanho": len(chunk_text),
                "tipo": "chunk",
                "chunk_id": chunk_id,
                "total_chunks": total_chunks,
                "chunk_text": chunk_text,
                "chunk_embedding": chunk_embedding.tolist() if hasattr(chunk_embedding, 'tolist') else chunk_embedding,
                "metadata": json.dumps(metadata) if metadata else None,
                "documento_principal_id": doc_id
            }
            
            response = self.supabase.table("documentos").insert(chunk_data).execute()
            return response
        except Exception as e:
            print(f"Erro ao salvar chunk: {e}")
            raise