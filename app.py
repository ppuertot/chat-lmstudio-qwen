from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# =============================================================================
# Configuración del servidor de chat LM Studio
# =============================================================================
# API de LM Studio (por defecto corre en el puerto 1234)
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Modelo predeterminado fijo: qwen/qwen3.5-9b
DEFAULT_MODEL_NAME = 'qwen/qwen3.5-9b'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/chat', methods=['POST'])
def chat():
    """
    Procesa el mensaje del usuario y lo envía a LM Studio.
    
    Usa siempre el modelo qwen/qwen3.5-9b (no hay selector de modelos).
    Espera un JSON con: { "message": "..." }
    """
    data = request.json
    
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'error': 'No hay mensaje para procesar'}), 400
    
    payload = {
        "model": DEFAULT_MODEL_NAME,  # Siempre usar qwen/qwen3.5-9b
        "messages": [
            {"role": "user", "content": message}
        ],
        "stream": False,
        "temperature": 0.7,
        "max_tokens": 512
    }
    
    try:
        response = requests.post(
            LM_STUDIO_URL, 
            json=payload,
            timeout=300
        )
        
        if response.status_code == 200:
            result = response.json()
            # Extraer solo el contenido real, ignorando reasoning_content si está presente
            message_obj = result.get('choices', [{}])[0].get('message', {})
            content = message_obj.get('content', '')
            reasoning_content = message_obj.get('reasoning_content', '')
            
            # Si hay razonamiento, extraer solo el contenido real (primer campo)
            if reasoning_content and content:
                ai_message = content
            else:
                ai_message = reasoning_content or content
            
            return jsonify({
                'success': True,
                'reply': ai_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            error_text = response.text
            if response.status_code == 404:
                return jsonify({
                    'error': f'Modelo no encontrado.\n\nAPI call failed with status {response.status_code}.',
                    'status': response.status_code,
                    'raw_error': error_text[:200]
                })
            elif response.status_code == 429:
                return jsonify({
                    'error': f'LM Studio está muy ocupado.\n\nAPI call failed with status {response.status_code}.',
                    'status': response.status_code,
                    'raw_error': error_text[:200]
                })
            else:
                return jsonify({
                    'error': f'Error conectando con LM Studio (estado {response.status_code})',
                    'status': response.status_code,
                    'raw_error': error_text[:500]
                })
                
    except requests.exceptions.ConnectionError:
        return jsonify({
            'error': 'No se pudo conectar con LM Studio.\n\nAsegúrate de que:\n1. LM Studio está ejecutando una IA Local Server\n2. La API esté en http://localhost:1234',
            'status': 0,
            'raw_error': 'Connection refused'
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'La solicitud tomó demasiado tiempo.',
            'status': 408
        })
    except Exception as e:
        return jsonify({
            'error': f'Error inesperado: {str(e)}',
            'status': 500
        })


if __name__ == '__main__':
    print("=" * 60)
    print("  Chat con LM Studio - Interfaz Web (Modelo Fijo)")
    print("=" * 60)
    print(f"Abriendo http://localhost:5000...")
    print()
    print("Configuración:")
    print(f"  • Modelo: {DEFAULT_MODEL_NAME} (fijo)")
    print(f"  • API de LM Studio: {LM_STUDIO_URL}")
    print("  • Escuchando en: http://localhost:5000")
    print()
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)