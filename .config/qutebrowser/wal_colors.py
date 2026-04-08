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
