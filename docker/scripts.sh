#!/bin/bash

# ==============================================================================
#  Script de utilidad para el Chat con LM Studio - Docker (Modo Host)
# ==============================================================================
# Uso: ./scripts.sh <comando> [opciones]
# 
# Comandos disponibles:
#   up         - Iniciar el contenedor con network_mode: host
#   down       - Detener y limpiar todo
#   restart    - Reiniciar el contenedor
#   logs       - Ver los logs del contenedor
#   stop       - Detener el contenedor
#   start      - Iniciar el contenedor detenido
# ==============================================================================

CONTAINER_NAME="lmstudio-chat-web"
COMPOSE_FILE="../docker/docker-compose.yml"

cd "$(dirname "$0")/.." || exit 1

case "$1" in
  up)
    echo "🐳 Iniciando Chat LM Studio en MODO HOST..."
    echo ""
    echo "ℹ️  Configuración:"
    echo "   • network_mode: host (para acceder a LM Studio vía localhost)"
    echo "   • API de LM Studio: http://localhost:1234"
    echo ""
    docker compose -f "$COMPOSE_FILE" up -d --build
    echo ""
    echo "✅ Contenedor iniciado!"
    echo ""
    echo "ℹ️  La aplicación estará disponible en:"
    echo "   http://localhost:5000"
    echo ""
    ;;
    
  down)
    echo "📦 Deteniendo y limpiando el contenedor..."
    docker compose -f "$COMPOSE_FILE" down
    echo "✅ Limpio completado."
    ;;
    
  restart)
    echo "🔄 Reiniciando el contenedor..."
    docker compose -f "$COMPOSE_FILE" restart
    echo "✅ Contenedor reiniciado."
    ;;
    
  logs)
    LOGS_LINES="${2:-100}"
    echo "📋 Últimas $LOGS_LINES líneas de los logs:"
    docker compose -f "$COMPOSE_FILE" logs --tail="$LOGS_LINES"
    if [ "$LOGS_LINES" = "follow" ]; then
      docker compose -f "$COMPOSE_FILE" logs -f
    fi
    ;;
    
  stop)
    echo "⏸️  Deteniendo el contenedor..."
    docker compose -f "$COMPOSE_FILE" stop
    echo "✅ Contenedor detenido."
    ;;
    
  start)
    echo "▶️  Iniciando el contenedor..."
    docker compose -f "$COMPOSE_FILE" start
    echo "✅ Contenedor iniciado."
    ;;
  
  status)
    echo "📊 Estado del contenedor:"
    docker ps --filter "name=$CONTAINER_NAME"
    if [ $? -ne 0 ]; then
      echo "ℹ️  El contenedor no está corriendo."
    else
      docker compose -f "$COMPOSE_FILE" logs --tail=10
    fi
    ;;
    
  shell)
    echo "🔓 Acceso al shell del contenedor..."
    docker exec -it $CONTAINER_NAME bash
    ;;

  help|--help|-h)
    cat << 'EOF'
💻 Chat LM Studio - Docker (Modo Host)

Uso: ./scripts.sh <comando> [opciones]

Comandos disponibles:
  up              Iniciar el contenedor con network_mode: host
  down            Detener y limpiar todo
  restart         Reiniciar el contenedor
  stop            Detener el contenedor sin borrarlo
  start           Iniciar el contenedor detenido
  logs [N/follow] Ver N líneas de logs (o 'follow' para modo tiempo real)
  status          Mostrar estado del contenedor y últimos logs
  shell           Abrir shell del contenedor

⚙️ Configuración:
   • network_mode: host - Permite acceso a localhost de LM Studio
   • API LM Studio: http://localhost:1234/v1/chat/completions
   
ℹ️ Por qué usar network_mode: host:
   Algunos sistemas de Linux no reconocen 'host.docker.internal'
   y prefieren conectar directamente a 127.0.0.1 o localhost.

💡 Instrucciones rápidas:

# Primera vez - Construir e iniciar
./scripts.sh up

# Detener todo
./scripts.sh down

# Ver últimos 50 logs
./scripts.sh logs 50

# Seguir logs en tiempo real
./scripts.sh logs follow

# Reiniciar
./scripts.sh restart
EOF
    ;;
  
  *)
    echo "❓ Comando no válido. Usa './scripts.sh help' para ver el menú de comandos."
    exit 1
    ;;
esac
