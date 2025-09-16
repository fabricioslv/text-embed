"""
Script para testar o EasyOCR e resolver problemas de codificação
"""
import os
import sys
import traceback

def test_easyocr():
    """Testa o EasyOCR com configurações adequadas para Windows"""
    print("=== Teste do EasyOCR ===")
    
    try:
        # Configurar variáveis de ambiente para evitar problemas de codificação
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        print("1. Importando EasyOCR...")
        import easyocr
        print("   SUCESSO: EasyOCR importado!")
        
        print("2. Inicializando OCR...")
        # Inicializar sem mostrar a barra de progresso para evitar problemas de codificação
        reader = easyocr.Reader(['pt'], gpu=False, verbose=False)
        print("   SUCESSO: OCR inicializado!")
        
        print("3. Testando OCR...")
        # Testar com uma imagem de exemplo (criar uma imagem simples)
        import numpy as np
        from PIL import Image, ImageDraw
        
        # Criar uma imagem simples com texto
        img = Image.new('RGB', (200, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10, 10), "Teste OCR", fill=(0, 0, 0))
        
        # Converter para array numpy
        img_array = np.array(img)
        
        # Testar o OCR
        result = reader.readtext(img_array)
        print(f"   SUCESSO: OCR executado! Resultados: {result}")
        
        print("\n[OK] EasyOCR está funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"ERRO: Falha no teste: {e}")
        print("Tipo de erro:", type(e).__name__)
        print("Traceback:")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_easyocr()