#!/usr/bin/env python3
import json, sys
from datetime import datetime

STATE_FILE = '/tmp/dunst-seen-ids'

# Ícones Nerd Font - consistentes com seu tema JetBrainsMono Nerd Font
ICONS = {
    'LOW':      '󰌵',   # nf-md-bell_outline
    'NORMAL':   '󰂚',   # nf-md-bell
    'CRITICAL': '󰂜',   # nf-md-bell_alert
}

# Classes CSS por urgência
CLASSES = {
    'LOW':      'low',
    'NORMAL':   'normal',
    'CRITICAL': 'critical',
}

data = json.load(sys.stdin)
notifs = data.get('data', [[]])[0]

# IDs atuais no histórico
current_ids = set(str(n.get('id', {}).get('data', '')) for n in notifs)

# IDs já vistos (lidos)
try:
    with open(STATE_FILE) as f:
        seen_ids = set(line.strip() for line in f if line.strip())
except:
    seen_ids = set()

new_ids = current_ids - seen_ids
new_count = len(new_ids)

lines = []
for n in notifs:
    nid     = str(n.get('id', {}).get('data', ''))
    app     = n.get('appname', {}).get('data', '?')
    summary = n.get('summary', {}).get('data', '?')
    body    = n.get('body', {}).get('data', '?')
    ts      = n.get('timestamp', {}).get('data', 0)
    dt      = datetime.fromtimestamp(ts / 1_000_000).strftime('%d/%m %H:%M')
    urgency = n.get('urgency', {}).get('data', 'NORMAL')

    icon    = ICONS.get(urgency, '󰂚')
    marker  = ' 󰄁' if nid in new_ids else ''      # nf-md-new_box

    # Formato limpo: ícone [data] app — summary: body
    lines.append(f"{icon} [{dt}] {app} — {summary}: {body}{marker}")

# Output Waybar JSON
text    = f"󰂞 {new_count}" if new_count > 0 else "󰂝"
tooltip = '\n'.join(lines) if lines else "Sem notificações"
cls     = "new" if new_count > 0 else "zero"

output = {
    "text": text,
    "tooltip": tooltip,
    "class": cls,
}

print(json.dumps(output))
