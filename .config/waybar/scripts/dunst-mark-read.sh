#!/usr/bin/env bash
# Salva os IDs atuais como "lidos"
dunstctl history | python3 -c "
import json, sys
data = json.load(sys.stdin)
notifs = data.get('data', [[]])[0]
for n in notifs:
    print(n.get('id', {}).get('data', ''))
" > /tmp/dunst-seen-ids

pkill -RTMIN+1 waybar
