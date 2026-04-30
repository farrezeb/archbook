#!/bin/bash
CACHE_FILE="/tmp/updates-count"
ICON="software-update-available"

if ! ping -c 1 archlinux.org &>/dev/null; then
    exit 0
fi

OFFICIAL=$(checkupdates 2>/dev/null | wc -l)
AUR=$(yay -Qua 2>/dev/null | wc -l)
TOTAL=$((OFFICIAL + AUR))

if [ "$TOTAL" -eq 0 ]; then
    rm -f "$CACHE_FILE"
    exit 0
fi

CACHED=$(cat "$CACHE_FILE" 2>/dev/null)
if [ "$CACHED" = "$TOTAL" ]; then
    exit 0
fi

echo "$TOTAL" > "$CACHE_FILE"

notify-send \
    --icon="$ICON" \
    --urgency=normal \
    --expire-time=10000 \
    "📦 $TOTAL atualizações disponíveis" \
    "Oficiais: $OFFICIAL | AUR: $AUR\nExecute 'topgrade' no terminal"
