from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json

app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
SESSIONS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sessions.json")

def load_sessions():
    if os.path.exists(SESSIONS_FILE):
        with open(SESSIONS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_sessions(sessions):
    with open(SESSIONS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    return HTML

@app.route('/sessions', methods=['GET'])
def get_sessions():
    return jsonify(load_sessions())

@app.route('/sessions', methods=['POST'])
def post_session():
    data = request.json
    sessions = load_sessions()
    sid = data['id']
    sessions[sid] = data
    save_sessions(sessions)
    return jsonify({"ok": True})

@app.route('/sessions/<sid>', methods=['DELETE'])
def delete_session(sid):
    sessions = load_sessions()
    if sid in sessions:
        del sessions[sid]
        save_sessions(sessions)
    return jsonify({"ok": True})

@app.route('/check_key')
def check_key():
    return jsonify({"ok": bool(GROQ_API_KEY)})

@app.route('/analyze', methods=['POST'])
def analyze():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY no configurada."}), 500

    data = request.json
    image_b64 = data.get('image')
    image_mime = data.get('mime', 'image/jpeg')
    context = data.get('context', '')
    phase = data.get('phase', 'Reconocimiento')
    machine = data.get('machine', 'maquina desconocida')
    severity = data.get('severity', 'Informativo')

    prompt = ("Eres un experto en pentesting documentando una sesion de '" + machine + "'. "
              "Fase: " + phase + ". Severidad estimada: " + severity + ".\n" +
              (("Contexto: " + context + "\n") if context else "") +
              """
INSTRUCCIONES CRITICAS:
- Describe EXACTAMENTE lo que ves en la imagen. IPs reales, puertos reales, versiones reales, comandos reales.
- NO inventes datos. Si ves 172.17.0.2 escribe 172.17.0.2.
- Copia el comando exacto que aparece en pantalla.

Genera el informe con este formato:

FASE: """ + phase + """
SEVERIDAD: """ + severity + """
HERRAMIENTA / COMANDO: [comando exacto visible]
HALLAZGO: [IPs, puertos, versiones, servicios reales de la imagen]
ANALISIS TECNICO: [que significa lo que se ve y sus implicaciones de seguridad]
SIGUIENTE PASO SUGERIDO: [accion concreta basada en los hallazgos reales]""")

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": "Bearer " + GROQ_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "max_tokens": 1024,
                "messages": [{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": "data:" + image_mime + ";base64," + image_b64}},
                        {"type": "text", "text": prompt}
                    ]
                }]
            },
            timeout=60
        )
        result = response.json()
        print("\n--- GROQ ---")
        print("Status:", response.status_code)
        if "error" in result:
            print("Error:", result["error"])
            return jsonify({"error": result["error"]["message"]}), 500
        print(result["choices"][0]["message"]["content"][:200])
        print("------------\n")
        return jsonify({"analysis": result["choices"][0]["message"]["content"]})
    except requests.exceptions.Timeout:
        return jsonify({"error": "Timeout. Intentalo de nuevo."}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/summarize', methods=['POST'])
def summarize():
    if not GROQ_API_KEY:
        return jsonify({"error": "GROQ_API_KEY no configurada."}), 500
    data = request.json
    entries_text = data.get('entries_text', '')
    machine = data.get('machine', '')
    prompt = ("Eres un experto en ciberseguridad. Resume en un parrafo ejecutivo profesional la siguiente sesion de pentesting sobre '" +
              machine + "'.\n\nEntradas:\n" + entries_text +
              "\n\nEscribe un resumen ejecutivo de maximo 150 palabras destacando: vulnerabilidades encontradas, severidad general, vector de ataque principal y recomendacion clave. En español.")
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": "Bearer " + GROQ_API_KEY, "Content-Type": "application/json"},
            json={
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "max_tokens": 300,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=30
        )
        result = response.json()
        if "error" in result:
            return jsonify({"error": result["error"]["message"]}), 500
        return jsonify({"summary": result["choices"][0]["message"]["content"]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AXIOM Reporter · by Zafiro</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0f1117; color: #e0e0e0; min-height: 100vh; display: flex; }
.sidebar { width: 260px; min-width: 260px; background: #161b22; border-right: 1px solid #30363d; display: flex; flex-direction: column; height: 100vh; position: fixed; left: 0; top: 0; overflow-y: auto; }
.sidebar-logo { padding: 18px 16px 14px; display: flex; align-items: center; gap: 10px; border-bottom: 1px solid #30363d; }
.zlogo { width: 32px; height: 32px; background: #1e40af; border-radius: 7px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.sidebar-logo h1 { font-size: 15px; font-weight: 700; color: #f0f0f0; }
.sidebar-logo span { font-size: 11px; color: #8b949e; display: block; }
.sidebar-section { padding: 12px 16px 8px; font-size: 11px; color: #6e7681; text-transform: uppercase; letter-spacing: 0.05em; }
.new-session-btn { margin: 0 12px 12px; background: #1e40af; color: white; border: none; border-radius: 8px; padding: 9px 14px; font-size: 13px; font-weight: 500; cursor: pointer; width: calc(100% - 24px); text-align: left; display: flex; align-items: center; gap: 8px; transition: opacity 0.15s; }
.new-session-btn:hover { opacity: 0.85; }
.session-item { padding: 9px 12px; margin: 0 8px 4px; border-radius: 8px; cursor: pointer; transition: background 0.1s; display: flex; align-items: center; justify-content: space-between; gap: 6px; }
.session-item:hover { background: #21262d; }
.session-item.active { background: #1e40af20; border: 1px solid #1e40af40; }
.session-item-name { font-size: 13px; color: #c9d1d9; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; flex: 1; }
.session-item-meta { font-size: 11px; color: #6e7681; white-space: nowrap; }
.session-del { background: none; border: none; color: #6e7681; cursor: pointer; font-size: 14px; padding: 2px 4px; border-radius: 4px; opacity: 0; transition: opacity 0.15s; }
.session-item:hover .session-del { opacity: 1; }
.session-del:hover { color: #ff7b7b; }
.main { margin-left: 260px; flex: 1; display: flex; flex-direction: column; min-height: 100vh; }
.topbar { background: #161b22; border-bottom: 1px solid #30363d; padding: 12px 24px; display: flex; align-items: center; gap: 12px; }
.topbar h2 { font-size: 15px; font-weight: 600; color: #f0f0f0; flex: 1; }
.topbar .session-meta { font-size: 12px; color: #6e7681; }
.content { padding: 24px; max-width: 860px; }
.card { background: #161b22; border: 1px solid #30363d; border-radius: 12px; padding: 20px; margin-bottom: 20px; }
.card h3 { font-size: 14px; font-weight: 600; color: #c9d1d9; margin-bottom: 14px; }
input[type=text], textarea, select { background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; border-radius: 8px; padding: 8px 12px; font-size: 14px; font-family: inherit; outline: none; transition: border 0.15s; width: 100%; }
input[type=text]:focus, textarea:focus, select:focus { border-color: #1e40af; }
.btn { height: 36px; padding: 0 16px; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; font-weight: 500; transition: opacity 0.15s; display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }
.btn:hover { opacity: 0.85; }
.btn:disabled { opacity: 0.4; cursor: not-allowed; }
.btn-blue { background: #1e40af; color: white; }
.btn-outline { background: transparent; color: #8b949e; border: 1px solid #30363d; }
.btn-outline:hover { border-color: #8b949e; color: #c9d1d9; }
.btn-red { background: transparent; color: #ff7b7b; border: 1px solid #8b2020; }
.upload-zone { border: 2px dashed #30363d; border-radius: 10px; padding: 28px; text-align: center; cursor: pointer; transition: all 0.15s; margin-bottom: 14px; }
.upload-zone:hover { border-color: #1e40af; background: #1e40af08; }
.upload-zone.has-image { padding: 10px; border-color: #1e40af60; }
.upload-zone p { font-size: 14px; color: #8b949e; margin-top: 6px; }
.upload-zone small { font-size: 12px; color: #6e7681; }
#file-input { display: none; }
#preview { max-width: 100%; max-height: 220px; object-fit: contain; border-radius: 8px; display: none; }
.row2 { display: flex; gap: 10px; margin-bottom: 12px; }
.row2 textarea { flex: 1; resize: vertical; min-height: 70px; line-height: 1.5; }
.selects-col { display: flex; flex-direction: column; gap: 8px; min-width: 150px; }
.selects-col label { font-size: 11px; color: #6e7681; margin-bottom: 2px; display: block; }
select { height: 36px; }
.error-box { background: #3d1515; border: 1px solid #8b2020; color: #ff7b7b; padding: 10px 14px; border-radius: 8px; font-size: 13px; margin-bottom: 12px; display: none; }
.analyzing { display: none; align-items: center; gap: 10px; padding: 10px 14px; background: #1e40af10; border: 1px solid #1e40af30; border-radius: 8px; margin-bottom: 12px; font-size: 13px; color: #60a5fa; }
.spinner { width: 15px; height: 15px; border: 2px solid #1e40af40; border-top-color: #60a5fa; border-radius: 50%; animation: spin 0.7s linear infinite; flex-shrink: 0; }
@keyframes spin { to { transform: rotate(360deg); } }
.action-row { display: flex; gap: 8px; flex-wrap: wrap; }
.sep { border: none; border-top: 1px solid #21262d; margin: 20px 0; }
.entries-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }
.entries-header h3 { font-size: 14px; font-weight: 600; color: #c9d1d9; }
.export-btns { display: none; gap: 8px; flex-wrap: wrap; }
.summary-box { background: #0d1117; border: 1px solid #1e40af30; border-radius: 10px; padding: 16px; margin-bottom: 20px; display: none; }
.summary-box h4 { font-size: 13px; color: #60a5fa; margin-bottom: 8px; }
.summary-box p { font-size: 13px; line-height: 1.7; color: #c9d1d9; }
.entry-card { background: #0d1117; border: 1px solid #30363d; border-radius: 10px; padding: 16px; margin-bottom: 14px; }
.entry-top { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; flex-wrap: wrap; }
.entry-actions { margin-left: auto; display: flex; gap: 6px; }
.phase-badge { font-size: 11px; padding: 2px 10px; border-radius: 99px; font-weight: 600; }
.sev-badge { font-size: 11px; padding: 2px 10px; border-radius: 99px; font-weight: 600; }
.phase-Reconocimiento { background: #0d2a4a; color: #58a6ff; }
.phase-Enumeracion { background: #2a1f4a; color: #bc8cff; }
.phase-Explotacion { background: #4a1f0d; color: #ff9966; }
.phase-Post-explotacion { background: #1a3a1a; color: #56d364; }
.phase-Otro { background: #21262d; color: #8b949e; }
.sev-Critico { background: #4a0d0d; color: #ff4444; }
.sev-Alto { background: #4a2a0d; color: #ff9944; }
.sev-Medio { background: #3a3a0d; color: #ffdd44; }
.sev-Bajo { background: #0d3a1a; color: #44dd88; }
.sev-Informativo { background: #21262d; color: #8b949e; }
.entry-num { font-size: 11px; color: #6e7681; }
.entry-img { width: 100%; max-height: 180px; object-fit: contain; border-radius: 8px; border: 1px solid #30363d; margin-bottom: 10px; background: #161b22; }
.entry-notes { font-size: 12px; color: #6e7681; font-style: italic; margin-bottom: 8px; padding: 6px 10px; background: #161b22; border-radius: 6px; border-left: 2px solid #1e40af; }
.entry-analysis { font-size: 13px; line-height: 1.8; color: #c9d1d9; white-space: pre-wrap; background: #161b22; border: 1px solid #21262d; border-radius: 8px; padding: 12px; }
.entry-ts { font-size: 11px; color: #6e7681; margin-top: 8px; }
.edit-area { width: 100%; min-height: 120px; resize: vertical; font-size: 13px; line-height: 1.7; margin-top: 8px; }
.empty { text-align: center; padding: 40px; color: #6e7681; }
.welcome { display: flex; align-items: center; justify-content: center; height: 100vh; }
.welcome-inner { text-align: center; max-width: 360px; }
.welcome-inner h2 { font-size: 20px; font-weight: 600; color: #c9d1d9; margin-bottom: 8px; }
.welcome-inner p { font-size: 14px; color: #6e7681; margin-bottom: 20px; }
.modal-bg { display: none; position: fixed; inset: 0; background: rgba(0,0,0,0.7); z-index: 100; align-items: center; justify-content: center; }
.modal-bg.open { display: flex; }
.modal { background: #161b22; border: 1px solid #30363d; border-radius: 14px; padding: 24px; width: 100%; max-width: 420px; }
.modal h3 { font-size: 16px; font-weight: 600; margin-bottom: 16px; color: #f0f0f0; }
.modal input { margin-bottom: 14px; }
.modal-btns { display: flex; gap: 8px; justify-content: flex-end; }
</style>
</head>
<body>

<div class="sidebar">
  <div class="sidebar-logo">
    <div class="zlogo">
      <svg width="20" height="20" viewBox="0 0 22 22" fill="none">
        <polygon points="11,1 20,6 20,16 11,21 2,16 2,6" fill="none" stroke="white" stroke-width="1.5"/>
        <text x="11" y="15.5" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="11" fill="white">Z</text>
      </svg>
    </div>
    <div>
      <h1>AXIOM Reporter</h1>
      <span>by Zafiro</span>
    </div>
  </div>
  <div style="padding: 12px 8px 8px;">
    <button class="new-session-btn" onclick="openNewSessionModal()">+ Nueva sesion</button>
  </div>
  <div class="sidebar-section">Sesiones guardadas</div>
  <div id="session-list"></div>
</div>

<div class="main">
  <div id="welcome-screen" class="welcome">
    <div class="welcome-inner">
      <div style="font-size:48px; margin-bottom:16px;">⬡</div>
      <h2>Bienvenido, Zafiro</h2>
      <p>Crea una nueva sesion para comenzar a documentar tu pentest con IA.</p>
      <button class="btn btn-blue" onclick="openNewSessionModal()">+ Nueva sesion</button>
    </div>
  </div>

  <div id="session-screen" style="display:none;">
    <div class="topbar">
      <h2 id="topbar-title">—</h2>
      <span class="session-meta" id="topbar-meta"></span>
    </div>
    <div class="content">

      <div class="card">
        <h3>Nueva captura</h3>
        <div class="upload-zone" id="upload-zone"
          onclick="document.getElementById('file-input').click()"
          ondragover="event.preventDefault(); this.classList.add('has-image')"
          ondragleave="this.classList.remove('has-image')"
          ondrop="handleDrop(event)">
          <div style="font-size:28px;">📸</div>
          <p>Haz clic o arrastra una captura aqui</p>
          <small>PNG, JPG — max 10 MB</small>
        </div>
        <input type="file" id="file-input" accept="image/*" onchange="handleFile(event)" />
        <img id="preview" />

        <div class="row2">
          <textarea id="context" placeholder="Notas / contexto (opcional)&#10;Ej: nmap al target, puertos 22 y 80 abiertos"></textarea>
          <div class="selects-col">
            <div>
              <label>Fase</label>
              <select id="phase">
                <option value="Reconocimiento">Reconocimiento</option>
                <option value="Enumeracion">Enumeracion</option>
                <option value="Explotacion">Explotacion</option>
                <option value="Post-explotacion">Post-explotacion</option>
                <option value="Otro">Otro</option>
              </select>
            </div>
            <div>
              <label>Severidad</label>
              <select id="severity">
                <option value="Informativo">Informativo</option>
                <option value="Bajo">Bajo</option>
                <option value="Medio">Medio</option>
                <option value="Alto">Alto</option>
                <option value="Critico">Critico</option>
              </select>
            </div>
          </div>
        </div>

        <div class="error-box" id="error-box"></div>
        <div class="analyzing" id="analyzing">
          <div class="spinner"></div>
          <span>Analizando con LLaMA-4 Vision...</span>
        </div>

        <div class="action-row">
          <button class="btn btn-blue" id="analyze-btn" onclick="analyze()" disabled style="flex:1;">Analizar con IA</button>
        </div>
      </div>

      <hr class="sep">

      <div class="entries-header">
        <h3 id="entry-count">Informe (0 entradas)</h3>
        <div class="export-btns" id="export-btns">
          <button class="btn btn-outline" onclick="generateSummary()">Resumen IA</button>
          <button class="btn btn-outline" onclick="exportPDF()">Exportar PDF</button>
          <button class="btn btn-outline" onclick="exportMarkdown()">Obsidian (.md)</button>
        </div>
      </div>

      <div class="summary-box" id="summary-box">
        <h4>Resumen ejecutivo (generado por IA)</h4>
        <p id="summary-text"></p>
      </div>

      <div id="entries-list"></div>
    </div>
  </div>
</div>

<div class="modal-bg" id="new-session-modal">
  <div class="modal">
    <h3>Nueva sesion</h3>
    <input type="text" id="new-machine-name" placeholder="Nombre de la maquina (ej: Lame — HackTheBox)" />
    <div class="modal-btns">
      <button class="btn btn-outline" onclick="closeNewSessionModal()">Cancelar</button>
      <button class="btn btn-blue" onclick="createSession()">Crear</button>
    </div>
  </div>
</div>

<script>
var currentSessionId = null;
var sessions = {};
var imageBase64 = null;
var imageMime = 'image/jpeg';

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
}

function loadSessions() {
  fetch('/sessions')
    .then(function(r) { return r.json(); })
    .then(function(data) {
      sessions = data;
      renderSidebar();
      var ids = Object.keys(sessions);
      if (ids.length > 0) {
        openSession(ids[ids.length - 1]);
      }
    });
}

function saveCurrentSession() {
  if (!currentSessionId || !sessions[currentSessionId]) return;
  fetch('/sessions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(sessions[currentSessionId])
  });
}

function renderSidebar() {
  var list = document.getElementById('session-list');
  var ids = Object.keys(sessions);
  if (ids.length === 0) {
    list.innerHTML = '<div style="padding:8px 16px;font-size:12px;color:#6e7681;">Sin sesiones guardadas</div>';
    return;
  }
  var html = '';
  ids.slice().reverse().forEach(function(id) {
    var s = sessions[id];
    var active = id === currentSessionId ? ' active' : '';
    var count = (s.entries || []).length;
    html += '<div class="session-item' + active + '" onclick="openSession(\'' + id + '\')">';
    html += '<span class="session-item-name">' + s.machine + '</span>';
    html += '<span class="session-item-meta">' + count + ' entradas</span>';
    html += '<button class="session-del" onclick="event.stopPropagation(); deleteSession(\'' + id + '\')" title="Eliminar">✕</button>';
    html += '</div>';
  });
  list.innerHTML = html;
}

function openNewSessionModal() {
  document.getElementById('new-session-modal').classList.add('open');
  setTimeout(function() { document.getElementById('new-machine-name').focus(); }, 100);
}
function closeNewSessionModal() {
  document.getElementById('new-session-modal').classList.remove('open');
  document.getElementById('new-machine-name').value = '';
}

document.getElementById('new-machine-name').addEventListener('keydown', function(e) {
  if (e.key === 'Enter') createSession();
  if (e.key === 'Escape') closeNewSessionModal();
});

function createSession() {
  var name = document.getElementById('new-machine-name').value.trim();
  if (!name) return;
  var id = uid();
  sessions[id] = {
    id: id,
    machine: name,
    created: new Date().toLocaleString('es-ES'),
    entries: []
  };
  saveCurrentSession();
  fetch('/sessions', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(sessions[id])
  });
  closeNewSessionModal();
  renderSidebar();
  openSession(id);
}

function deleteSession(id) {
  if (!confirm('Eliminar sesion "' + sessions[id].machine + '"? Esta accion no se puede deshacer.')) return;
  delete sessions[id];
  fetch('/sessions/' + id, {method: 'DELETE'});
  if (currentSessionId === id) {
    currentSessionId = null;
    var ids = Object.keys(sessions);
    if (ids.length > 0) {
      openSession(ids[ids.length - 1]);
    } else {
      document.getElementById('welcome-screen').style.display = 'flex';
      document.getElementById('session-screen').style.display = 'none';
    }
  }
  renderSidebar();
}

function openSession(id) {
  currentSessionId = id;
  var s = sessions[id];
  document.getElementById('welcome-screen').style.display = 'none';
  document.getElementById('session-screen').style.display = 'block';
  document.getElementById('topbar-title').textContent = s.machine;
  document.getElementById('topbar-meta').textContent = 'Creada: ' + s.created;
  document.getElementById('summary-box').style.display = 'none';
  imageBase64 = null;
  document.getElementById('preview').style.display = 'none';
  document.getElementById('upload-zone').classList.remove('has-image');
  document.getElementById('analyze-btn').disabled = true;
  document.getElementById('context').value = '';
  renderSidebar();
  renderEntries();
}

function processFile(file) {
  if (!file) return;
  if (file.size > 10 * 1024 * 1024) { showError('La imagen supera los 10 MB.'); return; }
  imageMime = file.type || 'image/jpeg';
  var reader = new FileReader();
  reader.onload = function(ev) {
    imageBase64 = ev.target.result.split(',')[1];
    var prev = document.getElementById('preview');
    prev.src = ev.target.result;
    prev.style.display = 'block';
    document.getElementById('upload-zone').classList.add('has-image');
    document.getElementById('analyze-btn').disabled = false;
    hideError();
  };
  reader.readAsDataURL(file);
}
function handleFile(e) { processFile(e.target.files[0]); }
function handleDrop(e) { e.preventDefault(); processFile(e.dataTransfer.files[0]); }
function showError(msg) { var el = document.getElementById('error-box'); el.textContent = msg; el.style.display = 'block'; }
function hideError() { document.getElementById('error-box').style.display = 'none'; }

function analyze() {
  if (!imageBase64 || !currentSessionId) return;
  var context = document.getElementById('context').value.trim();
  var phase = document.getElementById('phase').value;
  var severity = document.getElementById('severity').value;
  var btn = document.getElementById('analyze-btn');
  btn.disabled = true;
  document.getElementById('analyzing').style.display = 'flex';
  hideError();

  var machine = sessions[currentSessionId].machine;

  fetch('/analyze', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({image: imageBase64, mime: imageMime, context: context, phase: phase, severity: severity, machine: machine})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { showError(data.error); btn.disabled = false; return; }
    var entry = {
      id: uid(),
      phase: phase,
      severity: severity,
      context: context,
      image: 'data:' + imageMime + ';base64,' + imageBase64,
      analysis: data.analysis,
      timestamp: new Date().toLocaleString('es-ES'),
      editing: false
    };
    sessions[currentSessionId].entries.unshift(entry);
    saveCurrentSession();
    renderEntries();
    renderSidebar();
    document.getElementById('context').value = '';
    document.getElementById('preview').style.display = 'none';
    document.getElementById('upload-zone').classList.remove('has-image');
    document.getElementById('file-input').value = '';
    imageBase64 = null;
    btn.disabled = true;
  })
  .catch(function(e) { showError('Error de conexion. Esta corriendo app.py?'); btn.disabled = false; })
  .finally(function() { document.getElementById('analyzing').style.display = 'none'; });
}

function deleteEntry(entryId) {
  if (!confirm('Eliminar esta entrada?')) return;
  var entries = sessions[currentSessionId].entries;
  sessions[currentSessionId].entries = entries.filter(function(e) { return e.id !== entryId; });
  saveCurrentSession();
  renderEntries();
  renderSidebar();
}

function startEdit(entryId) {
  var entries = sessions[currentSessionId].entries;
  for (var i = 0; i < entries.length; i++) {
    if (entries[i].id === entryId) { entries[i].editing = true; break; }
  }
  renderEntries();
}

function saveEdit(entryId) {
  var entries = sessions[currentSessionId].entries;
  for (var i = 0; i < entries.length; i++) {
    if (entries[i].id === entryId) {
      var textarea = document.getElementById('edit-' + entryId);
      if (textarea) entries[i].analysis = textarea.value;
      entries[i].editing = false;
      break;
    }
  }
  saveCurrentSession();
  renderEntries();
}

function cancelEdit(entryId) {
  var entries = sessions[currentSessionId].entries;
  for (var i = 0; i < entries.length; i++) {
    if (entries[i].id === entryId) { entries[i].editing = false; break; }
  }
  renderEntries();
}

function getBadgePhase(phase) {
  var map = {'Reconocimiento':'phase-Reconocimiento','Enumeracion':'phase-Enumeracion','Explotacion':'phase-Explotacion','Post-explotacion':'phase-Post-explotacion'};
  return map[phase] || 'phase-Otro';
}
function getBadgeSev(sev) {
  var map = {'Critico':'sev-Critico','Alto':'sev-Alto','Medio':'sev-Medio','Bajo':'sev-Bajo','Informativo':'sev-Informativo'};
  return map[sev] || 'sev-Informativo';
}

function renderEntries() {
  if (!currentSessionId) return;
  var entries = sessions[currentSessionId].entries || [];
  document.getElementById('entry-count').textContent = 'Informe (' + entries.length + ' entradas)';
  document.getElementById('export-btns').style.display = entries.length > 0 ? 'flex' : 'none';

  if (entries.length === 0) {
    document.getElementById('entries-list').innerHTML = '<div class="empty"><div style="font-size:36px;margin-bottom:10px;">📄</div><p>Sube tu primera captura para comenzar</p></div>';
    return;
  }

  var html = '';
  for (var i = 0; i < entries.length; i++) {
    var e = entries[i];
    html += '<div class="entry-card">';
    html += '<div class="entry-top">';
    html += '<span class="phase-badge ' + getBadgePhase(e.phase) + '">' + e.phase + '</span>';
    html += '<span class="sev-badge ' + getBadgeSev(e.severity) + '">' + (e.severity || 'Informativo') + '</span>';
    html += '<span class="entry-num">#' + (entries.length - i) + '</span>';
    html += '<div class="entry-actions">';
    if (!e.editing) {
      html += '<button class="btn btn-outline" style="height:28px;font-size:11px;" onclick="startEdit(\'' + e.id + '\')">Editar</button>';
    }
    html += '<button class="btn btn-red" style="height:28px;font-size:11px;" onclick="deleteEntry(\'' + e.id + '\')">Borrar</button>';
    html += '</div></div>';
    html += '<img src="' + e.image + '" class="entry-img" alt="Captura" />';
    if (e.context) html += '<div class="entry-notes">' + e.context + '</div>';
    if (e.editing) {
      html += '<textarea class="edit-area" id="edit-' + e.id + '">' + e.analysis + '</textarea>';
      html += '<div style="display:flex;gap:8px;margin-top:8px;">';
      html += '<button class="btn btn-blue" style="font-size:12px;" onclick="saveEdit(\'' + e.id + '\')">Guardar</button>';
      html += '<button class="btn btn-outline" style="font-size:12px;" onclick="cancelEdit(\'' + e.id + '\')">Cancelar</button>';
      html += '</div>';
    } else {
      html += '<div class="entry-analysis">' + e.analysis + '</div>';
    }
    html += '<div class="entry-ts">Hora: ' + e.timestamp + '</div>';
    html += '</div>';
  }
  document.getElementById('entries-list').innerHTML = html;
}

function generateSummary() {
  if (!currentSessionId) return;
  var entries = sessions[currentSessionId].entries || [];
  if (entries.length === 0) return;
  var text = '';
  for (var i = entries.length - 1; i >= 0; i--) {
    text += 'Entrada ' + (entries.length - i) + ' [' + entries[i].phase + ' - ' + (entries[i].severity||'Informativo') + ']:\n' + entries[i].analysis + '\n\n';
  }
  var box = document.getElementById('summary-box');
  var textEl = document.getElementById('summary-text');
  box.style.display = 'block';
  textEl.textContent = 'Generando resumen...';

  fetch('/summarize', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({entries_text: text, machine: sessions[currentSessionId].machine})
  })
  .then(function(r) { return r.json(); })
  .then(function(data) {
    if (data.error) { textEl.textContent = 'Error: ' + data.error; return; }
    textEl.textContent = data.summary;
    sessions[currentSessionId].summary = data.summary;
    saveCurrentSession();
  })
  .catch(function() { textEl.textContent = 'Error generando resumen.'; });
}

function exportPDF() {
  if (!currentSessionId) return;
  var s = sessions[currentSessionId];
  var entries = s.entries || [];
  var rows = '';
  for (var i = entries.length - 1; i >= 0; i--) {
    var e = entries[i];
    rows += '<div class="entry">';
    rows += '<div style="display:flex;gap:8px;margin-bottom:10px;">';
    rows += '<span class="phase phase-' + e.phase + '">' + e.phase + '</span>';
    rows += '<span class="sev sev-' + (e.severity||'Informativo') + '">' + (e.severity||'Informativo') + '</span>';
    rows += '</div>';
    rows += '<img src="' + e.image + '" />';
    if (e.context) rows += '<p class="ctx">' + e.context + '</p>';
    rows += '<pre>' + e.analysis + '</pre>';
    rows += '<div class="ts">Hora: ' + e.timestamp + '</div>';
    rows += '</div>';
  }
  var summary = s.summary ? '<div class="exec-summary"><h3>Resumen Ejecutivo</h3><p>' + s.summary + '</p></div>' : '';

  var html = '<!DOCTYPE html><html lang="es"><head><meta charset="UTF-8"><title>Informe ' + s.machine + '</title><style>';
  html += 'body{font-family:Arial,sans-serif;max-width:860px;margin:40px auto;color:#1a1a1a;padding:0 24px;}';
  html += '.header{display:flex;align-items:center;gap:14px;margin-bottom:8px;}';
  html += 'h1{font-size:22px;color:#1e40af;margin:0;}';
  html += '.by{font-size:12px;color:#6b7280;}';
  html += 'h2{font-size:18px;margin:16px 0 4px;}';
  html += '.meta{font-size:13px;color:#666;margin-bottom:16px;}';
  html += '.divider{border:none;border-top:2px solid #1e40af;margin:16px 0 24px;}';
  html += '.exec-summary{background:#eff6ff;border:1px solid #bfdbfe;border-radius:8px;padding:16px;margin-bottom:24px;}';
  html += '.exec-summary h3{font-size:14px;color:#1e40af;margin-bottom:8px;}';
  html += '.exec-summary p{font-size:13px;line-height:1.7;}';
  html += '.entry{border:1px solid #ddd;border-radius:8px;padding:20px;margin-bottom:24px;page-break-inside:avoid;}';
  html += '.phase{display:inline-block;font-size:11px;padding:2px 10px;border-radius:99px;font-weight:600;}';
  html += '.sev{display:inline-block;font-size:11px;padding:2px 10px;border-radius:99px;font-weight:600;margin-left:6px;}';
  html += '.phase-Reconocimiento{background:#dbeafe;color:#1e40af;}.phase-Enumeracion{background:#ede9fe;color:#5b21b6;}.phase-Explotacion{background:#fee2e2;color:#991b1b;}.phase-Post-explotacion{background:#dcfce7;color:#166534;}.phase-Otro{background:#f3f4f6;color:#374151;}';
  html += '.sev-Critico{background:#fee2e2;color:#991b1b;}.sev-Alto{background:#ffedd5;color:#9a3412;}.sev-Medio{background:#fef9c3;color:#854d0e;}.sev-Bajo{background:#dcfce7;color:#166534;}.sev-Informativo{background:#f3f4f6;color:#374151;}';
  html += 'img{max-width:100%;border-radius:6px;border:1px solid #e5e7eb;margin:10px 0;display:block;}';
  html += 'pre{white-space:pre-wrap;font-family:Arial,sans-serif;font-size:13px;line-height:1.8;background:#f9fafb;padding:14px;border-radius:6px;border:1px solid #e5e7eb;}';
  html += '.ctx{font-size:12px;color:#6b7280;font-style:italic;margin:6px 0;}';
  html += '.ts{font-size:11px;color:#9ca3af;margin-top:8px;}';
  html += '.footer{margin-top:40px;padding-top:16px;border-top:1px solid #e5e7eb;text-align:center;font-size:12px;color:#9ca3af;}';
  html += '@media print{.entry{page-break-inside:avoid;}}';
  html += '</style><script>window.onload=function(){window.print();}<\/script></head><body>';
  html += '<div class="header">';
  html += '<svg width="44" height="44" viewBox="0 0 44 44" fill="none"><polygon points="22,2 40,12 40,32 22,42 4,32 4,12" fill="#1e40af"/><text x="22" y="30" text-anchor="middle" font-family="Arial Black,Arial" font-weight="900" font-size="20" fill="white">Z</text></svg>';
  html += '<div><h1>AXIOM Reporter</h1><div class="by">by Zafiro</div></div></div>';
  html += '<h2>' + s.machine + '</h2>';
  html += '<div class="meta">Generado: ' + new Date().toLocaleString('es-ES') + ' &nbsp;·&nbsp; ' + entries.length + ' entradas</div>';
  html += '<hr class="divider">';
  html += summary;
  html += rows;
  html += '<div class="footer">AXIOM Reporter &nbsp;·&nbsp; <strong style="color:#1e40af;">by Zafiro</strong></div>';
  html += '</body></html>';

  var win = window.open('', '_blank');
  win.document.write(html);
  win.document.close();
}

function exportMarkdown() {
  if (!currentSessionId) return;
  var s = sessions[currentSessionId];
  var entries = s.entries || [];
  var now = new Date().toLocaleString('es-ES');
  var slug = s.machine.replace(/[^a-z0-9]/gi, '_');
  var md = '---\n';
  md += 'titulo: ' + s.machine + '\n';
  md += 'fecha: ' + now + '\n';
  md += 'autor: Zafiro\n';
  md += 'tipo: pentest\n';
  md += 'tags: [HTB, pentesting, AXIOM, Zafiro]\n';
  md += '---\n\n';
  md += '# ' + s.machine + '\n\n';
  md += '> **AXIOM Reporter** by Zafiro\n';
  md += '> ' + entries.length + ' entradas · ' + now + '\n\n';
  if (s.summary) {
    md += '## Resumen Ejecutivo\n\n' + s.summary + '\n\n';
  }
  md += '---\n\n';

  for (var i = entries.length - 1; i >= 0; i--) {
    var e = entries[i];
    var num = entries.length - i;
    md += '## Entrada ' + num + ' — ' + e.phase + ' | ' + (e.severity||'Informativo') + '\n\n';
    md += '**Fecha:** ' + e.timestamp + '\n\n';
    if (e.context) md += '**Notas:** ' + e.context + '\n\n';
    md += '![[' + slug + '_captura_' + num + '.png]]\n\n';
    md += e.analysis + '\n\n';
    md += '---\n\n';
  }

  md += '## Resumen de entradas\n\n';
  md += '| # | Fase | Severidad | Timestamp |\n';
  md += '|---|------|-----------|----------|\n';
  for (var j = entries.length - 1; j >= 0; j--) {
    var n = entries.length - j;
    md += '| ' + n + ' | ' + entries[j].phase + ' | ' + (entries[j].severity||'Informativo') + ' | ' + entries[j].timestamp + ' |\n';
  }

  var blob = new Blob([md], {type: 'text/markdown'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = slug + '.md';
  a.click();

  setTimeout(function() {
    for (var k = entries.length - 1; k >= 0; k--) {
      var num2 = entries.length - k;
      var parts = entries[k].image.split(',');
      var mime = parts[0].match(/:(.*?);/)[1];
      var binary = atob(parts[1]);
      var arr = new Uint8Array(binary.length);
      for (var x = 0; x < binary.length; x++) arr[x] = binary.charCodeAt(x);
      var imgBlob = new Blob([arr], {type: mime});
      var imgA = document.createElement('a');
      imgA.href = URL.createObjectURL(imgBlob);
      imgA.download = slug + '_captura_' + num2 + '.png';
      imgA.click();
    }
  }, 600);
}

loadSessions();
</script>
</body>
</html>"""

if __name__ == '__main__':
    import webbrowser
    print("\n  AXIOM Reporter — by Zafiro")
    print("  Abriendo en http://localhost:5000\n")
    if not GROQ_API_KEY:
        print("  ADVERTENCIA: GROQ_API_KEY no encontrada.")
        print("  Ejecuta en PowerShell:")
        print('  [System.Environment]::SetEnvironmentVariable("GROQ_API_KEY","TU_KEY","User")\n')
    webbrowser.open("http://localhost:5000")
    app.run(debug=False, port=5000)
