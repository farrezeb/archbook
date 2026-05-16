#!/bin/zsh
# ~/.zshrc - Configuração do Zsh

#######################################################
# CORES DO PYWAL (INTEGRAÇÃO DINÂMICA)
#######################################################
if [ -f "$HOME/.cache/wal/sequences" ] && [ -s "$HOME/.cache/wal/sequences" ]; then
    (cat "$HOME/.cache/wal/sequences" 2>/dev/null &)
fi

#######################################################
# PROMPT
#######################################################
autoload -U colors && colors
setopt PROMPT_SUBST

PROMPT='%F{blue}%B %b%f%F{white}%B%~%b%f%F{red}%B %b%f'

#######################################################
# HISTÓRICO
#######################################################
export HISTFILE="$HOME/.local/state/zsh/history"
mkdir -p "$(dirname "$HISTFILE")"
export HISTSIZE=100000
export SAVEHIST=200000
export HISTTIMEFORMAT="%F %T "

setopt APPEND_HISTORY          # Anexa ao invés de sobrescrever
setopt INC_APPEND_HISTORY      # Salva imediatamente após cada comando
setopt SHARE_HISTORY           # Compartilha histórico entre sessões
setopt HIST_IGNORE_DUPS        # Ignora duplicatas consecutivas
setopt HIST_IGNORE_ALL_DUPS    # Remove duplicatas antigas
setopt HIST_IGNORE_SPACE       # Ignora comandos com espaço no início
setopt HIST_REDUCE_BLANKS      # Remove espaços extras
setopt HIST_SAVE_NO_DUPS       # Não salva duplicatas no arquivo
setopt HIST_EXPIRE_DUPS_FIRST  # Expira duplicatas primeiro quando histórico enche
setopt HIST_FIND_NO_DUPS       # Não mostra duplicatas ao navegar no histórico
setopt EXTENDED_HISTORY        # Salva timestamp no histórico

# Equivalente ao HISTIGNORE do bash
HISTORY_IGNORE="(ls|ll|la|l|cd|pwd|clear|history|exit|fastfetch|bg|fg|bcp|h)"

#######################################################
# COMPORTAMENTO DO SHELL
#######################################################
setopt AUTO_CD                 # cd automático só com o nome do dir
setopt NO_CLOBBER              # Evita sobrescrever arquivos sem querer
setopt CORRECT                 # Sugere correção de comandos digitados errado
setopt INTERACTIVE_COMMENTS    # Permite comentários no shell interativo
setopt GLOB_STAR_SHORT         # **/* funciona nativamente
setopt EXTENDED_GLOB           # Globbing avançado: ^, ~, #
setopt NULL_GLOB               # Glob sem match não dá erro, retorna vazio
setopt NO_BEEP                 # Sem beep
setopt NUMERIC_GLOB_SORT       # Ordena file10 depois de file9, não depois de file1

# Atualiza LINES/COLUMNS ao redimensionar terminal
setopt CHECK_WINSIZE 2>/dev/null || true

#######################################################
# COMPLETION — ZSH NATIVO
#######################################################
autoload -Uz compinit
compinit -d "$HOME/.cache/zsh/zcompdump"

setopt COMPLETE_IN_WORD        # Completa a partir do meio da palavra
setopt ALWAYS_TO_END           # Move cursor pro fim após completion
setopt AUTO_MENU               # Mostra menu de completion automaticamente
setopt LIST_PACKED             # Lista de completion mais compacta

zstyle ':completion:*' menu select                        # Menu navegável com setas
zstyle ':completion:*' matcher-list 'm:{a-zA-Z}={A-Za-z}' # Case insensitive
zstyle ':completion:*' list-colors "${(s.:.)LS_COLORS}"   # Cores na completion
zstyle ':completion:*' group-name ''                       # Agrupa por categoria
zstyle ':completion:*:descriptions' format '%F{yellow}%B--- %d ---%b%f'
zstyle ':completion:*:warnings' format '%F{red}Sem resultados para: %d%f'
zstyle ':completion:*' rehash true                         # Detecta novos binários automaticamente
zstyle ':completion:*:*:kill:*:processes' list-colors '=(#b) #([0-9]#)*=0=01;31'
zstyle ':completion:*:kill:*' command 'ps -u $USER -o pid,%cpu,tty,cputime,cmd'

# Git completion nativa
zstyle ':completion:*:*:git:*' script /usr/share/bash-completion/completions/git

#######################################################
# KEYBINDINGS
#######################################################
bindkey -e                                    # Modo emacs (padrão, igual bash)
bindkey '^[[A' history-search-backward        # Seta cima → busca no histórico
bindkey '^[[B' history-search-forward         # Seta baixo → busca no histórico
bindkey '^[[C' forward-char
bindkey '^[[D' backward-char
bindkey '^R' history-incremental-search-backward  # Ctrl+R nativo do zsh
bindkey '^[[1;5C' forward-word                # Ctrl+Seta direita
bindkey '^[[1;5D' backward-word               # Ctrl+Seta esquerda
bindkey '^H' backward-delete-word             # Ctrl+Backspace deleta palavra

# Integração nativa do fzf (Arch) — Ctrl+R busca histórico, Ctrl+T arquivos, Alt+C dirs
if [[ -f /usr/share/fzf/key-bindings.zsh ]]; then
    source /usr/share/fzf/key-bindings.zsh
fi
if [[ -f /usr/share/fzf/completion.zsh ]]; then
    source /usr/share/fzf/completion.zsh
fi

# Configuração visual do fzf
export FZF_DEFAULT_COMMAND='fd --type f --hidden --strip-cwd-prefix'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"
export FZF_DEFAULT_OPTS='
  --height=60%
  --layout=reverse
  --border=rounded
  --prompt="  "
  --pointer="  "
  --preview-window=right:65%:wrap:border-left
'
export FZF_CTRL_T_OPTS="--preview 'bat --color=always --style=plain,numbers --line-range=:500 {}'"
export FZF_ALT_C_OPTS="--preview 'eza --tree --icons --color=always {} | head -100'"

# Título do terminal
precmd() { print -Pn "\e]0;%~\a" }

#######################################################
# EXPORTS — XDG
#######################################################
export XDG_DATA_HOME="$HOME/.local/share"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_BIN_HOME="$HOME/.local/bin"

#######################################################
# EXPORTS — APLICAÇÕES
#######################################################
export EDITOR='micro'
export VISUAL='micro'
export GIT_EDITOR='micro'
export DIFFPROG='micro'
export MICRO_TRUECOLOR=1

export TERMINAL='foot'
export BROWSER='qutebrowser'

export GPG_TTY=$(tty)
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)

export NPM_CONFIG_USERCONFIG="$XDG_CONFIG_HOME/npm/npmrc"
export PYTHONSTARTUP="$XDG_CONFIG_HOME/python/pythonrc"
export CARGO_HOME="$XDG_DATA_HOME/cargo"
export GNUPGHOME="$XDG_DATA_HOME/gnupg"
export GTK2_RC_FILES="$XDG_CONFIG_HOME/gtk-2.0/gtkrc"
export ANDROID_USER_HOME="$XDG_DATA_HOME/android"
export DOCKER_CONFIG="$XDG_CONFIG_HOME/docker"
export SAL_USE_VCLPLUGIN=gtk3
export LINUXTOOLBOXDIR="$HOME/linuxtoolbox"

#######################################################
# EXPORTS — VARIÁVEIS DE DIRETÓRIO
#######################################################
export dl="$(xdg-user-dir DOWNLOAD)"
export docs="$(xdg-user-dir DOCUMENTS)"
export media="$(xdg-user-dir PICTURES)"
export scr="$HOME/scr"
export config="${XDG_CONFIG_HOME:-$HOME/.config}"
export wallpapers="/usr/share/meus_wallpapers"

#######################################################
# EXPORTS — MAN PAGES (CORES)
#######################################################
export LESS_TERMCAP_mb=$'\E[1;31m'
export LESS_TERMCAP_md=$'\E[1;34m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[1;32m'

#######################################################
# EXPORTS — LS COLORS
#######################################################
export CLICOLOR=1
export LS_COLORS='no=00:fi=00:di=00;34:ln=01;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.gz=01;31:*.bz2=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.avi=01;35:*.fli=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.ogg=01;35:*.mp3=01;35:*.wav=01;35:*.xml=00;31:'

#######################################################
# PATH
#######################################################
export PATH="$HOME/.local/bin:$HOME/scr:/usr/local/bin:$PATH"

#######################################################
# AUTOSUGGESTIONS + SYNTAX HIGHLIGHTING
# (únicos 2 pacotes externos — yay -S zsh-autosuggestions zsh-syntax-highlighting)
#######################################################
[ -f /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh ] && \
    source /usr/share/zsh/plugins/zsh-autosuggestions/zsh-autosuggestions.zsh

[ -f /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh ] && \
    source /usr/share/zsh/plugins/zsh-syntax-highlighting/zsh-syntax-highlighting.zsh

# Configuração do autosuggestions
ZSH_AUTOSUGGEST_STRATEGY=(history completion)   # Busca no histórico, depois completion
ZSH_AUTOSUGGEST_BUFFER_MAX_SIZE=20
ZSH_AUTOSUGGEST_USE_ASYNC=true
bindkey '^ ' autosuggest-accept                 # Ctrl+Espaço aceita sugestão
bindkey '^[[C' forward-char                     # → aceita um char da sugestão

#######################################################
# ALIASES — VISUALIZAÇÃO (EZA)
#######################################################
alias ls='eza --icons=always --group-directories-first --color=always'
alias ll='eza -lh --icons --group-directories-first --git'
alias la='eza -Ah --icons --group-directories-first'
alias tree='eza --tree --icons'
alias find='fd --hidden --follow'
compdef eza=ls    # Reutiliza completion do ls para o eza

#######################################################
# ALIASES — NAVEGAÇÃO
#######################################################
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'
alias home='cd ~'
alias docs='cd "$docs"'
alias dl='cd "$dl"'
alias media='cd "$media"'
alias scr='cd "$scr"'
alias bin='cd "$XDG_BIN_HOME"'
alias config='cd "$config"'
alias share='cd "$XDG_DATA_HOME"'
alias wallpapers='cd "$wallpapers"'

#######################################################
# ALIASES — PRODUTIVIDADE
#######################################################
alias e='$EDITOR'
alias c='clear'
alias ezsh='$EDITOR ~/.zshrc && source ~/.zshrc && clear && echo -e "\033[1;32m✓ Zshrc recarregado!\033[0m"'
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias ip='ip -color=auto'

#######################################################
# ALIASES — SISTEMA
#######################################################
alias df='df -h'
alias du='du -h'
alias free='free -h'
alias cp='cp -ivp'
alias mv='mv -iv'
alias rm='rm -vI'
alias dd='echo "Use iso2sd para gravação segura."'

#######################################################
# ALIASES — MANUTENÇÃO DO SISTEMA
#######################################################
alias update='topgrade'
alias update-fast='topgrade --only system'
alias update-clean='topgrade --cleanup'
alias update-quiet='topgrade > ~/.local/share/topgrade.log 2>&1'
alias update-check='topgrade -n'
alias update-aur='yay -Sua'
alias update-deep='topgrade && sudo pacman -Scc && yay -Sc'

alias cleanup='~/.local/bin/sistema-clean'
alias cleanup-dry='~/.local/bin/sistema-clean --dry-run'
alias orphans='orphans=$(pacman -Qdtq); [ -n "$orphans" ] && sudo pacman -Rns $orphans'

alias mirrors-br='sudo reflector --country Brazil --latest 5 --sort rate --save /etc/pacman.d/mirrorlist && yay -Syyu'
alias mirrors-global='sudo reflector --latest 10 --sort rate --save /etc/pacman.d/mirrorlist && yay -Syyu'
alias mirrors-fix='sudo reflector --country "Brazil,United States,Germany" --latest 10 --sort rate --save /etc/pacman.d/mirrorlist'

#######################################################
# ALIASES — GIT
#######################################################
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='pass git pull && pass git push'
alias gl='git log --oneline --graph --all'
alias github='~/.local/bin/sync.sh'

#######################################################
# ALIASES — HISTÓRICO
#######################################################
alias h='fc -l 1 | fzf --tac --header "Histórico Global"'

#######################################################
# ALIASES — YOUTUBE-DLP
#######################################################
alias ytmp3='yt-dlp -x --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s"'
alias ytmp4='yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(title)s.%(ext)s"'
alias ytlist-mp3='yt-dlp -x --audio-format mp3 -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"'
alias ytlist-mp4='yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"'
alias yttmp3='yt-dlp --download-sections "*01:00-02:00" -x --audio-format mp3 "URL"'

#######################################################
# ALIASES — USB
#######################################################
alias usb-in='udisksctl mount -b /dev/sdb1 && ln -s /run/media/farrezeb/* ~/USB'
alias usb-out='udisksctl unmount -b /dev/sdb1 && rm ~/USB && udisksctl power-off -b /dev/sdb1'

#######################################################
# ALIASES — WI-FI
#######################################################
alias senhawifi='nmcli -s device wifi show-password'
alias wifi-on='nmcli radio wifi on'

#######################################################
# ALIASES — ESPOCRM (DOCKER)
#######################################################
alias espocrm-up='cd ~/espocrm-docker && docker compose up -d'
alias espocrm-down='cd ~/espocrm-docker && docker compose down'
alias espocrm-logs='cd ~/espocrm-docker && docker compose logs -f'
alias espocrm-status='cd ~/espocrm-docker && docker compose ps'
alias espocrm='~/.local/bin/espocrm.sh'
alias espocrm-db='sudo docker exec espocrm-app env | grep -i -E "(db|mysql|password|user)"'

#######################################################
# ALIASES — DIVERSOS
#######################################################
alias criariso='sudo ventoyweb'
alias meubkp='tar -czvf ~/hyprland_backup_$(date +%Y%m%d).tar.gz ~/.config/hypr ~/.config/waybar ~/.config/dunst ~/.config/fuzzel ~/.config/qutebrowser ~/.local/bin/ ~/.config/foot ~/.config/lf ~/.config/wal ~/.config/imv ~/.config/mpv /usr/share/meus_wallpapers/ ~/.bashrc ~/.zshrc ~/.inputrc'
alias myalias='alias | fzf --header "Meus Aliases" | cut -d"=" -f1 | cut -d" " -f2 | xargs -r -I {} zsh -c "{}"'
alias lsend='files=$(fzf -m --preview "ls -lh {}") && [ -n "$files" ] && echo "$files" | xargs -d "\n" localsend'
alias printtop='ps -Heo user,pid,pcpu,pmem,args --sort=-pcpu | grep -v "\[.*\]" | head -n 50 > ~/dl/snapshot_ps_$(date +%Y%m%d_%H%M%S).txt && ls -lh ~/dl/snapshot_ps_*.txt | tail -1'
alias printbrowser='ps aux | grep -E "qutebrowser|chrome|QtWebEngine" | grep -v grep > ~/dl/browser_$(date +%Y%m%d_%H%M%S).txt && echo "Salvo em ~/dl/browser_*.txt"'

#######################################################
# FUNÇÃO — LF WRAPPER (muda de diretório ao sair)
#######################################################
lf() {
    local tmp
    tmp="$(mktemp)"
    command lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        local dir
        dir="$(cat "$tmp")"
        rm -f "$tmp"
        [ -d "$dir" ] && [ "$dir" != "$(pwd)" ] && cd "$dir"
    fi
}

#######################################################
# FUNÇÃO — COMANDOS FAVORITOS (FZF)
#######################################################
comandos() {
    local cmd
    cmd=$(column -t -s $'\t' ~/.config/fzfbash/commands | \
          fzf --header "Comandos Favoritos" --prompt "  " | \
          awk '{print $1}')
    [ -z "$cmd" ] && return
    eval "$cmd"
}

#######################################################
# FUNÇÃO — SENHA WI-FI (FZF)
#######################################################
fpass() {
    local file
    file=$(sudo ls /etc/NetworkManager/system-connections/ | \
           fzf --header "Selecione a rede para ver a senha")
    if [ -n "$file" ]; then
        echo -e "\n Rede: ${file%.nmconnection}"
        sudo grep -h '^psk=' "/etc/NetworkManager/system-connections/$file" \
            | cut -d= -f2 | xargs echo " Senha:"
    fi
}

#######################################################
# FUNÇÃO — PRIORIDADE WI-FI (FZF + NMCLI)
#######################################################
wpref() {
    local escolha interface
    interface=$(nmcli -t -f DEVICE,TYPE device | grep ":wifi$" | cut -d: -f1 | head -n1)
    escolha=$(nmcli -t -f TYPE,NAME connection show | grep "^802-11-wireless" | \
              cut -d: -f2 | fzf --header "Priorizar e Conectar agora:")
    if [ -n "$escolha" ] && [ -n "$interface" ]; then
        nmcli -t -f TYPE,NAME connection show | grep "^802-11-wireless" | cut -d: -f2 | \
            xargs -I {} sudo nmcli connection modify "{}" connection.autoconnect-priority 1
        sudo nmcli connection modify "$escolha" connection.autoconnect-priority 100
        echo "Alternando para: $escolha..."
        sudo nmcli device disconnect "$interface" && sudo nmcli device connect "$interface"
        echo "Conectado em $escolha com prioridade máxima!"
    else
        echo "Operação cancelada ou interface wifi não encontrada."
    fi
}

#######################################################
# FUNÇÃO — FORMATAR PENDRIVE
#######################################################
format-drive() {
    local DEVICE="$1"
    local NAME="$2"

    if [[ ! "$DEVICE" == /dev/* ]]; then
        NAME="$1"
        DEVICE=$(lsblk -p -d -n -o NAME,RM | grep " 1$" | awk '{print $1}' | grep -v "/dev/sda" | head -n 1)
    fi

    if [ -z "$DEVICE" ] || [ -z "$NAME" ]; then
        echo "Uso: format-drive <nome> ou format-drive /dev/sdX <nome>"
        return 1
    fi

    if [[ "$DEVICE" == "/dev/sda"* ]]; then
        echo "ERRO: Operação em /dev/sda bloqueada!"
        return 1
    fi

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "ALVO: $DEVICE | NOME: $NAME | SISTEMA: exFAT"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -rp "Tem certeza? Isso apagará TUDO! (y/N): " confirm
    [[ ! "$confirm" =~ ^[Yy]$ ]] && { echo "Operação cancelada."; return 0; }

    echo "Limpando assinaturas antigas..."
    sudo wipefs -a "$DEVICE"
    echo "Criando nova tabela de partição GPT..."
    sudo parted -s "$DEVICE" mklabel gpt mkpart primary 1MiB 100%
    echo "Sincronizando disco..."
    sudo partprobe "$DEVICE"
    sleep 2

    local partition
    partition="$([[ $DEVICE == *"nvme"* ]] && echo "${DEVICE}p1" || echo "${DEVICE}1")"

    if [ -b "$partition" ]; then
        echo "Formatando $partition como exFAT..."
        sudo mkfs.exfat -n "$NAME" "$partition"
        echo "✅ Concluído: $DEVICE formatado como '$NAME'."
    else
        echo "❌ ERRO: Partição $partition não encontrada. Reconecte o pendrive."
        return 1
    fi
}

#######################################################
# FUNÇÃO — CP COM BARRA DE PROGRESSO (RSYNC)
#######################################################
cpp() {
    rsync -ah --progress "$@"
}

#######################################################
# FUNÇÃO — EXTRATOR UNIVERSAL
#######################################################
ex() {
    if [ ! -f "$1" ]; then
        echo "'$1' não é um arquivo válido"
        return 1
    fi
    case "$1" in
        *.tar.bz2|*.tbz2) tar xjf "$1"    ;;
        *.tar.gz|*.tgz)   tar xzf "$1"    ;;
        *.tar)             tar xf  "$1"    ;;
        *.bz2)             bunzip2 "$1"    ;;
        *.gz)              gunzip  "$1"    ;;
        *.rar)             unrar x "$1"    ;;
        *.zip)             unzip   "$1"    ;;
        *.Z)               uncompress "$1" ;;
        *.7z)              7z x    "$1"    ;;
        *)                 echo "'$1' não pode ser extraído via ex()" ;;
    esac
}

#######################################################
# FUNÇÃO — BUSCAR ARQUIVOS
#######################################################
buscar() {
    fd -HI "$1" / 2>/dev/null || sudo find / -iname "*$1*" 2>/dev/null
}

#######################################################
# FUNÇÃO — CONVERTER PARA EPUB (APPLE BOOKS)
#######################################################
convertepub() {
    command -v pandoc &>/dev/null || { echo "Erro: instale pandoc (yay -S pandoc-bin)"; return 1; }
    [ -z "$1" ] && { echo "Uso: convertepub arquivo.docx"; return 1; }
    [ ! -f "$1" ] && { echo "Erro: '$1' não existe."; return 1; }

    local input="$1"
    local base="${input%.*}"
    local output="${base}.epub"
    local title
    title=$(echo "$base" | tr '_-' ' ')

    echo "Convertendo: $input → $output"
    pandoc "$input" -o "$output" --to=epub3 --toc --split-level=1 \
        --metadata lang=pt-BR --metadata title="$title"

    if [ $? -eq 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ Sucesso! '$output' pronto para o iPhone."
    else
        echo "❌ Erro na conversão."
    fi
}

#######################################################
# FUNÇÃO — CONVERTER EPUB PARA DOCX
#######################################################
epubparadocx() {
    local FILE="$1"
    [ -z "$FILE" ] || [ ! -f "$FILE" ] && {
        echo "Uso: epubparadocx livro.epub"
        return 1
    }

    echo "Extraindo texto de: $FILE..."
    if epub2html "$FILE"; then
        local HTML="${FILE%.epub}.html"
        local DOCX="${FILE%.epub}.docx"
        echo "Convertendo para DOCX..."
        pandoc "$HTML" -o "$DOCX" && {
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "✅ Concluído! Arquivo: $DOCX"
        } || echo "❌ Erro na conversão do Pandoc."
    else
        echo "❌ Erro na extração do EPUB."
    fi
}

#######################################################
# FUNÇÃO — CONVERTER PDF PARA DOCX
#######################################################
pdfparadocx() {
    local FILE="$1"
    [ -z "$FILE" ] || [ ! -f "$FILE" ] && {
        echo "Uso: pdfparadocx arquivo.pdf"
        return 1
    }

    local VENV="$HOME/scr/venv/bin/activate"
    local SCRIPT="$HOME/scr/extrair_pdf.py"
    local HTML="${FILE%.pdf}.html"
    local DOCX="${FILE%.pdf}.docx"

    echo "Extraindo texto..."
    ( source "$VENV" && python "$SCRIPT" "$FILE" )

    if [ -f "$HTML" ]; then
        echo "Gerando DOCX via Pandoc..."
        pandoc "$HTML" -f html -t docx -o "$DOCX"
        rm "$HTML"
        local SIZE
        SIZE=$(du -h "$DOCX" | cut -f1)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "✅ Concluído! Tamanho: $SIZE — Arquivo: $DOCX"
    else
        echo "❌ Falha na extração do texto."
    fi
}

#######################################################
# FUNÇÃO — GERENCIADOR DE SENHAS (PASS)
#######################################################
pass-new() {
    echo "📁 Caminho (ex: facebook/farrezeb):"
    read -r path

    if pass show "$path" &>/dev/null; then
        echo "⚠️  Atenção: $path já existe!"
        read -rp "Sobrescrever? [y/N] " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || { echo "❌ Cancelado"; return 1; }
    fi

    echo "👤 Login/Email:"
    read -r login
    echo "🌐 URL (deixe em branco para usar: ${path%%/*}):"
    read -r url
    url=${url:-${path%%/*}}
    echo "🔑 Senha (oculta):"
    read -rs password
    echo ""

    [ -z "$password" ] && { echo "❌ Erro: senha não pode ser vazia"; return 1; }

    printf "%s\nlogin: %s\nurl: %s\n" "$password" "$login" "$url" | pass insert -m "$path"

    if [ $? -eq 0 ]; then
        echo "✅ Criado: $path"
        echo ""
        pass show "$path"
    else
        echo "❌ Erro ao criar entrada"
        return 1
    fi
}
