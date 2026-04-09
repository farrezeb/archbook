# ============================================================================
# QUTEBROWSER - CLEAN & STABLE CONFIG (Fernando Edition)
# ============================================================================

config.load_autoconfig(False)

# ============================================================================
# PYWAL COLOR INTEGRATION
# ============================================================================

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from wal_colors import colors as wal
    bg = wal['bg']
    fg = wal['fg']
    c1 = wal['c1']
    c4 = wal['c4']
    c15 = wal['c15']
except ImportError:
    bg, fg, c1, c4, c15 = '#000000', '#ffffff', '#ff0000', '#0000ff', '#ffffff'

# --- Webpage Dark Mode ---
c.colors.webpage.darkmode.enabled = True
c.colors.webpage.darkmode.policy.images = 'smart'

# --- Statusbar ---
c.colors.statusbar.normal.bg = bg
c.colors.statusbar.normal.fg = c15
c.colors.statusbar.url.success.https.fg = c1

# --- Completion ---
c.colors.completion.even.bg = bg
c.colors.completion.odd.bg = bg
c.colors.completion.match.fg = c1
c.colors.completion.item.selected.bg = c4
c.colors.completion.item.selected.fg = fg
c.colors.completion.item.selected.match.fg = c1

# TEXTO PRINCIPAL DA COMPLETION
c.colors.completion.fg = c4
c.colors.completion.category.fg = c15
c.colors.completion.category.bg = bg

# SELEÇÃO COM HOVER/MOUSE
c.colors.completion.item.selected.bg = bg
c.colors.completion.item.selected.fg = fg
c.colors.completion.item.selected.match.fg = c1

# BORDA DA SELEÇÃO (destaque visual)
c.colors.completion.item.selected.border.top = c1
c.colors.completion.item.selected.border.bottom = c1
c.colors.completion.scrollbar.fg = c4
c.colors.completion.scrollbar.bg = bg

# --- Tabs ---
c.colors.tabs.even.bg = bg
c.colors.tabs.odd.bg = bg
c.colors.tabs.selected.even.bg = c4
c.colors.tabs.selected.odd.bg = c4


# ============================================================================
# ENGINE / PERFORMANCE
# ============================================================================

c.qt.args = [
    # Wayland nativo (Hyprland)
    '--enable-features=UseOzonePlatform',
    '--ozone-platform=wayland',

    # Estabilidade Intel HD 4000
    '--ignore-gpu-blocklist',

    # GPU equilibrada (não mata aceleração)
    '--enable-gpu-rasterization',
    '--enable-zero-copy',

    # Economia de RAM
    '--process-per-site-instance',

    # Limitar caches absurdos
    '--disk-cache-size=52428800',
    '--media-cache-size=52428800',

    # Limita processos renderer (bom em 4-8 GB RAM)
    '--renderer-process-limit=3',

    # Pra decode de vídeo melhor (se não estiver full)
    '--enable-features=VaapiVideoDecoder,VaapiIgnoreDriverChecks',
    '--use-gl=egl',
]

# ============================================================================
# PRIVACY / COMPATIBILIDADE
# ============================================================================

c.content.blocking.method = 'both'
c.content.javascript.enabled = True
c.content.cookies.accept = 'all'
c.content.webgl = True
c.content.canvas_reading = True

config.set('content.blocking.enabled', False, '*://*.youtube.com/*')
config.set('content.blocking.enabled', False, '*://*.youtu.be/*')

# ============ PASS (Password Store) ============

config.bind('<Alt-Shift-u>', 'spawn --userscript qute-pass-menu', mode='insert')
config.bind('pw', 'spawn --userscript qute-pass-menu', mode='normal')
config.bind('<Ctrl-Shift-p>', 'spawn --userscript qute-pass-menu', mode='normal')

# ============================================================================
# DOWNLOADS
# ============================================================================

c.downloads.location.directory = '~/dl'
c.downloads.position = 'bottom'
c.downloads.remove_finished = 5000

# ============================================================================
# EDITOR / FILE PICKER
# ============================================================================

c.editor.command = ['foot', '-e', 'micro', '{file}']
c.fileselect.handler = 'external'
c.fileselect.single_file.command = ['foot', '-e', 'lf', '-selection-path', '{}']
c.fileselect.multiple_files.command = ['foot', '-e', 'lf', '-selection-path', '{}']
c.fileselect.folder.command = ['foot', '-e', 'lf', '-selection-path', '{}']

# ============================================================================
# INTERFACE (Chrome-like)
# ============================================================================

c.statusbar.show = 'always'
c.tabs.show = 'multiple'
c.tabs.position = 'top'
c.tabs.background = True
c.tabs.last_close = 'close'
c.tabs.select_on_remove = 'last-used'

c.tabs.padding = {
    'top': 5,
    'bottom': 5,
    'left': 9,
    'right': 9
}

c.tabs.title.format = "{audio}{current_title}"

# ============================================================================
# SCROLL / INPUT
# ============================================================================

c.scrolling.bar = 'never'
#c.scrolling.smooth = False

c.input.insert_mode.auto_load = True
c.input.insert_mode.auto_leave = True

# ============================================================================
# SEARCH ENGINES
# ============================================================================

c.url.default_page = 'about:blank'
c.url.start_pages = ['about:blank']
c.url.searchengines = {
    'DEFAULT': 'https://duckduckgo.com/?q={}',
    'g': 'https://google.com/search?q={}',
    'yt': 'https://youtube.com/results?search_query={}',
    'gh': 'https://github.com/search?q={}',
    'aw': 'https://wiki.archlinux.org/?search={}',
}

# Completion mais útil
c.completion.height = '30%'
c.completion.shrink = True

# Statusbar mais limpa (remove elementos desnecessários)
c.statusbar.widgets = ['keypress', 'url', 'scroll', 'history', 'tabs', 'progress']

# ============================================================================
# FONTS
# ============================================================================

c.fonts.default_family = 'JetBrainsMono Nerd Font'
c.fonts.default_size = '11pt'
c.fonts.web.family.standard = 'SF Pro Display'
c.fonts.web.family.sans_serif = 'SF Pro Display'
c.fonts.web.family.fixed = 'JetBrainsMono Nerd Font'
c.fonts.web.size.default = 16

# ============================================================================
# ZOOM
# ============================================================================

c.zoom.default = '100%'

# ============================================================================
# KEYBINDS ESSENCIAIS
# ============================================================================

# Navegação de histórico
config.bind('H', 'back')
config.bind('L', 'forward')

# Navegação de tabs
config.bind('J', 'tab-prev')
config.bind('K', 'tab-next')

# SCROLL - adicionar explicitamente
config.bind('j', 'scroll down')
config.bind('k', 'scroll up')
config.bind('gg', 'scroll-to-perc 0')
config.bind('G', 'scroll-to-perc 100')
config.bind('Ctrl+d', 'scroll-page 0.5')
config.bind('Ctrl+u', 'scroll-page -0.5')

# Interface
config.bind('xb', 'config-cycle statusbar.show always never')
config.bind('xt', 'config-cycle tabs.show always never')
config.bind(',d', 'config-cycle colors.webpage.darkmode.enabled true false')
config.bind('tt', 'open -t https://translate.google.com/translate?sl=auto&tl=pt&u={url}')
config.bind('<Ctrl+Shift+r>', 'config-source')
