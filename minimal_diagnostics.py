"""
Versão minimalista do app.py para diagnóstico
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    st.title("📚 Vetorizador Inteligente de Documentos - Modo Diagnóstico")
    
    # Verificar variáveis de ambiente críticas
    st.header("📋 Diagnóstico do Sistema")
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if supabase_url:
            st.success("✅ SUPABASE_URL configurada")
        else:
            st.error("❌ SUPABASE_URL não encontrada")
    
    with col2:
        if supabase_key:
            st.success("✅ SUPABASE_KEY configurada")
        else:
            st.error("❌ SUPABASE_KEY não encontrada")
    
    # Teste de imports essenciais
    st.subheader("🔧 Teste de Componentes")
    
    components = [
        ("Streamlit", "import streamlit"),
        ("Sentence Transformers", "from sentence_transformers import SentenceTransformer"),
        ("FAISS", "import faiss"),
        ("NumPy", "import numpy"),
        ("EasyOCR", "import easyocr"),
        ("Supabase", "from supabase import create_client")
    ]
    
    for name, import_stmt in components:
        try:
            exec(import_stmt)
            st.success(f"✅ {name}")
        except Exception as e:
            st.error(f"❌ {name} - {str(e)[:50]}...")
    
    # Informações importantes
    st.info("💡 Esta é uma versão minimalista para diagnóstico. "
            "Se você está vendo esta página, o Streamlit está funcionando!")
    
    st.divider()
    st.write("🔄 **Próximos passos:**")
    st.write("1. Verifique se todas as dependências estão instaladas")
    st.write("2. Confirme que o Supabase está acessível")
    st.write("3. Tente fazer upload de um documento de teste")

if __name__ == "__main__":
    main()