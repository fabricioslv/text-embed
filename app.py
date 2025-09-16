import streamlit as st
from sentence_transformers import SentenceTransformer
import textract
import sqlite3
import json
import faiss
import numpy as np
from datetime import datetime
import os

# Inicialização
st.set_page_config(page_title="Vetorizador de Documentos", layout="wide")
model = SentenceTransformer('all-MiniLM-L6-v2')
embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
documentos = []

# Banco de dados
conn = sqlite3.connect("documentos.db")
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

# Carrega documentos do banco
def carregar_documentos():
    cursor.execute("SELECT nome, texto, embedding FROM documentos")
    for nome, texto, embedding in cursor.fetchall():
        emb = json.loads(embedding)
        documentos.append({"nome": nome, "texto": texto, "embedding": emb})
        index.add(np.array([emb]))

carregar_documentos()

# Upload e vetorização
st.title("🧠 Vetorizador de Documentos com IA")
st.markdown("Envie múltiplos arquivos PDF, DOCX ou TXT para extrair texto e gerar embeddings.")

uploaded_files = st.file_uploader("Selecione os arquivos", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        try:
            texto = textract.process(file).decode('utf-8')
            embedding = model.encode(texto)
            index.add(np.array([embedding]))
            documentos.append({"nome": file.name, "texto": texto, "embedding": embedding.tolist()})
            cursor.execute("INSERT INTO documentos (nome, texto, embedding, data) VALUES (?, ?, ?, ?)",
                           (file.name, texto, json.dumps(embedding.tolist()), datetime.now().isoformat()))
            conn.commit()
            st.success(f"{file.name} processado com sucesso.")
        except Exception as e:
            st.error(f"Erro ao processar {file.name}: {str(e)}")

# Busca semântica
st.header("🔍 Busca Semântica")
consulta = st.text_input("Digite sua pergunta")

if consulta:
    consulta_embedding = model.encode(consulta)
    D, I = index.search(np.array([consulta_embedding]), k=3)
    for i in I[0]:
        doc = documentos[i]
        st.markdown(f"**📄 {doc['nome']}**")
        st.write(doc["texto"][:500] + "...")

# Exportação
st.header("📤 Exportar Embeddings")
if st.button("Exportar como JSON"):
    cursor.execute("SELECT nome, embedding FROM documentos")
    dados = cursor.fetchall()
    export = [{"nome": nome, "embedding": json.loads(embedding)} for nome, embedding in dados]
    st.download_button("Baixar JSON", data=json.dumps(export, indent=2), file_name="embeddings.json")

# Dashboard de documentos
st.header("📋 Documentos Processados")
cursor.execute("SELECT nome, data FROM documentos ORDER BY data DESC")
docs = cursor.fetchall()
for nome, data in docs:
    st.markdown(f"📄 **{nome}** — `{data}`")