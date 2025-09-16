"""
App Streamlit mínima para testar carregamento
"""
import streamlit as st

def main():
    st.title("Teste de Carregamento Mínimo")
    st.write("Se você está vendo esta página, o Streamlit está funcionando!")
    
    # Informações de diagnóstico
    st.subheader("Informações de Diagnóstico")
    st.write(f"Versão do Python: {st.__version__}")
    
    # Teste simples
    if st.button("Testar Funcionalidade"):
        st.success("Funcionalidade básica funcionando!")
        
    st.info("Esta é uma versão mínima da aplicação para diagnosticar problemas de carregamento.")

if __name__ == "__main__":
    main()