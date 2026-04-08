#!/bin/bash
cd ~/espocrm-docker

case "$1" in
    start|up)
        echo "🚀 Iniciando EspoCRM..."
        docker compose up -d
        sleep 5
        echo "✅ EspoCRM disponível em http://localhost:8080"
        ;;
    stop|down)
        echo "🛑 Parando EspoCRM..."
        docker compose down
        ;;
    restart)
        echo "🔄 Reiniciando EspoCRM..."
        docker compose restart
        ;;
    status)
        docker compose ps
        ;;
    logs)
        docker compose logs -f
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status|logs}"
        exit 1
        ;;
esac
