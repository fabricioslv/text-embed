"""
Módulo para gerenciamento de chunks de documentos
"""
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class DocumentChunk:
    """Representa um chunk de documento"""
    id: Optional[int] = None
    document_id: Optional[int] = None
    chunk_id: int = 0
    total_chunks: int = 1
    text: str = ""
    embedding: Optional[List[float]] = None
    position: int = 0
    metadata: Optional[Dict[str, Any]] = None

class DocumentChunker:
    """Classe para dividir documentos em chunks"""
    
    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """
        Inicializa o chunker
        
        Args:
            chunk_size: Tamanho máximo de cada chunk em caracteres
            overlap: Número de caracteres de sobreposição entre chunks
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str, doc_id: Optional[int] = None, 
                   metadata: Optional[Dict[str, Any]] = None) -> List[DocumentChunk]:
        """
        Divide um texto em chunks
        
        Args:
            text: Texto a ser dividido
            doc_id: ID do documento original
            metadata: Metadados adicionais
            
        Returns:
            Lista de DocumentChunk
        """
        if not text:
            return []
        
        chunks = []
        text_length = len(text)
        chunk_id = 0
        
        # Calcular número total de chunks
        total_chunks = max(1, (text_length - self.overlap) // (self.chunk_size - self.overlap) + 1)
        
        start = 0
        while start < text_length:
            end = min(start + self.chunk_size, text_length)
            chunk_text = text[start:end]
            
            chunk = DocumentChunk(
                document_id=doc_id,
                chunk_id=chunk_id,
                total_chunks=total_chunks,
                text=chunk_text,
                position=start,
                metadata=metadata or {}
            )
            
            chunks.append(chunk)
            chunk_id += 1
            
            # Avançar com sobreposição
            start = end - self.overlap if end < text_length else end
        
        return chunks
    
    def reconstruct_text(self, chunks: List[DocumentChunk]) -> str:
        """
        Reconstrói o texto original a partir dos chunks
        
        Args:
            chunks: Lista de chunks ordenados
            
        Returns:
            Texto reconstruído
        """
        if not chunks:
            return ""
        
        # Ordenar chunks por posição
        sorted_chunks = sorted(chunks, key=lambda x: x.position)
        return "".join(chunk.text for chunk in sorted_chunks)

class DocumentLibrary:
    """Classe para gerenciar a biblioteca de documentos e seus chunks"""
    
    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.chunker = DocumentChunker()
    
    def store_document(self, name: str, text: str, embedding: List[float], 
                      doc_type: str = "txt", metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Armazena um documento completo e seus chunks
        
        Args:
            name: Nome do documento
            text: Texto completo do documento
            embedding: Embedding do documento completo
            doc_type: Tipo do documento
            metadata: Metadados adicionais
            
        Returns:
            ID do documento inserido
        """
        # Preparar dados do documento principal
        doc_data = {
            "nome": name,
            "texto": text,
            "embedding": embedding,
            "tamanho": len(text),
            "tipo": doc_type,
            "data": datetime.now().isoformat(),
            "metadata": json.dumps(metadata) if metadata else None
        }
        
        # Inserir documento principal
        response = self.supabase.table("documentos").insert(doc_data).execute()
        doc_id = response.data[0]["id"]
        
        # Dividir em chunks e armazenar
        chunks = self.chunker.chunk_text(text, doc_id, metadata)
        if chunks:
            chunk_data = []
            for chunk in chunks:
                chunk_data.append({
                    "nome": f"{name}_chunk_{chunk.chunk_id}",
                    "texto": text,  # Texto completo para referência
                    "embedding": embedding,  # Embedding do documento completo
                    "tamanho": len(text),
                    "tipo": doc_type,
                    "chunk_id": chunk.chunk_id,
                    "total_chunks": chunk.total_chunks,
                    "chunk_text": chunk.text,
                    "chunk_embedding": None,  # Pode ser preenchido posteriormente
                    "metadata": json.dumps(chunk.metadata) if chunk.metadata else None,
                    "documento_principal_id": doc_id  # Referência ao documento principal
                })
            
            # Inserir chunks
            self.supabase.table("documentos").insert(chunk_data).execute()
        
        return doc_id
    
    def get_document_chunks(self, doc_id: int) -> List[Dict[str, Any]]:
        """
        Obtém todos os chunks de um documento
        
        Args:
            doc_id: ID do documento
            
        Returns:
            Lista de chunks
        """
        response = self.supabase.table("documentos").select("*").eq("documento_principal_id", doc_id).execute()
        return response.data
    
    def search_similar_chunks(self, query_embedding: List[float], limit: int = 10) -> List[Dict[str, Any]]:
        """
        Busca chunks similares a um embedding de consulta
        
        Args:
            query_embedding: Embedding de consulta
            limit: Limite de resultados
            
        Returns:
            Lista de chunks similares
        """
        response = self.supabase.table("documentos").select("*").neq("chunk_embedding", None).limit(limit).execute()
        # Aqui você implementaria a lógica de similaridade real
        # Esta é uma implementação simplificada
        return response.data
    
    def get_document_statistics(self) -> Dict[str, Any]:
        """
        Obtém estatísticas da biblioteca de documentos
        
        Returns:
            Dicionário com estatísticas
        """
        try:
            # Total de documentos
            total_response = self.supabase.table("documentos").select("*", count="exact").execute()
            total_docs = total_response.count or 0
            
            # Total de chunks
            chunks_response = self.supabase.table("documentos").select("*", count="exact").neq("chunk_id", 0).execute()
            total_chunks = chunks_response.count or 0
            
            # Tamanho total
            size_response = self.supabase.table("documentos").select("tamanho").execute()
            total_size = sum(row["tamanho"] for row in size_response.data if row["tamanho"]) if size_response.data else 0
            
            return {
                "total_documentos": total_docs,
                "total_chunks": total_chunks,
                "tamanho_total": total_size,
                "tamanho_medio": total_size / total_docs if total_docs > 0 else 0,
                "tamanho_total_mb": total_size / 1024 / 1024
            }
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}

# Exemplo de uso
if __name__ == "__main__":
    # Exemplo de como usar a biblioteca
    print("DocumentChunker e DocumentLibrary prontos para uso!")
    print("Para usar, importe estas classes em seu aplicativo principal.")