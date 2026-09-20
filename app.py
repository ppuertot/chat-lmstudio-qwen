from flask import Flask, render_template, request, jsonify, Response
import requests
import json
import os
import time

app = Flask(__name__)

# =============================================================================
# Configuración del servidor de chat LM Studio
# =============================================================================
# API de LM Studio (por defecto corre en el puerto 1234)
LM_STUDIO_URL = os.environ.get(
    "LM_STUDIO_URL",
    "http://localhost:1234/v1/chat/completions"
)

# Modelo a usar (configurable con la variable de entorno LM_STUDIO_MODEL)
MODEL_NAME = os.environ.get(
    "LM_STUDIO_MODEL",
    "deepseek/deepseek-r1-0528-qwen3-8b"
)

# Instrucción de sistema (idioma/tono). Por defecto responde en español.
# Se puede cambiar con la variable de entorno SYSTEM_PROMPT.
SYSTEM_PROMPT = os.environ.get(
    "SYSTEM_PROMPT",
    "Responde siempre en español."
)

# Temperatura de muestreo (configurable con TEMPERATURE). Cada modelo puede
# preferir un valor distinto: p. ej. gpt-oss rinde mejor cerca de 1.0.
TEMPERATURE = float(os.environ.get("TEMPERATURE", "0.7"))

# Máximo de tokens de la respuesta (configurable con MAX_TOKENS). Debe ser
# amplio porque el razonamiento interno también consume este presupuesto.
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "4096"))

# Si el modelo aún se está cargando (JIT de LM Studio), reintentar hasta
# LOAD_RETRY_SECONDS antes de devolver error.
LOAD_RETRY_SECONDS = int(os.environ.get("LOAD_RETRY_SECONDS", "300"))
LOAD_RETRY_INTERVAL = 5


@app.route('/')
def index():
    return render_template('index.html', model=MODEL_NAME)


def _sse(obj):
    """Formatea un objeto como evento Server-Sent Events."""
    return f"data: {json.dumps(obj, ensure_ascii=False)}\n\n"


def _stream_response(payload):
    """Genera los fragmentos de texto que devuelve LM Studio en modo streaming."""
    deadline = time.time() + LOAD_RETRY_SECONDS

    # Si el modelo no está cargado y LM Studio usa carga JIT, la primera
    # petición devuelve 400 mientras carga. Reintentamos hasta el deadline.
    while True:
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json=payload,
                stream=True,
                timeout=300
            )
        except requests.exceptions.ConnectionError:
            yield _sse({'error': 'No se pudo conectar con LM Studio.\n\nAsegúrate de que:\n1. LM Studio está ejecutando una IA Local Server\n2. La API esté en http://localhost:1234'})
            return
        except requests.exceptions.Timeout:
            yield _sse({'error': 'La solicitud tomó demasiado tiempo.'})
            return
        except Exception as e:
            yield _sse({'error': f'Error inesperado: {str(e)}'})
            return

        if response.status_code == 400:
            body = response.text.lower()
            if ('load model' in body or 'loading' in body) and time.time() < deadline:
                response.close()
                yield _sse({'status': 'loading', 'message': 'Cargando el modelo en LM Studio, espera…'})
                time.sleep(LOAD_RETRY_INTERVAL)
                continue
        break

    if response.status_code != 200:
        error_text = response.text
        if response.status_code == 404:
            error = 'Modelo no encontrado.\n\nAPI call failed with status 404.'
        elif response.status_code == 429:
            error = 'LM Studio está muy ocupado.\n\nAPI call failed with status 429.'
        else:
            error = f'Error conectando con LM Studio (estado {response.status_code})'
        yield _sse({'error': error, 'raw_error': error_text[:500]})
        return

    # Avisar de que el modelo ya está listo y comienza la generación
    yield _sse({'status': 'ready'})

    # LM Studio envía líneas "data: {...}" con el delta de cada token.
    # Decodificamos siempre como UTF-8 (no confiar en el charset anunciado,
    # porque si falta requests asume ISO-8859-1 y corrompe los acentos).
    # Usamos solo delta.content (ignoramos reasoning_content).
    try:
        for raw_line in response.iter_lines():
            if not raw_line:
                continue
            line = raw_line.decode('utf-8', errors='replace')
            if line.startswith('data:'):
                line = line[5:].strip()
            if line == '[DONE]':
                break
            try:
                chunk = json.loads(line)
            except json.JSONDecodeError:
                continue
            delta = chunk.get('choices', [{}])[0].get('delta', {})
            content = delta.get('content') or ''
            if content:
                yield _sse({'delta': content})
    except requests.exceptions.RequestException as e:
        yield _sse({'error': f'Se interrumpió la conexión con LM Studio: {str(e)}'})
        return

    yield 'data: [DONE]\n\n'


@app.route('/chat', methods=['POST'])
def chat():
    """
    Procesa el mensaje del usuario y lo envía a LM Studio en modo streaming.

    Usa siempre el modelo configurado (no hay selector de modelos).
    Espera un JSON con: { "message": "..." } y responde con eventos SSE.
    """
    data = request.json

    message = data.get('message', '').strip()

    if not message:
        return jsonify({'error': 'No hay mensaje para procesar'}), 400

    messages = []
    if SYSTEM_PROMPT.strip():
        messages.append({"role": "system", "content": SYSTEM_PROMPT})
    messages.append({"role": "user", "content": message})

    payload = {
        "model": MODEL_NAME,
        "messages": messages,
        "stream": True,
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS
    }

    return Response(
        _stream_response(payload),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no'
        }
    )


if __name__ == '__main__':
    print("=" * 60)
    print("  Chat con LM Studio - Interfaz Web")
    print("=" * 60)
    print(f"Abriendo http://localhost:5000...")
    print()
    print("Configuración:")
    print(f"  • Modelo: {MODEL_NAME}")
    print(f"  • API de LM Studio: {LM_STUDIO_URL}")
    print(f"  • Instrucción de sistema: {SYSTEM_PROMPT!r}")
    print(f"  • Temperatura: {TEMPERATURE} | Max tokens: {MAX_TOKENS}")
    print("  • Escuchando en: http://localhost:5000")
    print()
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)