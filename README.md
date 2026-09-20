# 🤖 Chat con LM Studio - Interfaz Web

Una aplicación web moderna para chatear con modelos locales de LM Studio.

## 📋 Características Principales

- ✅ **Modelo configurable** por variable de entorno (por defecto `deepseek/deepseek-r1-0528-qwen3-8b`)
- ✅ **Idioma configurable** por variable de entorno (por defecto responde en español)
- ✅ **Interfaz de chat moderna** con diseño oscuro tipo WhatsApp
- ✅ **Conexión automática** a LM Studio (puerto 1234)
- ✅ **Modo host** para Linux que no reconoce `host.docker.internal`
- ✅ **Uso directo** del campo `content` de la respuesta (ignora `reasoning_content`)
- ✅ **Respuesta en streaming**: el texto se muestra conforme se va generando

## 📋 Requisitos

1. **LM Studio instalado y ejecutando:**
   - Descarga LM Studio: https://lmstudio.ai
   - Abre LM Studio e inicia una IA Local Server
   - Carga el modelo configurado (por defecto `deepseek/deepseek-r1-0528-qwen3-8b`) (Settings → Select Model Tab → Click 'Open')

## 🐳 Ejecución con Docker Compose (Recomendado)

### Opción A: Script de utilidad

```bash
cd chat-lmstudio
./docker/scripts.sh up
```

### Opción B: Comandos Docker directos

```bash
cd chat-lmstudio
docker compose -f docker/docker-compose.yml up -d --build
```

## 🌐 Acceso

Abre **http://localhost:5000** para chatear con tu modelo local.

## ⚙️ Configuración (variables de entorno)

| Variable | Por defecto | Descripción |
| --- | --- | --- |
| `LM_STUDIO_URL` | `http://localhost:1234/v1/chat/completions` | Endpoint de la API de LM Studio |
| `LM_STUDIO_MODEL` | `openai/gpt-oss-20b` | Modelo a usar (debe estar disponible/cargable en LM Studio) |
| `SYSTEM_PROMPT` | `Responde siempre en español.` | Instrucción de sistema; cambia el idioma/tono. Déjala vacía para no enviar instrucción |
| `TEMPERATURE` | `0.7` | Temperatura de muestreo. Cada modelo puede preferir otra (gpt-oss ~1.0) |
| `MAX_TOKENS` | `8192` | Máximo de tokens de la respuesta (incluye el razonamiento interno) |
| `LOAD_RETRY_SECONDS` | `300` | Tiempo máximo de reintento si el modelo se está cargando (JIT) |

Ejemplo en local:

```bash
LM_STUDIO_MODEL='qwen/qwen2.5-7b-instruct' SYSTEM_PROMPT='Reply in English.' TEMPERATURE=1.0 python app.py
```

En Docker, define estas variables en `docker/docker-compose.yml` (ya incluye las principales).

## 🔧 Configuración Técnica

### Backend (`app.py`)

- **API URL:** configurable con `LM_STUDIO_URL`
- **Modelo:** configurable con `LM_STUDIO_MODEL` (por defecto `openai/gpt-oss-20b`)
- **Endpoint:** `/chat` → Procesa mensajes de chat y responde con un stream SSE (`text/event-stream`)
- **Manejo de respuesta:** Emite cada token del campo `content` e ignora `reasoning_content`; termina con `data: [DONE]`
- **Carga bajo demanda:** si LM Studio está cargando el modelo (JIT), reintenta y emite eventos `status: loading` / `status: ready`

### Frontend (`templates/index.html`)

- **Interfaz responsive** con diseño oscuro
- **Layout:** título arriba, chat al medio y estado de conexión abajo
- **Auto-resize** del textarea
- **Formateo Markdown** completo (GFM) con `marked` + `DOMPurify` vendorizados en `static/`

### Docker (`docker/`)

- **Dockerfile:** Imagen Python 3.11-slim con Flask
- **docker-compose.yml:** Configuración con `network_mode: host`
- **scripts.sh:** Script de utilidad para comandos Docker

## 🐛 Solución de Problemas

### ❌ "No se pudo conectar con LM Studio"

**Verifica que LM Studio está ejecutando:**
1. Ve a la pestaña de servidor en LM Studio
2. Asegúrate de que no hay error rojo
3. Click en "Create server" si no aparece el ícono de servidor

**Modo GPU solo:**
- Si LM Studio está usando **"GPU only"** sin CPU, la API no funcionará
- Configura al menos un poco de memoria para la CPU en Settings → Server

**Puerto bloqueado:**
- Verifica que el puerto 1234 esté disponible
- `netstat -an | grep 1234` o revisa los "Connections" en la pestaña del servidor de LM Studio

### ❌ Respuesta con texto de razonamiento negro

Esto puede pasar si LM Studio está usando un formato experimental. El backend ya maneja esto automáticamente, pero puedes probar:

- **Desactivar el modelo de razonamiento** en LM Studio (Settings → Server)
- **Usar una versión diferente** del modelo que no active `reasoning_content` por defecto

### ❌ Modelo no encontrado (404)

El modelo debe estar **cargado** en memoria:
1. Ve a la pestaña **Modelos** en LM Studio
2. Selecciona el modelo `deepseek/deepseek-r1-0528-qwen3-8b`
3. Haz click en **"Open"**
4. Espera a que cargue completamente

## 📁 Estructura del Proyecto

```
chat-lmstudio/
├── app.py                          # Backend Flask con endpoint /chat
├── requirements.txt                # Dependencias Python
├── README.md                       # Esta documentación
├── static/                        # Assets estáticos (marked.min.js, purify.min.js)
└── templates/
    └── index.html                  # Interfaz frontend
└── docker/
    ├── Dockerfile                  # Imagen del contenedor
    ├── docker-compose.yml          # Configuración principal
    ├── scripts.sh                  # Script de utilidad para comandos
    └── .dockerignore               # Archivos a ignorar en el build
```

## 📦 Dependencias

- **Flask** - Framework web Python
- **requests** - Cliente HTTP para conectar con LM Studio

## 🌐 API

La app se conecta a la API nativa de LM Studio:

```
POST http://localhost:1234/v1/chat/completions
Content-Type: application/json

{
    "model": "deepseek/deepseek-r1-0528-qwen3-8b",
    "messages": [
        {"role": "user", "content": "Hola"}
    ],
    "stream": false,
    "temperature": 0.7,
    "max_tokens": 512
}
```

## 📝 Notas sobre el Modelo

El modelo **deepseek/deepseek-r1-0528-qwen3-8b** de LM Studio puede devolver un campo especial llamado `reasoning_content` con su proceso de pensamiento. El backend usa directamente el campo `content` e ignora `reasoning_content`.

## 🔒 Seguridad

- La app solo corre localmente (localhost)
- No expone puertos al exterior por defecto
- Puedes cambiar `host='0.0.0.0'` a `host='127.0.0.1'` si quieres limitarlo solo a localhost

## 📄 Licencia

Este proyecto es de código abierto y libre de usar.

---

**¡Disfruta chateando con tu modelo local!** 🚀

¿Necesitas ayuda? Revisa la documentación de LM Studio: https://lmstudio.ai/docs/