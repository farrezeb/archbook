#!/bin/bash
########################################################################################
# RANDOM WALLPAPER - Edição Dinâmica (Waybar + Dunst + Fuzzel + SWWW Random)
########################################################################################

export SWWW_SOCK="$XDG_RUNTIME_DIR/awww.socket"

# Pega assinatura do Hyprland silenciosamente
export HYPRLAND_INSTANCE_SIGNATURE=""
if [ -d "/tmp/hypr" ]; then
    export HYPRLAND_INSTANCE_SIGNATURE=$(ls -t /tmp/hypr 2>/dev/null | head -n 1 || true)
fi

# Se vazia, não imprime aviso e continua (swww/hyprctl lidam com vazio)
if [ -z "$HYPRLAND_INSTANCE_SIGNATURE" ]; then
    true  # placeholder silencioso - não faz nada
fi

export PATH="$PATH:/usr/local/bin" # Garante wal e swww

# Evita rodar se mudou muito recentemente
#ULTIMO_WALLPAPER="$HOME/.cache/ultimo_wallpaper.txt"
#if [ -f "$ULTIMO_WALLPAPER" ]; then
#    LAST_CHANGE=$(stat -c %Y "$ULTIMO_WALLPAPER")
#    NOW=$(date +%s)
#    if [ $((NOW - LAST_CHANGE)) -lt 600 ]; then   # 600 segundos = 10 minutos
#        echo "Wallpaper mudou recentemente. Saindo sem trocar."
#        exit 0
#    fi
#fi

# Verifica dependências básicas
command -v awww >/dev/null 2>&1 || { notify-send "Erro" "swww não instalado"; exit 1; }
command -v wal >/dev/null 2>&1 || { notify-send "Erro" "pywal não instalado"; exit 1; }

WALLPAPER_DIR="/usr/share/meus_wallpapers"

# 1. Escolhe a imagem
PAPEIS_PAREDE=$(find "$WALLPAPER_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" -o -iname "*.webp" \) 2>/dev/null)
if [ -z "$PAPEIS_PAREDE" ]; then
    notify-send "Erro" "Nenhum wallpaper encontrado em $WALLPAPER_DIR" -u critical
    exit 1
fi

ESCOLHIDO=$(echo "$PAPEIS_PAREDE" | shuf -n 1)

# --- Lógica de Transição Aleatória ---
TRANSITIONS=("fade" "left" "right" "top" "bottom" "wipe" "wave" "grow" "center" "any")
RANDOM_TRANSITION=${TRANSITIONS[$RANDOM % ${#TRANSITIONS[@]}]}

# 2. Aplica o wallpaper com swww
if ! pgrep -x awww-daemon > /dev/null; then
    awww-daemon > /dev/null 2>&1 &
    sleep 2
fi

awww img "$ESCOLHIDO" \
    --transition-type "$RANDOM_TRANSITION" \
    --transition-fps 60 \
    --transition-duration 1.5 \
    --transition-bezier .43,1.19,1,.4 2>/dev/null

NOME_IMG=$(basename "$ESCOLHIDO")
notify-send "Wallpaper ($RANDOM_TRANSITION)" "Aplicado: $NOME_IMG" -i "$ESCOLHIDO" -t 3000

# Cache para evitar reprocessamento desnecessário
if [ "$1" != "--force" ] && [ -f "$ULTIMO_WALLPAPER" ] && [ "$(cat "$ULTIMO_WALLPAPER")" = "$ESCOLHIDO" ]; then
    echo "Mesmo wallpaper detectado. Saindo..."
    exit 0
fi

echo "$ESCOLHIDO" > "$ULTIMO_WALLPAPER"

# 3. Gera as cores com Pywal
wal -i "$ESCOLHIDO" -q -a 100 2>/dev/null
sleep 0.3

# 3.5. Atualiza arquivo de cores do Qutebrowser
cat > ~/.config/qutebrowser/wal_colors.py << EOF
# Arquivo gerado automaticamente - NÃO EDITE MANUALMENTE
import os

def get_wal_colors():
    cache_colors = os.path.expanduser('~/.cache/wal/colors')
    if os.path.exists(cache_colors):
        with open(cache_colors) as f:
            lines = [line.strip() for line in f.readlines()]
            return {
                'bg': lines[0] if len(lines) > 0 else '#000000',
                'fg': lines[7] if len(lines) > 7 else '#ffffff',
                'c1': lines[1] if len(lines) > 1 else '#ff0000',
                'c4': lines[4] if len(lines) > 4 else '#0000ff',
                'c15': lines[15] if len(lines) > 15 else '#ffffff',
            }
    return {
        'bg': '#000000',
        'fg': '#ffffff',
        'c1': '#ff0000',
        'c4': '#0000ff',
        'c15': '#ffffff',
    }

colors = get_wal_colors()
EOF

# 4. Atualização de Configurações
if [ -f ~/.cache/wal/colors.sh ]; then
    source ~/.cache/wal/colors.sh

    # 4.1. Atualiza Dunst
    mkdir -p ~/.config/dunst
   cat > ~/.config/dunst/dunstrc << EOF
[global]
   monitor = 0
   follow = mouse
   width = (250, 500)
   height = (0, 750)
   offset = (17, 26)
   padding = 8
   horizontal_padding = 10
   gap_size = 5
   transparency = 20
   frame_width = 1
   font = JetBrains Mono 10
   corner_radius = 10
   min_icon_size = 32
   max_icon_size = 64
   format = "<b>%s</b>\n%b"
   progress_bar = true
   progress_bar_height = 8

[urgency_low]
   background = "${background}"
   foreground = "${foreground}"
   frame_color = "${color2}"
   timeout = 3

[urgency_normal]
   background = "${background}"
   foreground = "${foreground}"
   frame_color = "${color4}"
   timeout = 5

[urgency_critical]
   background = "${background}"
   foreground = "${color1}"
   frame_color = "${color1}"
   timeout = 0
EOF

    # 4.2. Atualiza Fuzzel
    mkdir -p ~/.config/fuzzel
    bg_clean="${background#\#}"
    fg_clean="${foreground#\#}"
    c1_clean="${color1#\#}"
    c4_clean="${color4#\#}"
    cat > ~/.config/fuzzel/fuzzel.ini << EOF
[main]
terminal=foot
layer=overlay
width=40
horizontal-pad=20
vertical-pad=10
inner-pad=10
font=JetBrainsMono Nerd Font:size=11

[colors]
background=${bg_clean}dd
text=${fg_clean}ff
match=${c1_clean}ff
selection=${c4_clean}dd
selection-text=${bg_clean}ff
selection-match=${c1_clean}ff
border=${c1_clean}ff

[border]
width=2
radius=10

[dmenu]
exit-immediately-if-empty=no
EOF

    # 4.3. Atualiza Cores do Hyprland de forma atômica
    c1=$(echo "$color1" | sed 's/#//g')
    c2=$(echo "$color2" | sed 's/#//g')
    cat > ~/.cache/wal/colors-hyprland.tmp << EOF
\$background = rgba(${bg_clean}ff)
\$foreground = rgba(${fg_clean}ff)
\$color0 = 0xff${c1}
\$color1 = 0xff${c1}
\$color2 = 0xff${c2}
\$color3 = 0xff$(echo "$color3" | sed 's/#//g')
\$color4 = 0xff$(echo "$color4" | sed 's/#//g')
\$color5 = 0xff$(echo "$color5" | sed 's/#//g')
\$color6 = 0xff$(echo "$color6" | sed 's/#//g')
\$color7 = 0xff$(echo "$color7" | sed 's/#//g')
EOF
    mv ~/.cache/wal/colors-hyprland.tmp ~/.cache/wal/colors-hyprland.conf
    hyprctl reload

    # 4.4. Reinicia o Dunst
    if pgrep -x dunst > /dev/null; then
        killall dunst 2>/dev/null
        sleep 0.2
        dunst > /dev/null 2>&1 &
    fi
fi

# Sincroniza as cores do Pywal com todos os terminais Foot abertos (silencioso)
if [ -f ~/.cache/wal/sequences ]; then
    seq_file=$(cat ~/.cache/wal/sequences)
    for t in /dev/pts/*; do
        if [[ "$t" =~ ^/dev/pts/[0-9]+$ ]] && [ -w "$t" ]; then
            printf %b "$seq_file" > "$t" 2>/dev/null &
        fi
    done
fi

# Avisa o foot para reler as configurações
killall -USR1 foot 2>/dev/null

killall -SIGUSR2 waybar 2>/dev/null || true
# Ou só pkill -x waybar && waybar &

# Faz o qutebrowser reler a configuração sem fechar
pkill -USR1 qutebrowser

exit 0
