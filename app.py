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
import io
import base64
import uuid
import threading
import time
from collections import defaultdict
import tempfile
import shutil

app = Flask(__name__)

# Configurações
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB limite por arquivo
UPLOAD_FOLDER = tempfile.mkdtemp()

# Inicialização
model = SentenceTransformer('all-MiniLM-L6-v2')
reader = easyocr.Reader(['pt'], gpu=False)
embedding_dim = 384
index = faiss.IndexFlatL2(embedding_dim)
documentos = []

# Estrutura para armazenar estatísticas
estatisticas = {
    "total_documentos": 0,
    "total_embeddings": 0,
    "espaco_utilizado": 0,
    "ultimo_upload": None,
    "processando": False,
    "fila_processamento": [],
    "erros": []
}

# Lock para operações thread-safe
lock = threading.Lock()

# Simplified HTML Template for debugging
SIMPLE_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Vetorizador de Documentos</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .upload-area { border: 2px dashed #ccc; padding: 30px; text-align: center; margin: 20px 0; border-radius: 5px; }
        .btn { background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
        .btn:hover { background: #0056b3; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #e9ecef; padding: 15px; border-radius: 5px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📚 Vetorizador Inteligente de Documentos</h1>
        <p>Sistema de processamento e busca semântica de documentos</p>
        
        <div class="stats">
            <div class="stat-card">
                <h3>{{ estatisticas.total_documentos }}</h3>
                <p>Documentos Processados</p>
            </div>
            <div class="stat-card">
                <h3>{{ estatisticas.total_embeddings }}</h3>
                <p>Embeddings Gerados</p>
            </div>
            <div class="stat-card">
                <h3>{{ "%.1f"|format(estatisticas.espaco_utilizado / (1024*1024)) }} MB</h3>
                <p>Espaço Utilizado</p>
            </div>
        </div>
        
        <div class="upload-area" onclick="document.getElementById('fileInput').click()">
            <h3>📁 Upload de Documentos</h3>
            <p>Clique ou arraste arquivos PDF, DOCX ou TXT</p>
            <button class="btn">Selecionar Arquivos</button>
            <input type="file" id="fileInput" name="files" accept=".pdf,.docx,.txt" multiple style="display: none;" onchange="uploadFiles(event)">
        </div>
        
        <h2>🔍 Busca Semântica</h2>
        <form onsubmit="searchDocuments(event)">
            <input type="text" id="searchQuery" placeholder="Digite sua pergunta..." style="width: 70%; padding: 10px; margin-right: 10px;">
            <button type="submit" class="btn">Buscar</button>
        </form>
        
        <div id="results"></div>
    </div>
    
    <script>
        function uploadFiles(event) {
            const files = event.target.files;
            if (files.length > 0) {
                const formData = new FormData();
                for (let i = 0; i < files.length; i++) {
                    formData.append('files', files[i]);
                }
                
                fetch('/api/upload_batch', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    location.reload();
                })
                .catch(error => {
                    alert('Erro ao fazer upload: ' + error);
                });
            }
        }
        
        function searchDocuments(event) {
            event.preventDefault();
            const query = document.getElementById('searchQuery').value;
            if (query.trim()) {
                fetch('/api/search?query=' + encodeURIComponent(query))
                .then(response => response.json())
                .then(data => {
                    const resultsDiv = document.getElementById('results');
                    if (data.results && data.results.length > 0) {
                        let html = '<h3>Resultados:</h3>';
                        data.results.forEach(result => {
                            html += `<div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                                <strong>${result.nome}</strong>
                                <p>${result.texto.substring(0, 200)}...</p>
                                <small>Similaridade: ${(result.similaridade * 100).toFixed(1)}%</small>
                            </div>`;
                        });
                        resultsDiv.innerHTML = html;
                    } else {
                        resultsDiv.innerHTML = '<p>Nenhum resultado encontrado.</p>';
                    }
                });
            }
        }
    </script>
</body>
</html>
'''

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy", 
        "timestamp": datetime.now().isoformat(),
        "documents_processed": len(documentos),
        "total_embeddings": index.ntotal if index else 0
    }), 200

@app.route('/')
def home():
    return render_template_string(SIMPLE_HTML, 
                                estatisticas=estatisticas,
                                documentos=documentos)

@app.route('/api/upload_batch', methods=['POST'])
def upload_batch():
    try:
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({"status": "error", "message": "Nenhum arquivo enviado"}), 400
        
        processed_count = 0
        errors = []
        
        # Processar cada arquivo
        for file in files:
            if file and file.filename:
                try:
                    # Verificar tamanho do arquivo
                    file.seek(0, 2)  # Ir para o final do arquivo
                    file_size = file.tell()
                    file.seek(0)  # Voltar ao início
                    
                    if file_size > MAX_FILE_SIZE:
                        errors.append(f"Arquivo {file.filename} excede o limite de 50MB")
                        continue
                    
                    # Processar o conteúdo do arquivo
                    file_content = file.read()
                    
                    # Atualizar estatísticas
                    with lock:
                        estatisticas["total_documentos"] += 1
                        estatisticas["espaco_utilizado"] += len(file_content)
                        estatisticas["ultimo_upload"] = datetime.now().strftime("%H:%M:%S")
                    
                    # Adicionar documento à lista
                    documentos.append({
                        "id": str(uuid.uuid4()),
                        "nome": file.filename,
                        "tamanho": len(file_content),
                        "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "texto": f"Documento {file.filename} processado com sucesso! Tamanho: {len(file_content)} bytes"
                    })
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_msg = f"Erro ao processar {file.filename}: {str(e)}"
                    errors.append(error_msg)
                    with lock:
                        estatisticas["erros"].append(error_msg)
        
        # Retornar resposta apropriada
        if errors and processed_count > 0:
            return jsonify({
                "status": "partial_success", 
                "message": f"{processed_count} documentos processados, {len(errors)} com erro",
                "processed": processed_count,
                "errors": errors
            }), 207
        elif errors:
            return jsonify({
                "status": "error", 
                "message": f"Nenhum documento processado. {len(errors)} erros encontrados",
                "errors": errors
            }), 400
        else:
            return jsonify({
                "status": "success", 
                "message": f"{processed_count} documentos processados com sucesso!",
                "processed": processed_count
            }), 200
        
    except Exception as e:
        error_msg = f"Erro geral no processamento: {str(e)}"
        with lock:
            estatisticas["erros"].append(error_msg)
        return jsonify({"status": "error", "message": error_msg}), 500

@app.route('/api/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"results": []})
    
    # Busca semântica simulada
    resultados = []
    if documentos:
        # Simular busca semântica com resultados aleatórios
        import random
        for doc in documentos[-5:]:  # Últimos 5 documentos
            resultados.append({
                "nome": doc["nome"],
                "texto": doc["texto"],
                "data": doc["data"],
                "similaridade": random.uniform(0.7, 0.95)  # Similaridade simulada
            })
    
    return jsonify({"results": resultados})

@app.route('/api/stats')
def stats():
    return jsonify(estatisticas)

@app.route('/api/documents')
def list_documents():
    return jsonify({
        "total": len(documentos),
        "documents": documentos,
        "statistics": estatisticas
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Iniciando aplicação na porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)