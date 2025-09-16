"""
Substituto temporário para o módulo imghdr que foi removido no Python 3.13.
Este módulo é necessário para compatibilidade com o Streamlit no Python 3.13.
"""

import warnings

# Emitir um aviso sobre o uso do módulo descontinuado
warnings.warn(
    "O módulo 'imghdr' foi removido no Python 3.13. "
    "Esta é uma implementação mínima para manter a compatibilidade.",
    DeprecationWarning,
    stacklevel=2
)

def what(file):
    """Determina o tipo de imagem de um arquivo."""
    # Implementação mínima - sempre retorna None
    return None

def whatfile(filename):
    """Determina o tipo de imagem de um arquivo pelo nome."""
    # Implementação mínima - sempre retorna None
    return None

# Constantes para compatibilidade
types = {
    'rgb': 'rgb',
    'gif': 'gif',
    'pbm': 'pbm',
    'pgm': 'pgm',
    'ppm': 'ppm',
    'tiff': 'tiff',
    'rast': 'rast',
    'xbm': 'xbm',
    'jpeg': 'jpeg',
    'bmp': 'bmp',
    'png': 'png',
    'webp': 'webp',
    'exr': 'exr',
}

# Funções para verificar tipos específicos de imagem
def test_rgb(h, f):
    return h[:2] == b'\001\332'

def test_gif(h, f):
    return h[:6] in (b'GIF87a', b'GIF89a')

def test_pbm(h, f):
    return h[:2] == b'P1'

def test_pgm(h, f):
    return h[:2] == b'P2'

def test_ppm(h, f):
    return h[:2] == b'P3'

def test_tiff(h, f):
    return h[:2] in (b'MM', b'II')

def test_rast(h, f):
    return h[:4] == b'\x59\xA6\x6A\x95'

def test_xbm(h, f):
    return b'#define ' in h

def test_jpeg(h, f):
    return h[:2] == b'\xff\xd8'

def test_bmp(h, f):
    return h[:2] == b'BM'

def test_png(h, f):
    return h[:8] == b'\211PNG\r\n\032\n'

def test_webp(h, f):
    return h[:12] == b'\x52\x49\x46\x46' and h[8:12] == b'\x57\x45\x42\x50'

def test_exr(h, f):
    return h[:4] == b'\x76\x2f\x31\x01'