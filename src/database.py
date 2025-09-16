import sqlite3
import json
from datetime import datetime
import os

class DatabaseManager:
    def __init__(self, db_path="documentos.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS documentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            texto TEXT,
            embedding TEXT,
            data TEXT
        )
        """)
        conn.commit()
        conn.close()

    def save_document(self, nome, texto, embedding):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO documentos (nome, texto, embedding, data) VALUES (?, ?, ?, ?)",
                       (nome, texto, json.dumps(embedding.tolist()), datetime.now().isoformat()))
        conn.commit()
        conn.close()

    def load_documents(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, texto, embedding FROM documentos")
        documents = []
        for nome, texto, embedding in cursor.fetchall():
            documents.append({
                "nome": nome,
                "texto": texto,
                "embedding": json.loads(embedding)
            })
        conn.close()
        return documents

    def delete_document(self, doc_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
        conn.commit()
        conn.close()

    def search_documents(self, name_pattern):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, data, LENGTH(texto) FROM documentos WHERE nome LIKE ?", (f"%{name_pattern}%",))
        documents = cursor.fetchall()
        conn.close()
        return documents

    def get_document_stats(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*), SUM(LENGTH(texto)) FROM documentos")
        stats = cursor.fetchone()
        conn.close()
        return stats

    def get_recent_documents(self, limit=5):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, data FROM documentos ORDER BY data DESC LIMIT ?", (limit,))
        documents = cursor.fetchall()
        conn.close()
        return documents

    def get_all_documents_for_chart(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT nome, data FROM documentos")
        documents = cursor.fetchall()
        conn.close()
        return documents