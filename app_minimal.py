"""
App Streamlit minimalista e funcional
"""
import streamlit as st
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

def main():
    st.set_page_config(page_title="Vetorizador de Documentos", layout="wide")
    
    # Estilos CSS minimalistas
    st.markdown("""
    <style>
    .big-title { font-size: 32px; font-weight: bold; color: #4CAF50; }
    .subtle { font-size: 16px; color: #777; margin-bottom: 20px; }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="big-title">📚 Vetorizador Inteligente de Documentos</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtle">Versão de diagnóstico - carregamento mínimo</div>', unsafe_allow_html=True)
    
    # Informações do sistema
    st.header("📋 Informações do Sistema")
    
    # Verificar variáveis de ambiente
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if supabase_url:
            st.success("✅ SUPABASE_URL configurada")
        else:
            st.warning("⚠️ SUPABASE_URL não encontrada")
    
    with col2:
        if supabase_key:
            st.success("✅ SUPABASE_KEY configurada")
        else:
            st.warning("⚠️ SUPABASE_KEY não encontrada")
    
    # Teste de funcionalidades básicas
    st.header("🔧 Teste de Funcionalidades")
    
    # Botão para testar interatividade
    if st.button("Testar Interatividade"):
        st.success("✅ Aplicação está respondendo!")
        st.balloons()
    
    # Informações úteis
    st.info("💡 Esta é uma versão minimalista da aplicação para diagnóstico.")
    
    # Próximos passos
    st.divider()
    st.subheader("🔄 Próximos Passos")
    st.write("1. Se esta página carregou, o Streamlit está funcionando!")
    st.write("2. Verifique as variáveis de ambiente no painel do Streamlit Cloud")
    st.write("3. Confirme que o Supabase está acessível")
    st.write("4. Tente fazer rebuild da aplicação")

if __name__ == "__main__":
    main()