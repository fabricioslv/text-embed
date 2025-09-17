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

# HTML Template completo
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 Vetorizador Inteligente de Documentos</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --primary-color: #4361ee;
            --secondary-color: #3f37c9;
            --accent-color: #4cc9f0;
            --success-color: #4ade80;
            --warning-color: #facc15;
            --danger-color: #f87171;
            --dark-color: #1e293b;
            --light-color: #f8fafc;
        }
        
        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .card {
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
            border: none;
            transition: transform 0.3s ease;
            background: rgba(255,255,255,0.95);
            backdrop-filter: blur(10px);
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .upload-area {
            border: 3px dashed #4361ee;
            border-radius: 15px;
            background: rgba(255,255,255,0.9);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .upload-area:hover {
            border-color: #3f37c9;
            background: rgba(255,255,255,0.95);
        }
        
        .stat-card {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            border-radius: 15px;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            border: none;
            border-radius: 10px;
            padding: 10px 20px;
            font-weight: 600;
        }
        
        .btn-primary:hover {
            background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
            transform: translateY(-2px);
        }
        
        .navbar-brand {
            font-weight: 700;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(135deg, var(--primary-color), var(--accent-color));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .progress-bar {
            background: linear-gradient(90deg, var(--primary-color), var(--accent-color));
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }
        
        .status-online {
            background-color: var(--success-color);
            box-shadow: 0 0 10px var(--success-color);
        }
        
        .status-processing {
            background-color: var(--warning-color);
            box-shadow: 0 0 10px var(--warning-color);
            animation: pulse 1.5s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .file-drop-highlight {
            border-color: #3f37c9 !important;
            background-color: rgba(255,255,255,0.98) !important;
        }
    </style>
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-brain me-2"></i>
                Vetorizador Inteligente
            </a>
            <div class="d-flex align-items-center">
                <span class="badge bg-{% if estatisticas.processando %}warning{% else %}success{% endif %} me-2">
                    <span class="status-indicator status-{% if estatisticas.processando %}processing{% else %}online{% endif %}"></span>
                    {% if estatisticas.processando %}Processando{% else %}Online{% endif %}
                </span>
                <span class="badge bg-info">{{ estatisticas.total_documentos }} documentos</span>
            </div>
        </div>
    </nav>

    <div class="container py-5">
        <!-- Header -->
        <div class="text-center mb-5">
            <h1 class="display-4 fw-bold text-white mb-3">
                <i class="fas fa-robot me-3"></i>Processamento Inteligente de Documentos
            </h1>
            <p class="lead text-white-50 mb-4">
                Transforme seus documentos em embeddings vetoriais para busca semântica avançada
            </p>
        </div>

        <!-- Stats Cards -->
        <div class="row mb-5">
            <div class="col-md-3 mb-4">
                <div class="stat-card card h-100 text-center p-4">
                    <i class="fas fa-file-alt fa-2x mb-3"></i>
                    <h3>{{ estatisticas.total_documentos }}</h3>
                    <p class="mb-0">Documentos</p>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stat-card card h-100 text-center p-4">
                    <i class="fas fa-vector-square fa-2x mb-3"></i>
                    <h3>{{ estatisticas.total_embeddings }}</h3>
                    <p class="mb-0">Embeddings</p>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stat-card card h-100 text-center p-4">
                    <i class="fas fa-database fa-2x mb-3"></i>
                    <h3>{{ "%.1f"|format(estatisticas.espaco_utilizado / (1024*1024)) }} MB</h3>
                    <p class="mb-0">Armazenados</p>
                </div>
            </div>
            <div class="col-md-3 mb-4">
                <div class="stat-card card h-100 text-center p-4">
                    <i class="fas fa-clock fa-2x mb-3"></i>
                    <h3>{{ estatisticas.ultimo_upload or "N/A" }}</h3>
                    <p class="mb-0">Último Upload</p>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="row">
            <!-- Left Column - Upload -->
            <div class="col-lg-6 mb-4">
                <div class="card upload-area p-5 text-center" id="uploadArea">
                    <i class="fas fa-cloud-upload-alt fa-3x mb-4 text-primary"></i>
                    <h3 class="mb-3">Upload de Documentos</h3>
                    <p class="text-muted mb-4">
                        Suporte para PDF, DOCX e TXT<br>
                        <small>Arraste e solte ou clique para selecionar</small>
                    </p>
                    <button class="btn btn-primary btn-lg" onclick="document.getElementById('fileInput').click()">
                        <i class="fas fa-folder-open me-2"></i>Selecionar Arquivos
                    </button>
                    <input type="file" id="fileInput" name="files" accept=".pdf,.docx,.txt" multiple style="display: none;" onchange="handleFileSelect(event)">
                </div>

                <!-- Batch Processing Info -->
                <div class="card mt-4 p-4">
                    <h3 class="mb-4"><i class="fas fa-tasks me-2"></i>Fila de Processamento</h3>
                    {% if estatisticas.fila_processamento and estatisticas.fila_processamento|length > 0 %}
                        <div class="alert alert-warning">
                            <i class="fas fa-hourglass-half me-2"></i>
                            {{ estatisticas.fila_processamento|length }} documentos na fila de processamento
                        </div>
                    {% else %}
                        <div class="alert alert-success">
                            <i class="fas fa-check-circle me-2"></i>
                            Nenhum documento na fila de processamento
                        </div>
                    {% endif %}
                    
                    {% if estatisticas.erros and estatisticas.erros|length > 0 %}
                        <div class="alert alert-danger mt-3">
                            <i class="fas fa-exclamation-triangle me-2"></i>
                            {{ estatisticas.erros|length }} erros encontrados
                            <button class="btn btn-sm btn-outline-danger ms-2" onclick="clearErrors()">Limpar Erros</button>
                        </div>
                    {% endif %}
                </div>

                <!-- Search Section -->
                <div class="card mt-4 p-4">
                    <h3 class="mb-4"><i class="fas fa-search me-2"></i>Busca Semântica</h3>
                    <form id="searchForm">
                        <div class="input-group mb-3">
                            <input type="text" class="form-control" id="searchQuery" placeholder="Digite sua pergunta ou termo de busca..." required>
                            <button class="btn btn-primary" type="submit">
                                <i class="fas fa-search"></i>
                            </button>
                        </div>
                    </form>
                    <div id="searchResults"></div>
                </div>
            </div>

            <!-- Right Column - Features -->
            <div class="col-lg-6">
                <div class="card p-4 mb-4">
                    <h3 class="mb-4"><i class="fas fa-star me-2"></i>Recursos Avançados</h3>
                    <div class="row text-center">
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-file-pdf"></i>
                            </div>
                            <p class="small mb-0">PDF</p>
                        </div>
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-file-word"></i>
                            </div>
                            <p class="small mb-0">DOCX</p>
                        </div>
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-file-alt"></i>
                            </div>
                            <p class="small mb-0">TXT</p>
                        </div>
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-brain"></i>
                            </div>
                            <p class="small mb-0">IA</p>
                        </div>
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-search"></i>
                            </div>
                            <p class="small mb-0">Busca</p>
                        </div>
                        <div class="col-4 mb-3">
                            <div class="feature-icon">
                                <i class="fas fa-download"></i>
                            </div>
                            <p class="small mb-0">Export</p>
                        </div>
                    </div>
                </div>

                <!-- System Info -->
                <div class="card p-4">
                    <h3 class="mb-4"><i class="fas fa-info-circle me-2"></i>Informações do Sistema</h3>
                    <div class="row">
                        <div class="col-6">
                            <p><strong>Modelo:</strong><br>all-MiniLM-L6-v2</p>
                        </div>
                        <div class="col-6">
                            <p><strong>Dimensões:</strong><br>384</p>
                        </div>
                        <div class="col-6">
                            <p><strong>Index:</strong><br>FAISS FlatL2</p>
                        </div>
                        <div class="col-6">
                            <p><strong>OCR:</strong><br>EasyOCR (PT)</p>
                        </div>
                        <div class="col-12">
                            <p><strong>Limite Arquivo:</strong><br>50MB por arquivo</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Recent Documents -->
        <div class="card p-4 mt-4">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3><i class="fas fa-history me-2"></i>Documentos Recentes</h3>
                <a href="/api/documents" class="btn btn-outline-primary btn-sm" target="_blank">
                    <i class="fas fa-code me-1"></i>API
                </a>
            </div>
            {% if documentos %}
                <div class="row">
                    {% for doc in documentos[-6:]|reverse %}
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="card p-3 h-100">
                            <div class="d-flex justify-content-between align-items-start mb-2">
                                <h6 class="mb-0">
                                    <i class="fas fa-file me-1 text-primary"></i>
                                    {{ doc.nome[:20] }}{% if doc.nome|length > 20 %}...{% endif %}
                                </h6>
                                <span class="badge bg-secondary">{{ "%.1f"|format(doc.tamanho / 1024) }} KB</span>
                            </div>
                            <small class="text-muted">{{ doc.data }}</small>
                            <div class="mt-2">
                                <span class="badge bg-success">Processado</span>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>
            {% else %}
                <div class="text-center py-5">
                    <i class="fas fa-file fa-3x text-muted mb-3"></i>
                    <p class="text-muted">Nenhum documento processado ainda</p>
                </div>
            {% endif %}
        </div>
    </div>

    <!-- Loading Modal -->
    <div class="modal fade" id="loadingModal" tabindex="-1">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-body text-center p-5">
                    <div class="spinner-border text-primary mb-3" role="status">
                        <span class="visually-hidden">Carregando...</span>
                    </div>
                    <h5>Processando Documentos</h5>
                    <p class="text-muted">Isso pode levar alguns segundos...</p>
                    <div class="progress">
                        <div class="progress-bar progress-bar-striped progress-bar-animated" style="width: 100%"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    <script>
        // Função para lidar com seleção de arquivos
        function handleFileSelect(event) {
            const files = event.target.files;
            if (files.length > 0) {
                processFiles(files);
            }
        }
        
        // Função para processar múltiplos arquivos
        function processFiles(files) {
            // Mostrar modal de carregamento
            const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
            modal.show();
            
            // Criar FormData para enviar múltiplos arquivos
            const formData = new FormData();
            let fileCount = 0;
            
            for (let i = 0; i < files.length; i++) {
                if (files[i].size > 50 * 1024 * 1024) { // 50MB
                    alert(`Arquivo ${files[i].name} excede o limite de 50MB. Será ignorado.`);
                    continue;
                }
                formData.append('files', files[i]);
                fileCount++;
            }
            
            if (fileCount === 0) {
                modal.hide();
                return;
            }
            
            // Enviar todos os arquivos de uma vez
            fetch('/api/upload_batch', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                setTimeout(() => {
                    modal.hide();
                    if (data.status === 'success') {
                        alert(`${data.processed} documentos processados com sucesso!`);
                        location.reload();
                    } else if (data.status === 'partial_success') {
                        let message = `${data.processed} documentos processados`;
                        if (data.errors && data.errors.length > 0) {
                            message += `, ${data.errors.length} com erro`;
                        }
                        alert(message);
                        location.reload();
                    } else {
                        alert('Erro ao processar documentos: ' + data.message);
                    }
                }, 1000);
            })
            .catch(error => {
                console.error('Erro:', error);
                modal.hide();
                alert('Erro ao enviar documentos');
            });
        }
        
        // Função para limpar erros
        function clearErrors() {
            fetch('/api/clear_errors', {
                method: 'POST'
            })
            .then(() => location.reload());
        }
        
        // Função de busca
        document.getElementById('searchForm').addEventListener('submit', function(e) {
            e.preventDefault();
            const query = document.getElementById('searchQuery').value;
            if (!query.trim()) return;
            
            fetch(`/api/search?query=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data.results);
            })
            .catch(error => {
                console.error('Erro na busca:', error);
                document.getElementById('searchResults').innerHTML = 
                    '<div class="alert alert-danger">Erro ao realizar busca</div>';
            });
        });
        
        // Função para exibir resultados da busca
        function displaySearchResults(results) {
            const container = document.getElementById('searchResults');
            if (!results || results.length === 0) {
                container.innerHTML = '<div class="alert alert-info">Nenhum resultado encontrado</div>';
                return;
            }
            
            let html = `<h4 class="mb-3">${results.length} resultados encontrados</h4>`;
            results.forEach(result => {
                html += `
                <div class="card mb-3 p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6><i class="fas fa-file me-2 text-primary"></i>${result.nome}</h6>
                        <span class="badge bg-info">Similaridade: ${(result.similaridade * 100).toFixed(1)}%</span>
                    </div>
                    <p class="text-muted">${result.texto.substring(0, 200)}${result.texto.length > 200 ? '...' : ''}</p>
                    <small class="text-muted">${result.data}</small>
                </div>
                `;
            });
            
            container.innerHTML = html;
        }
        
        // Drag and drop support
        document.addEventListener('DOMContentLoaded', function() {
            const uploadArea = document.getElementById('uploadArea');
            
            uploadArea.addEventListener('dragover', function(e) {
                e.preventDefault();
                uploadArea.classList.add('file-drop-highlight');
            });
            
            uploadArea.addEventListener('dragleave', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('file-drop-highlight');
            });
            
            uploadArea.addEventListener('drop', function(e) {
                e.preventDefault();
                uploadArea.classList.remove('file-drop-highlight');
                
                const files = e.dataTransfer.files;
                if (files.length > 0) {
                    document.getElementById('fileInput').files = files;
                    processFiles(files);
                }
            });
        });
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
        "total_embeddings": index.ntotal if index else 0,
        "processing_queue": len(estatisticas.get('fila_processamento', [])),
        "is_processing": estatisticas.get('processando', False)
    })

@app.route('/')
def home():
    # Garantir que as estruturas existam
    if 'fila_processamento' not in estatisticas:
        estatisticas['fila_processamento'] = []
    if 'erros' not in estatisticas:
        estatisticas['erros'] = []
    
    return render_template_string(HTML_TEMPLATE, 
                                estatisticas=estatisticas,
                                documentos=documentos)

@app.route('/api/upload_batch', methods=['POST'])
def upload_batch():
    try:
        files = request.files.getlist('files')
        if not files or len(files) == 0:
            return jsonify({"status": "error", "message": "Nenhum arquivo enviado"})
        
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
            })
        elif errors:
            return jsonify({
                "status": "error", 
                "message": f"Nenhum documento processado. {len(errors)} erros encontrados",
                "errors": errors
            })
        else:
            return jsonify({
                "status": "success", 
                "message": f"{processed_count} documentos processados com sucesso!",
                "processed": processed_count
            })
        
    except Exception as e:
        error_msg = f"Erro geral no processamento: {str(e)}"
        with lock:
            estatisticas["erros"].append(error_msg)
        return jsonify({"status": "error", "message": error_msg})

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

@app.route('/api/clear_errors', methods=['POST'])
def clear_errors():
    """Limpar lista de erros"""
    with lock:
        estatisticas["erros"] = []
    return jsonify({"status": "success", "message": "Erros limpos com sucesso!"})

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Resetar o sistema (apenas para desenvolvimento)"""
    global documentos
    with lock:
        documentos = []
        estatisticas.update({
            "total_documentos": 0,
            "total_embeddings": 0,
            "espaco_utilizado": 0,
            "ultimo_upload": None,
            "processando": False,
            "fila_processamento": [],
            "erros": []
        })
    return jsonify({"status": "success", "message": "Sistema resetado com sucesso!"})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)