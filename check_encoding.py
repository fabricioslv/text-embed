"""
Script para verificar encoding dos arquivos críticos
"""
import os
import chardet

def check_file_encoding(file_path):
    """Verifica o encoding de um arquivo"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding'], result['confidence']
    except Exception as e:
        return None, 0

def main():
    """Verifica encoding dos arquivos críticos"""
    print("=== Verificacao de Encoding dos Arquivos ===")
    
    critical_files = [
        "app.py",
        "requirements.txt",
        "Procfile",
        "runtime.txt",
        ".env",
        "src/supabase_db.py",
        "src/document_library.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            encoding, confidence = check_file_encoding(file_path)
            if encoding:
                print(f"[OK] {file_path}: {encoding} ({confidence:.2f} confidence)")
            else:
                print(f"[ERRO] {file_path}: Nao foi possivel detectar encoding")
        else:
            print(f"[AVISO] {file_path}: Arquivo nao encontrado")

if __name__ == "__main__":
    main()