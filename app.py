from flask import Flask, request, jsonify, render_template_string
import os
from sentence_transformers import SentenceTransformer
import json
import faiss
import numpy as np
from datetime import datetime
import easyocr
from docx import Document
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Inicialização
model = SentenceTransformer('all-MiniLM-L6-v2')
reader = easyocr.Reader(['pt'], gpu=False)
embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
documentos = []

# Página HTML básica
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Vetorizador de Documentos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .card { background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin: 10px 0; }
        .upload-form { border: 2px dashed #ccc; padding: 20px; text-align: center; }
        input, textarea, button { padding: 10px; margin: 5px; }
        button { background-color: #4CAF50; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #45a049; }
    </style>
</head>
<body>
    <h1>📚 Vetorizador Inteligente de Documentos</h1>
    
    <div class="upload-form">
        <h2>📂 Upload de Documentos</h2>
        <form method="post" action="/upload" enctype="multipart/form-data">
            <input type="file" name="file" accept=".pdf,.docx,.txt" required>
            <button type="submit">Processar Documento</button>
        </form>
    </div>
    
    <div>
        <h2>🔍 Busca Semântica</h2>
        <form method="get" action="/search">
            <input type="text" name="query" placeholder="Digite sua pergunta" style="width: 300px;">
            <button type="submit">Buscar</button>
        </form>
    </div>
    
    {% if results %}
    <div>
        <h2>📋 Resultados</h2>
        {% for doc in results %}
        <div class="card">
            <strong>📄 {{ doc.nome }}</strong><br>
            {{ doc.texto[:300] }}...
        </div>
        {% endfor %}
    </div>
    {% endif %}
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    # Processamento básico de upload
    return jsonify({"status": "Documento processado com sucesso!"})

@app.route('/search')
def search():
    query = request.args.get('query', '')
    # Busca semântica básica
    return render_template_string(HTML_TEMPLATE, results=[])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=True)