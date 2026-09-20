from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime

app = Flask(__name__)

# =============================================================================
# Configuración del servidor de chat LM Studio
# =============================================================================
# URL de la API de LM Studio (por defecto corre en el puerto 1234)
# Modelos disponibles en LM Studio: Settings → Select Model Tab
LM_STUDIO_URL = "http://localhost:1234/v1/chat/completions"

# Nombre del modelo por defecto si no se especifica uno
DEFAULT_MODEL_NAME = 'qwen/qwen3.5-9b'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/models')
def get_models():
    """
    Obtiene los modelos cargados en LM Studio.
    Retorna: {"status": "online", "url": "...", "models": [{"id": "...", "display_name": "..."}], "count": N}
    """
    try:
        # Obtener la lista de modelos cargados de LM Studio
        models_response = requests.get(f"{LM_STUDIO_URL}/models", timeout=30)
        
        if models_response.status_code == 200:
            models_data = models_response.json().get('data', [])
            
            # Construir lista de modelos con nombres legibles
            models_list = []
            for model in models_data:
                model_id = model.get('id', '')
                display_name = model_id
                
                # Obtener el nombre amigable del ID (ej: "qwen/qwen3.5-9b" -> "Qwen 3.5 9B")
                parts = model_id.split('/')
                if len(parts) >= 2:
                    owner = parts[0]
                    name = parts[1]
                    display_name = f"{name.replace('-', ' ').replace('_', ' ').title()}" if '/' not in name else display_name
                
                models_list.append({
                    'id': model_id,
                    'display_name': display_name
                })
            
            return jsonify({
                'status': 'online',
                'url': LM_STUDIO_URL,
                'models': models_list,
                'count': len(models_list)
            })
        else:
            return jsonify({'status': 'error', 'error': f'LM Studio no responde correctamente'}), 500
    except requests.exceptions.ConnectionError:
        return jsonify({
            'status': 'offline',
            'error': 'LM Studio no está ejecutando una IA Local Server'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'error': str(e)})


@app.route('/chat', methods=['POST'])
def chat():
    """
    Procesa el mensaje del usuario y lo envía a LM Studio.
    Espera un JSON con: { "message": "...", "model": "..." }
    """
    data = request.json
    
    message = data.get('message', '').strip()
    model = data.get('model', DEFAULT_MODEL_NAME)
    
    if not message:
        return jsonify({'error': 'No hay mensaje para procesar'}), 400
    
    payload = {
        "model": model,
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
            # Manejar ambos formatos: content (estándar) y reasoning_content (modelos Qwen con reasoning)
            message_obj = result.get('choices', [{}])[0].get('message', {})
            ai_message = message_obj.get('content', '') or message_obj.get('reasoning_content', '')
            
            return jsonify({
                'success': True,
                'reply': ai_message,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        else:
            error_text = response.text
            if response.status_code == 404:
                return jsonify({
                    'error': f'Modelo no encontrado. Verifica que el modelo esté cargado en LM Studio.\n\nAPI call failed with status {response.status_code}.',
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
            'error': 'No se pudo conectar con LM Studio.\n\nAsegúrate de que:\n1. LM Studio está ejecutando una IA Local Server\n2. No estás usando "GPU only" mode (debe tener habilitada la CPU también)\n3. La API esté en http://localhost:1234',
            'status': 0,
            'raw_error': 'Connection refused'
        })
    except requests.exceptions.Timeout:
        return jsonify({
            'error': 'La solicitud tomó demasiado tiempo.\n\nPodría ser que el modelo sea muy lento o tenga problemas de memoria.',
            'status': 408
        })
    except Exception as e:
        return jsonify({
            'error': f'Error inesperado: {str(e)}',
            'status': 500
        })


if __name__ == '__main__':
    print("=" * 60)
    print("  Chat con LM Studio - Interfaz Web")
    print("=" * 60)
    print("Abriendo http://localhost:5000...")
    print()
    print("Configuración:")
    print(f"  • API de LM Studio: {LM_STUDIO_URL}")
    print("  • Escuchando en: http://localhost:5000")
    print()
    print("Para usar modelos diferentes, ve a:")
    print("  Settings > Select Model Tab > Click 'Open' next to your model")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)