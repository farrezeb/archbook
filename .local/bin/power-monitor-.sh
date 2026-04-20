 #!/bin/bash
########################################################################################
# POWER MANAGER - MacBook A1278 (macOS-style)
# Event-driven power management usando udev (0% CPU idle, resposta instantânea)
########################################################################################
POWER_SUPPLY="/sys/class/power_supply/ADP1/online"
LOG_ENABLED=false  # Mude para true se quiser ver logs
log() {
    if [ "$LOG_ENABLED" = true ]; then
        logger -t power-manager "$1"
        echo "[$(date '+%H:%M:%S')] $1"
    fi
}
# Criar configurações do swayidle
create_configs() {
    # Bateria: Agressivo (economia)
    cat > /tmp/swayidle_bat.conf << 'EOF'
timeout 120 'brightnessctl -s set 10%' resume 'brightnessctl -r'
timeout 180 '/usr/local/bin/lockscreen'
timeout 240 'systemctl suspend'
before-sleep '/usr/local/bin/lockscreen'
EOF
    # AC: Relaxado (conveniência)
    cat > /tmp/swayidle_ac.conf << 'EOF'
timeout 600 'brightnessctl -s set 10%' resume 'brightnessctl -r'
timeout 900 '/usr/local/bin/lockscreen'
#timeout 1200 'systemctl suspend'
before-sleep '/usr/local/bin/lockscreen'
EOF
}
# Trocar perfil de energia
switch_profile() {
    local state=$(cat "$POWER_SUPPLY" 2>/dev/null || echo "1")
    # Matar swayidle anterior
    pkill -9 swayidle 2>/dev/null
    sleep 0.5
    if [ "$state" = "1" ]; then
        log "Power adapter connected - Using AC profile"
        swayidle -w -C /tmp/swayidle_ac.conf >/dev/null 2>&1 &
    else
        log "On battery power - Using Battery profile"
        swayidle -w -C /tmp/swayidle_bat.conf >/dev/null 2>&1 &
    fi
}
# Inicialização
log "Power Manager starting..."
create_configs
switch_profile
# Monitorar eventos de power_supply via udev (estilo macOS/IOKit)
# CPU: 0% quando idle, resposta instantânea quando há mudança
log "Monitoring power events (event-driven)..."
udevadm monitor --subsystem-match=power_supply --property | \
    while IFS= read -r line; do
        # Detecta mudança no AC adapter
        if echo "$line" | grep -q "POWER_SUPPLY_ONLINE="; then
            sleep 0.2  # Debounce (evita múltiplas trocas)
            switch_profile
        fi
    done
