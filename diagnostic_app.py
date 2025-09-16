"""
App Streamlit de diagnóstico para verificar variáveis de ambiente e conexão
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Tentar carregar variáveis de ambiente
load_dotenv()

def main():
    st.title("🔧 Diagnóstico da Aplicação")
    
    # Verificar variáveis de ambiente
    st.subheader("1. Variáveis de Ambiente")
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if supabase_url:
        st.success("✅ SUPABASE_URL está definida")
        st.text(f"URL: {supabase_url[:50]}...")
    else:
        st.error("❌ SUPABASE_URL NÃO está definida")
    
    if supabase_key:
        st.success("✅ SUPABASE_KEY está definida")
    else:
        st.error("❌ SUPABASE_KEY NÃO está definida")
    
    # Verificar porta
    st.subheader("2. Configuração de Porta")
    port = os.environ.get("PORT") or os.environ.get("STREAMLIT_SERVER_PORT")
    if port:
        st.success(f"✅ Porta configurada: {port}")
    else:
        st.info("ℹ️ Porta não definida explicitamente (usará padrão)")
    
    # Testar imports críticos
    st.subheader("3. Teste de Imports")
    try:
        import streamlit as st
        st.success("✅ Streamlit importado com sucesso")
    except Exception as e:
        st.error(f"❌ Erro ao importar Streamlit: {e}")
    
    try:
        from sentence_transformers import SentenceTransformer
        st.success("✅ Sentence Transformers importado com sucesso")
    except Exception as e:
        st.error(f"❌ Erro ao importar Sentence Transformers: {e}")
    
    try:
        import faiss
        st.success("✅ FAISS importado com sucesso")
    except Exception as e:
        st.error(f"❌ Erro ao importar FAISS: {e}")
    
    try:
        import easyocr
        st.success("✅ EasyOCR importado com sucesso")
    except Exception as e:
        st.error(f"❌ Erro ao importar EasyOCR: {e}")
    
    # Testar conexão com Supabase
    st.subheader("4. Teste de Conexão com Supabase")
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            supabase = create_client(supabase_url, supabase_key)
            # Testar uma operação simples
            response = supabase.table("documentos").select("id").limit(1).execute()
            st.success("✅ Conexão com Supabase estabelecida com sucesso!")
        except Exception as e:
            st.error(f"❌ Erro na conexão com Supabase: {e}")
    else:
        st.warning("⚠️ Não é possível testar conexão - variáveis não definidas")
    
    st.info("💡 Esta é uma versão de diagnóstico da aplicação para identificar problemas.")

if __name__ == "__main__":
    main()