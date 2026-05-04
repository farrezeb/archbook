import json, sys
from datetime import datetime

STATE_FILE = '/tmp/dunst-seen-ids'

data = json.load(sys.stdin)
notifs = data.get('data', [[]])[0]

# IDs atuais no histórico
current_ids = set(str(n.get('id', {}).get('data', '')) for n in notifs)

# IDs já vistos (lidos)
try:
    with open(STATE_FILE) as f:
        seen_ids = set(f.read().strip().splitlines())
except:
    seen_ids = set()

new_ids = current_ids - seen_ids
new = len(new_ids)

lines = []
for n in notifs:
    nid     = str(n.get('id', {}).get('data', ''))
    app     = n.get('appname', {}).get('data', '?')
    summary = n.get('summary', {}).get('data', '?')
    body    = n.get('body', {}).get('data', '?')
    ts      = n.get('timestamp', {}).get('data', 0)
    dt      = datetime.fromtimestamp(ts / 1_000_000).strftime('%d/%m %H:%M')
    urgency = n.get('urgency', {}).get('data', '')
    icon    = {'LOW': '🔵', 'NORMAL': '🟡', 'CRITICAL': '🔴'}.get(urgency, '⚪')
    marker  = ' 🆕' if nid in new_ids else ''
    lines.append(icon + ' [' + dt + '] ' + app + ' — ' + summary + ': ' + body + marker)

text    = ('󰂞 ' + str(new)) if new > 0 else '󰂝 ✓'
tooltip = '\\n'.join(lines) if lines else 'Sem notificações'
cls     = 'new' if new > 0 else 'zero'
print('{"text": "' + text + '", "tooltip": "' + tooltip + '", "class": "' + cls + '"}')
