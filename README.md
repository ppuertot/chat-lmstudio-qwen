# 🤖 Chat con LM Studio - Interfaz Web (Modelo Fijo)

Una aplicación web moderna para chatear con el modelo **DeepSeek R1 0528 Qwen3 8B** usando LM Studio local.

## 📋 Características Principales

- ✅ **Modelo fijo**: DeepSeek R1 0528 Qwen3 8B (`deepseek/deepseek-r1-0528-qwen3-8b`)
- ✅ **Interfaz de chat moderna** con diseño oscuro tipo WhatsApp
- ✅ **Conexión automática** a LM Studio (puerto 1234)
- ✅ **Modo host** para Linux que no reconoce `host.docker.internal`
- ✅ **Uso directo** del campo `content` de la respuesta (ignora `reasoning_content`)

## 📋 Requisitos

1. **LM Studio instalado y ejecutando:**
   - Descarga LM Studio: https://lmstudio.ai
   - Abre LM Studio e inicia una IA Local Server
   - Carga el modelo `deepseek/deepseek-r1-0528-qwen3-8b` (Settings → Select Model Tab → Click 'Open')

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

Abre **http://localhost:5000** para chatear con DeepSeek R1 0528 Qwen3 8B.

## 🔧 Configuración Técnica

### Backend (`app.py`)

- **API URL:** `http://localhost:1234/v1/chat/completions`
- **Modelo por defecto:** `deepseek/deepseek-r1-0528-qwen3-8b` (fijo)
- **Endpoint:** `/chat` → Procesa mensajes de chat
- **Manejo de respuesta:** Usa directamente el campo `content` e ignora `reasoning_content`

### Frontend (`templates/index.html`)

- **Interfaz responsive** con diseño oscuro
- **Auto-resize** del textarea
- **Formateo Markdown** básico (negritas, cursivas, código)

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
├── static/                        # Assets estáticos (vacío)
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

**¡Disfruta chateando con DeepSeek R1 0528 Qwen3 8B!** 🚀

¿Necesitas ayuda? Revisa la documentación de LM Studio: https://lmstudio.ai/docs/