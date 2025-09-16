"""
Script para verificar variáveis de ambiente no Streamlit Cloud
"""
import os
from dotenv import load_dotenv

def check_streamlit_env():
    """Verifica as variáveis de ambiente no ambiente do Streamlit"""
    print("=== Verificação de Variáveis de Ambiente ===")
    
    # Tentar carregar .env
    print("1. Tentando carregar .env...")
    load_dotenv()
    print("   Tentativa de carregamento concluída!")
    
    # Verificar variáveis importantes
    print("2. Verificando variáveis de ambiente...")
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    print(f"   SUPABASE_URL: {'Definida' if supabase_url else 'NÃO DEFINIDA'}")
    print(f"   SUPABASE_KEY: {'Definida' if supabase_key else 'NÃO DEFINIDA'}")
    
    if supabase_url:
        print(f"   SUPABASE_URL (primeiros 70 caracteres): {supabase_url[:70]}...")
    
    # Verificar outras variáveis possíveis
    print("3. Verificando outras variáveis relevantes...")
    
    # Variáveis do Streamlit
    streamlit_vars = [
        "STREAMLIT_SERVER_PORT",
        "PORT", 
        "STREAMLIT_SERVER_ADDRESS",
        "STREAMLIT_BROWSER_SERVER_ADDRESS"
    ]
    
    for var in streamlit_vars:
        value = os.environ.get(var)
        if value:
            print(f"   {var}: {value}")
    
    # Verificar diretório atual e estrutura
    print("4. Informações do ambiente...")
    print(f"   Diretório atual: {os.getcwd()}")
    print(f"   Arquivo .env existe: {os.path.exists('.env')}")
    
    # Listar arquivos importantes
    important_files = [
        "app.py",
        "requirements.txt",
        ".env",
        "src/supabase_db.py"
    ]
    
    for file in important_files:
        exists = os.path.exists(file)
        print(f"   {file}: {'Existe' if exists else 'NÃO EXISTE'}")
    
    print("\n[INFO] Verificação concluída!")
    return True

if __name__ == "__main__":
    check_streamlit_env()