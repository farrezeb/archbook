#!/bin/bash
########################################
# POWER MANAGER - MacBook A1278
# Modo servidor CRM (EspoCRM)
# AC: nunca suspende, tela apaga apenas
# BAT: suspende normalmente
########################################

POWER_SUPPLY="/sys/class/power_supply/ADP1/online"
LID_STATE="/proc/acpi/button/lid/LID0/state"
LOG_ENABLED=true
HYPR_USER="farrezeb"
HYPR_UID=1000

# Inicializar com estado atual para evitar ação na startup
LAST_LID=""

log() {
    [ "$LOG_ENABLED" = true ] && logger -t power-manager "$1" && echo "[$(date '+%H:%M:%S')] $1"
}

is_on_ac() {
    [ -f "$POWER_SUPPLY" ] && [ "$(cat "$POWER_SUPPLY" 2>/dev/null)" = "1" ]
}

is_lid_closed() {
    [ -f "$LID_STATE" ] && grep -q "closed" "$LID_STATE" 2>/dev/null
}

hypr_sig() {
    find /run/user/${HYPR_UID}/hypr/ -maxdepth 1 -mindepth 1 -type d 2>/dev/null \
        | xargs basename 2>/dev/null \
        | head -1
}

dpms_off() {
    local sig
    sig=$(hypr_sig)
    [ -z "$sig" ] && log "dpms_off: sem assinatura Hyprland, ignorando" && return
    log "DPMS: apagando tela"
    sudo -u "$HYPR_USER" \
        XDG_RUNTIME_DIR="/run/user/${HYPR_UID}" \
        HYPRLAND_INSTANCE_SIGNATURE="$sig" \
        /usr/bin/hyprctl dispatch dpms off 2>/dev/null
}

dpms_on() {
    local sig
    sig=$(hypr_sig)
    [ -z "$sig" ] && log "dpms_on: sem assinatura Hyprland, ignorando" && return
    log "DPMS: ligando tela"
    sudo -u "$HYPR_USER" \
        XDG_RUNTIME_DIR="/run/user/${HYPR_UID}" \
        HYPRLAND_INSTANCE_SIGNATURE="$sig" \
        /usr/bin/hyprctl dispatch dpms on 2>/dev/null
}

lid_action() {
    if [ "$1" = "closed" ]; then
        if is_on_ac; then
            log "Tampa fechada + AC: servidor mode, só apaga tela"
            dpms_off
        else
            log "Tampa fechada + Bateria: suspendendo"
            systemctl suspend
        fi
    else
        log "Tampa aberta: ligando tela"
        dpms_on
        pkill -USR1 swayidle 2>/dev/null
    fi
}

create_configs() {
    # BATERIA: dim → suspend (sem lock)
    cat > /run/swayidle_bat.conf << 'EOF'
timeout 90  '/usr/bin/brightnessctl -s set 10%' resume '/usr/bin/brightnessctl -r'
timeout 110 '/usr/local/bin/lockscreen'
timeout 150 '/usr/bin/systemctl suspend'
EOF

    # AC / SERVIDOR - caminho absoluto para hyprctl
    cat > /run/swayidle_ac.conf << 'EOF'
timeout 400 '/usr/local/bin/lockscreen'
timeout 600 '/usr/bin/hyprctl dispatch dpms off' resume '/usr/bin/hyprctl dispatch dpms on'
EOF
}

switch_profile() {
    pkill -9 swayidle 2>/dev/null
    sleep 0.3

    local sig
    sig=$(hypr_sig)

    if [ -z "$sig" ]; then
        log "switch_profile: Hyprland ainda não disponível, abortando swayidle"
        return
    fi

    if is_on_ac; then
        log "Perfil AC: idle 10min apaga tela, nunca suspende"
        sudo -u "$HYPR_USER" \
            XDG_RUNTIME_DIR="/run/user/${HYPR_UID}" \
            WAYLAND_DISPLAY="wayland-1" \
            HYPRLAND_INSTANCE_SIGNATURE="$sig" \
            /usr/bin/swayidle -w -C /run/swayidle_ac.conf >/dev/null 2>&1 &
    else
        log "Perfil Bateria: dim 90s → suspend 150s"
        sudo -u "$HYPR_USER" \
            XDG_RUNTIME_DIR="/run/user/${HYPR_UID}" \
            WAYLAND_DISPLAY="wayland-1" \
            HYPRLAND_INSTANCE_SIGNATURE="$sig" \
            /usr/bin/swayidle -w -C /run/swayidle_bat.conf >/dev/null 2>&1 &
    fi
}

check_lid() {
    local current
    is_lid_closed && current="closed" || current="open"

    # Na primeira execução, apenas registra sem executar ação
    if [ -z "$LAST_LID" ]; then
        LAST_LID="$current"
        log "Estado inicial da tampa: $current (sem ação)"
        return
    fi

    if [ "$current" != "$LAST_LID" ]; then
        LAST_LID="$current"
        lid_action "$current"
    fi
}

# Aguarda Hyprland iniciar (máx 60s)
wait_hyprland() {
    local tries=0
    log "Aguardando Hyprland..."
    while [ $tries -lt 60 ]; do
        local sig
        sig=$(hypr_sig)
        if [ -n "$sig" ] && [ -S "/run/user/${HYPR_UID}/hypr/${sig}/.socket.sock" ]; then
            log "Hyprland pronto: $sig"
            return 0
        fi
        sleep 1
        tries=$((tries + 1))
    done
    log "AVISO: Hyprland não detectado após 60s, continuando mesmo assim"
    return 1
}

# Função separada para monitorar apenas o lid
monitor_lid() {
    while true; do
        sleep 2
        check_lid
    done
}

# ── Main ───────────────────────────────────────────────────────────────────────
log "=== Power Manager iniciando (servidor CRM) ==="
wait_hyprland
create_configs
switch_profile

# Inicializa LAST_LID antes de começar monitoramento
is_lid_closed && LAST_LID="closed" || LAST_LID="open"
log "Estado inicial definido: $LAST_LID"

# Separar os loops de monitoramento (evita concorrência no pipe)
monitor_lid &

log "Monitorando eventos de energia..."
udevadm monitor --subsystem-match=power_supply --property | while IFS= read -r line; do
    if echo "$line" | grep -q "POWER_SUPPLY_ONLINE="; then
        sleep 0.3
        log "Evento AC detectado"
        switch_profile
        # Não chama check_lid aqui para evitar duplicidade
    fi
done
