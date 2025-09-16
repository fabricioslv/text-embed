import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os

def show_dashboard(db_manager):
    st.header("📊 Resumo de Uso")
    
    # Obter estatísticas
    total_docs, total_bytes = db_manager.get_document_stats()
    
    # Mostrar métricas
    st.metric("📄 Documentos processados", total_docs or 0)
    st.metric("💾 Espaço ocupado", f"{(total_bytes or 0) / 1024 / 1024:.2f} MB")

    # Últimos documentos
    st.subheader("📋 Últimos documentos")
    recent_docs = db_manager.get_recent_documents()
    for nome, data in recent_docs:
        st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>Processado em {data}</span></div>", unsafe_allow_html=True)

    # Gráfico de documentos por data
    all_docs = db_manager.get_all_documents_for_chart()
    if all_docs:
        df = pd.DataFrame(all_docs, columns=["nome", "data"])
        df["data"] = pd.to_datetime(df["data"])
        fig = px.histogram(df, x="data", nbins=20, title="Documentos por Data")
        st.plotly_chart(fig)

def show_document_manager(db_manager):
    st.header("🗂️ Gerenciador de Arquivos")
    nome_busca = st.text_input("🔎 Buscar documento por nome")
    
    docs = db_manager.search_documents(nome_busca)
    for doc_id, nome, data, tamanho in docs:
        st.markdown(f"<div class='card'>📄 <strong>{nome}</strong><br><span class='subtle'>{data} — {tamanho / 1024:.1f} KB</span></div>", unsafe_allow_html=True)
        if st.button(f"🗑️ Excluir {nome}", key=doc_id):
            db_manager.delete_document(doc_id)
            st.success(f"{nome} excluído.")
            st.experimental_rerun()