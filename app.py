import streamlit as st
from sentence_transformers import SentenceTransformer
import sqlite3
import json
import faiss
import numpy as np
from datetime import datetime
import os
from pdf2image import convert_from_bytes
import easyocr
from docx import Document
import pandas as pd
import plotly.express as px
from sklearn.metrics.pairwise import cosine_similarity

# Configurações iniciais
st.set_page_config(page_title="Vetorizador de Documentos", layout="wide")
st.markdown("""
<style>
.big-title { font-size: 32px; font-weight: bold; color: #4CAF50; }
.subtle { font-size: 16px; color: #777; margin-bottom: 20px; }
.card { background-color: #f9f9f9; padding: 10px; border-radius: 8px; margin-bottom: 10px; box-shadow: 1px 1px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">📚 Vetorizador Inteligente de Documentos</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Processamento de PDFs, DOCX e TXT com IA, busca semântica, exportação e dashboard completo.</div>', unsafe_allow_html=True)

# Inicialização
model = SentenceTransformer('all-MiniLM-L6-v2')
reader = easyocr.Reader(['pt'], gpu=False)
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

# Funções de extração
def extrair_texto(file):
    ext = os.path.splitext(file.name)[1].lower()
    if ext == ".pdf":
        imagens = convert_from_bytes(file.read())
        texto = ""
        for img in imagens:
            resultado = reader.readtext(np.array(img), detail=0)
            texto += "\n".join(resultado)
        return texto
    elif ext == ".docx":
        doc = Document(file)
        return "\n".join([p.text for p in doc.paragraphs])
    elif ext == ".txt":
        return file.read().decode('utf-8')
    else:
        return "Formato não suportado."

# Upload e vetorização
st.header("📂 Upload de Documentos")
uploaded_files = st.file_uploader("Selecione seus arquivos", type=["pdf", "docx", "txt"], accept_multiple_files=True)

if uploaded_files:
    for file in uploaded_files:
        texto = extrair_texto(file)
        if texto and len(texto) > 50:
            embedding = model.encode(texto)
            index.add(np.array([embedding]))
            documentos.append({"nome": file.name, "texto": texto, "embedding": embedding.tolist()})
            cursor.execute("INSERT INTO documentos (nome, texto, embedding, data) VALUES (?, ?, ?, ?)",
                           (file.name, texto, json.dumps(embedding.tolist()), datetime.now().isoformat()))
            conn.commit()
            st.success(f"✅ {file.name} processado com sucesso.")
        else:
            st.warning(f"⚠️ {file.name} não pôde ser processado ou está vazio.")

# Busca semântica
st.header("🔍 Busca Semântica")
consulta = st.text_input("Digite sua pergunta")

if consulta:
    consulta_embedding = model.encode(consulta)
    D, I = index.search(np.array([consulta_embedding]), k=3)
    for i in I[0]:
        doc = documentos[i]
        st.markdown(f"<div class='card'><strong>📄 {doc['nome']}</strong><br>{doc['texto'][:500]}...</div>", unsafe_allow_html=True)

# Chat com documentos
st.header("💬 Chat com os Documentos")
pergunta = st.text_input("Pergunte algo sobre seus arquivos")

if pergunta:
    pergunta_emb = model.encode(pergunta)
    melhores = sorted(documentos, key=lambda d: cosine_similarity([pergunta_emb], [d["embedding"]])[0][0], reverse=True)
    trecho = melhores[0]["texto"][:500]
    st.markdown(f"<div class='card'><strong>📄 {melhores[0]['nome']}</strong><br>{trecho}...</div>", unsafe_allow_html=True)

# Exportação
st.header("📤 Exportar Embeddings")
if st.button("Exportar como JSON"):
    cursor.execute("SELECT nome, embedding FROM documentos")
    dados = cursor.fetchall()
    export = [{"nome": nome, "embedding": json.loads(embedding)} for nome, embedding in dados]
    st.download_button("📥 Baixar JSON", data=json.dumps(export, indent=2), file_name="embeddings.json")

# Dashboard
st.header("📊 Resumo de Uso")
cursor.execute("SELECT COUNT(*), SUM(LENGTH(texto)) FROM documentos")
total_docs, total_bytes = cursor.fetchone()
st.metric("📄 Documentos processados", total_docs)
st.metric("💾 Espaço ocupado", f"{total_bytes / 1024 / 1024:.2f} MB")

cursor.execute("SELECT nome, data FROM documentos ORDER BY data DESC LIMIT 5")
st.subheader("📋 Últimos documentos")
for nome, data in cursor.fetchall():
    st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>Processado em {data}</span></div>", unsafe_allow_html=True)

# Gráfico de documentos por data
cursor.execute("SELECT nome, data FROM documentos")
df = pd.DataFrame(cursor.fetchall(), columns=["nome", "data"])
df["data"] = pd.to_datetime(df["data"])
fig = px.histogram(df, x="data", nbins=20, title="Documentos por Data")
st.plotly_chart(fig)

# Gerenciador de documentos
st.header("🗂️ Gerenciador de Arquivos")
nome_busca = st.text_input("🔎 Buscar documento por nome")
cursor.execute("SELECT id, nome, data, LENGTH(texto) FROM documentos WHERE nome LIKE ?", (f"%{nome_busca}%",))
docs = cursor.fetchall()

for doc_id, nome, data, tamanho in docs:
    st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>{data} — {tamanho / 1024:.1f} KB</span></div>", unsafe_allow_html=True)
    if st.button(f"🗑️ Excluir {nome}", key=doc_id):
        cursor.execute("DELETE FROM documentos WHERE id = ?", (doc_id,))
        conn.commit()
        st.success(f"{nome} excluído.")