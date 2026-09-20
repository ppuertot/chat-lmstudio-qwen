# 🤖 Chat con LM Studio - Interfaz Web

Una aplicación web moderna para chatear con modelos de IA locales cargados en LM Studio.

## 📋 Características

- ✅ Conectado a la API nativa de LM Studio (puerto 1234)
- ✅ Interfaz de chat moderna y responsiva
- ✅ Selector de modelos local (llama, mistral, phi, gpt4all, etc.)
- ✅ Indicador de estado en tiempo real
- ✅ Diseño oscuro agradable a la vista
- ✅ Soporte para mensajes largos con scroll automático

## 🐳 Docker (Recomendado) - Modo Host

### Opción A: Usar el script de utilidad

```bash
cd chat-lmstudio
./docker/scripts.sh up  # Construye e inicia automáticamente
```

El contenedor se conecta a LM Studio en `http://host.docker.internal:1234`.

### Opción B: Comandos Docker directos

```bash
cd chat-lmstudio

# Primera vez: construir la imagen
docker build -f docker/Dockerfile -t lmstudio-chat-web ./docker/

# Iniciar el contenedor
docker run -d \
  --name lmstudio-chat-web \
  -p 5000:5000 \
  -e LM_STUDIO_URL="http://host.docker.internal:1234/v1/chat/completions" \
  --network lmstudio-net \
  lmstudio-chat-web
```

### Opción C: Usar docker-compose (Recomendado)

```bash
cd chat-lmstudio
# Construir e iniciar con una sola línea
docker compose -f docker/docker-compose.yml up -d --build
```

Para detener y limpiar:
```bash
docker compose -f docker/docker-compose.yml down
```

### Ver logs

```bash
# Últimos 100 líneas
docker compose -f docker/docker-compose.yml logs --tail=100

# Seguir logs en tiempo real
docker compose -f docker/docker-compose.yml logs -f

# Detener y reiniciar
docker compose -f docker/docker-compose.yml restart
```

## 🚀 Instalación (Sin Docker)

---

### 1. Instalar LM Studio y cargar un modelo

1. Descarga LM Studio desde: https://lmstudio.ai
2. Abre LM Studio e inicia una **IA Local Server**:
   - Click en el ícono de servidor en la barra lateral
   - Configura las opciones (por defecto funciona bien)
   - Click en **"Create server"**
   
3. Carga un modelo:
   - Ve a **Modelos** → haz scroll y selecciona uno
   - Click en **"Open"** para cargarlo
   - Verifica que aparezca en la lista de modelos cargados

### 2. Instalar dependencias Python

```bash
cd chat-lmstudio
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
python app.py
```

La interfaz web abrirá automáticamente en **http://localhost:5000**

## 🎯 Configuración de Modelos

Por defecto, la app usa modelos comunes, pero puedes cambiarlos en el selector lateral izquierdo o editar los modelos disponibles en el archivo `templates/index.html` (busca la sección `defaultOptions`).

Modelos recomendados para empezar:
- **quen3.5-9b** - ✅ Modelo predeterminado (excellent reasoning)
- **llama-2-13b-chat-hf** - Excelente razonamiento general
- **mistral-7b-instruct-v0.2** - Rápido y eficiente
- **gpt4all-j** - Ligero y compatible con hardware modesto
- **phi-3-mini** - Moderno de Microsoft, buen rendimiento

## 🔧 Configuración Avanzada

### Cambiar puerto de API de LM Studio

Por defecto, LM Studio usa el puerto 1234. Si usas otro:

1. En LM Studio: Settings → Server Tab → cambia **Port**
2. Edita `chat-lmstudio/app.py` y actualiza la línea:
   ```python
   LM_STUDIO_URL = "http://localhost:YOUR_PORT/v1/chat/completions"
   ```

### Cambiar puerto de la app web

En `app.py`, cambia:
```python
app.run(host='0.0.0.0', port=5000, debug=True)
```

### Streaming de respuestas (en tiempo real)

Actualmente las respuestas se muestran al final. Para verlas aparecer en tiempo real, descomenta la configuración de streaming en `app.py` y actualiza el frontend.

## 🐛 Solución de Problemas

### ❌ "No se pudo conectar con LM Studio"

#### Problemas en Docker

**Windows/macOS:** Asegúrate de usar `host.docker.internal` como IP del host:
```yaml
# docker/docker-compose.yml debería tener:
- environment:
    - LM_STUDIO_URL=http://host.docker.internal:1234/v1/chat/completions
```

**Linux:** Algunas distribuciones usan `host-gateway` o `localhost`:
```yaml
# Opcional: para Linux que no reconoce host.docker.internal
- environment:
    - LM_STUDIO_URL=http://host-gateway:1234/v1/chat/completions
```

**Para probar si LM Studio funciona:**
Abre esta URL desde el navegador de tu PC:
- `http://localhost:1234/v1/models` - Verifica que LM Studio está respondiendo
- Si funciona, configura la API para usar el puerto correcto (si no es 1234)

#### Problemas generales

1. **Verifica que LM Studio está ejecutando:**
   - Ve a la pestaña de servidor en LM Studio
   - Asegúrate de que no hay error rojo
   - Click en "Create server" si no aparece el ícono de servidor

2. **Modo GPU solo:**
   - Si LM Studio está usando **"GPU only"** sin CPU, la API no funcionará
   - Configura al menos un poco de memoria para la CPU en Settings → Server

3. **Puerto bloqueado:**
   - Verifica que el puerto 1234 esté disponible
   - `netstat -an | grep 1234` o revisa los "Connections" en la pestaña del servidor de LM Studio

### ❌ Modelo no encontrado (404)

El modelo debe estar **cargado** en memoria:
1. Ve a la pestaña **Modelos** en LM Studio
2. Selecciona tu modelo y haz click en **"Open"**
3. Espera a que cargue completamente (puede tardar unos minutos)
4. Verifica que aparezca en la lista con estado "Cargado"

### ❌ Error 429 (Too Many Requests)

LM Studio está muy ocupado:
- Reduce el número de tokens en `app.py`: `max_tokens`
- Usa un modelo más pequeño
- Espera unos segundos entre mensajes

## 📁 Estructura del Proyecto

```
chat-lmstudio/
├── app.py              # Backend Flask (conecta con API de LM Studio)
├── requirements.txt    # Dependencias Python
├── templates/
│   └── index.html     # Interfaz frontend
└── README.md          # Esta documentación
```

## 🎨 Personalización

### Cambiar colores en `templates/index.html`

En la sección `<style>`, edita las variables CSS:
- `--bg-primary`: Color de fondo principal
- `--bg-message-user`: Color de mensajes del usuario
- `--bg-message-ai`: Color de respuestas de IA
- etc.

### Agregar nuevos modelos al selector

Edita la lista `defaultOptions` en el `<script>`:
```javascript
const defaultOptions = [
    { value: 'nuevo-modelo', text: 'Nombre del modelo' },
    // ... otros modelos
];
```

## 📦 Dependencias

- **Flask** - Framework web Python
- **requests** - Cliente HTTP para conectar con LM Studio
- **python-socketio** - Para funcionalidades en tiempo real (opcional)
- **eventlet** - Manejo de conexiones asíncronas

## 🌐 API de LM Studio

La app se conecta a la API estándar de LM Studio:

```
http://localhost:1234/v1/chat/completions
```

Esta es la misma API que usan otras aplicaciones como Ollama-webui o LangChain.

## 🔒 Seguridad

- La app solo corre localmente (localhost)
- No expone puertos al exterior por defecto
- Puedes cambiar `host='0.0.0.0'` a `host='127.0.0.1'` si quieres limitarlo solo a localhost

## 💡 Ideas para Mejorar

- [ ] Habilitar streaming de respuestas en tiempo real
- [ ] Añadir historial de chat persistente (SQLite)
- [ ] Soporte para archivos adjuntos (subir PDFs, imágenes)
- [ ] Opción para borrar el historial del chat
- [ ] Modo oscuro/claro intercambiable
- [ ] Exportar conversaciones a texto

## 📄 Licencia

Este proyecto es de código abierto y libre de usar.

---

**¡Disfruta chateando con tu IA local!** 🚀

¿Necesitas ayuda? Revisa la documentación de LM Studio: https://lmstudio.ai/docs/

## 🔧 Script de utilidad Docker (scripts.sh)

Ubicado en `docker/scripts.sh` - Facilita la gestión del contenedor:

```bash
# Construir imagen
docker/scripts.sh build

# Iniciar automáticamente
docker/scripts.sh up

# Iniciar en modo desarrollo (auto-reinicio con cambios)
docker/scripts.sh updev

# Ver logs
docker/scripts.sh logs 50      # Últimos 50 líneas
docker/scripts.sh logs follow  # Seguir en tiempo real

# Reiniciar
docker/scripts.sh restart

# Detener y limpiar todo
docker/scripts.sh down
```

Uso: `docker/scripts.sh <comando> [opciones]`
