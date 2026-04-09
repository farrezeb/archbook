#!/bin/bash
# ~/.bashrc - Configuração otimizada do Bash

# Retorna se não for uma sessão interativa
[[ $- != *i* ]] && return

#######################################################
# CORES DO PYWAL (INTEGRAÇÃO DINÂMICA)
#######################################################

if [ -f "$HOME/.cache/wal/sequences" ] && [ -s "$HOME/.cache/wal/sequences" ]; then
    (cat "$HOME/.cache/wal/sequences" 2>/dev/null &)
fi

wrap_color() {
    echo -n "\[$1\]"
}

C_LOGO=$(wrap_color "\e[1;94m")     # Amarelo Bold ()
C_PATH=$(wrap_color "\e[1;37m")      # Branco Bold
C_ARROW=$(wrap_color "\e[1;31m")     # Vermelho Bold
C_RESET=$(wrap_color "\e[0m")        # Reset

#######################################################
# CONFIGURAÇÃO DO PROMPT (PS1)
#######################################################

# Limpar configurações anteriores
unset PROMPT_COMMAND

PS1="${C_LOGO} ${C_PATH} \w${C_ARROW} ${C_RESET}"


#######################################################
# CONFIGURAÇÕES LF WRAPPER
#######################################################
lf() {
    tmp="$(mktemp)"
    # O comando real do lf grava o último diretório no arquivo temporário
    command lf -last-dir-path="$tmp" "$@"
    if [ -f "$tmp" ]; then
        dir="$(cat "$tmp")"
        rm -f "$tmp"
        if [ -d "$dir" ] && [ "$dir" != "$(pwd)" ]; then
            cd "$dir"
        fi
    fi
}

#######################################################
# CONFIGURAÇÕES DE EXPORT (MAN PAGES E LS)
#######################################################

# Cores nas Man Pages
export LESS_TERMCAP_mb=$'\E[1;31m'
export LESS_TERMCAP_md=$'\E[1;34m'
export LESS_TERMCAP_me=$'\E[0m'
export LESS_TERMCAP_se=$'\E[0m'
export LESS_TERMCAP_so=$'\E[01;44;33m'
export LESS_TERMCAP_ue=$'\E[0m'
export LESS_TERMCAP_us=$'\E[1;32m'

# Cores para o comando LS
export CLICOLOR=1
export LS_COLORS='no=00:fi=00:di=00;34:ln=01;36:pi=40;33:so=01;35:do=01;35:bd=40;33;01:cd=40;33;01:or=40;31;01:ex=01;32:*.tar=01;31:*.tgz=01;31:*.arj=01;31:*.taz=01;31:*.lzh=01;31:*.zip=01;31:*.z=01;31:*.Z=01;31:*.gz=01;31:*.bz2=01;31:*.deb=01;31:*.rpm=01;31:*.jar=01;31:*.jpg=01;35:*.jpeg=01;35:*.gif=01;35:*.bmp=01;35:*.pbm=01;35:*.pgm=01;35:*.ppm=01;35:*.tga=01;35:*.xbm=01;35:*.xpm=01;35:*.tif=01;35:*.tiff=01;35:*.png=01;35:*.mov=01;35:*.mpg=01;35:*.mpeg=01;35:*.avi=01;35:*.fli=01;35:*.gl=01;35:*.dl=01;35:*.xcf=01;35:*.xwd=01;35:*.ogg=01;35:*.mp3=01;35:*.wav=01;35:*.xml=00;31:'

#######################################################
# ALIASES DE VISUALIZAÇÃO (EZA)
#######################################################
alias ls='eza --icons=always --group-directories-first --color=always'
alias ll='eza -lh --icons --group-directories-first --git'
alias la='eza -Ah --icons --group-directories-first'
alias tree='eza --tree --icons'
#alias cat='bat'
alias find='fd --hidden --follow'

#######################################################
# EXPORTS & AMBIENTE (PADRÃO XDG)
#######################################################
# GPG no Wayland
export GPG_TTY=$(tty)
export SSH_AUTH_SOCK=$(gpgconf --list-dirs agent-ssh-socket)

export XDG_DATA_HOME="$HOME/.local/share"
export XDG_CONFIG_HOME="$HOME/.config"
export XDG_STATE_HOME="$HOME/.local/state"
export XDG_CACHE_HOME="$HOME/.cache"
export XDG_BIN_HOME="$HOME/.local/bin"

# Redirecionamento de arquivos de configuração
export NPM_CONFIG_USERCONFIG="$XDG_CONFIG_HOME/npm/npmrc"
export PYTHONSTARTUP="$XDG_CONFIG_HOME/python/pythonrc"
export CARGO_HOME="$XDG_DATA_HOME/cargo"
export GNUPGHOME="$XDG_DATA_HOME/gnupg"
export GTK2_RC_FILES="$XDG_CONFIG_HOME/gtk-2.0/gtkrc"
export ANDROID_USER_HOME="$XDG_DATA_HOME/android"
export DOCKER_CONFIG="$XDG_CONFIG_HOME/docker"
export SAL_USE_VCLPLUGIN=gtk3

# Editores (Definir antes dos aliases)
export MICRO_TRUECOLOR=1
export EDITOR='micro'
export VISUAL='micro'

# --- VARIÁVEIS DE USUÁRIO (Para usar com: la $documentos, cp $downloads) ---
export dl="$(xdg-user-dir DOWNLOAD)"      # Atalho curto $dl
export docs="$(xdg-user-dir DOCUMENTS)"   # Atalho curto $docs
export media="$(xdg-user-dir PICTURES)"   # Unifica Imagens/Vídeos/Música
export scr="$HOME/scr"
export config="${XDG_CONFIG_HOME:-$HOME/.config}"
export wallpapers="/usr/share/meus_wallpapers"

shopt -s autocd

# --- ATALHOS DE NAVEGAÇÃO (Para usar com: documentos, downloads) ---
alias docs='cd "$docs"'
alias dl='cd "$dl"'
alias media='cd "$media"'
alias scr='cd "$scr"'
alias bin='cd "$XDG_BIN_HOME"'
alias config='cd "$config"'
alias share='cd "$XDG_DATA_HOME"'
alias home='cd ~'
alias wallpapers='cd "$wallpapers"'
alias e='$EDITOR'
alias c='clear'

########################################
# HISTORY — UNIFICADO E TURBINADO
########################################

export HISTFILE="$HOME/.local/state/bash/history"
mkdir -p "$(dirname "$HISTFILE")"

export HISTSIZE=100000
export HISTFILESIZE=200000
export HISTTIMEFORMAT="%F %T "

# Ignora duplicados e comandos que começam com espaço
export HISTCONTROL=ignoreboth:erasedups
export HISTIGNORE="ls:ll:la:l:cd:pwd:clear:history:exit:fastfetch:bg:fg:bcp:h"

# Configurações de comportamento (O que você queria manter)
shopt -s histappend  # Anexa ao invés de sobrescrever
shopt -s cmdhist     # Salva comandos multilinhas em uma entrada
shopt -s lithist    # Preserva quebras de linha literais no histórico

# Sincroniza o histórico entre abas do terminal em tempo real
PROMPT_COMMAND="history -a; history -n; ${PROMPT_COMMAND:-}"

# Seu alias de busca fuzzy
alias h='history | fzf --tac --header "Histórico Global"'

# Ctrl+R vira busca history gráfica
bind '"\C-r": "\C-a history | fzf\n"'

# Comportamento do Terminal
bind "set bell-style visible" 2>/dev/null
shopt -s checkwinsize
stty -ixon 2>/dev/null
bind "set completion-ignore-case on" 2>/dev/null
bind "set show-all-if-ambiguous On" 2>/dev/null

# Outras variáveis
export LINUXTOOLBOXDIR="$HOME/linuxtoolbox"
export TERMINAL="foot"
export BROWSER="qutebrowser"

#######################################################
# TRAVAS DE SEGURANÇA GLOBAIS
#######################################################

# Bloqueia dd manual
alias dd='echo "Use iso2sd para gravação segura."'

# Evita sobrescrever arquivos sem querer
set -o noclobber

#######################################################
# FUNÇÕES ÚTEIS
#######################################################

# fzfbash: Busca e executa aliases/funções definidos no .bashrc
comandos() {
    local cmd

    cmd=$(column -t -s $'\t' ~/.config/fzfbash/commands | \
          fzf --header "Comandos Favoritos" \
              --prompt "  " | \
          awk '{print $1}')

    [ -z "$cmd" ] && return

    eval "$cmd"
}

# Alias rápido para listar apenas aliases simples
alias myalias='alias | fzf --header "Meus Aliases" | cut -d"=" -f1 | cut -d" " -f2 | xargs -r -I {} bash -c "{}"'

# fpass: Seleciona a rede com fzf e mostra a senha (PSK)
fpass() {
    local file
    file=$(sudo ls /etc/NetworkManager/system-connections/ | fzf --header "Selecione a rede para ver a senha")

    if [ -n "$file" ]; then
        echo -e "\n Rede: ${file%.nmconnection}"
        sudo grep -h '^psk=' "/etc/NetworkManager/system-connections/$file" | cut -d= -f2 | xargs echo " Senha:"
    fi
}

# wpref: Define a prioridade e RECONECTA na hora
wpref() {
    local escolha interface
    # Detecta o nome da sua interface wifi (ex: wlan0)
    interface=$(nmcli -t -f DEVICE,TYPE device | grep ":wifi$" | cut -d: -f1 | head -n1)
    # Lista conexões salvas
    escolha=$(nmcli -t -f TYPE,NAME connection show | grep "^802-11-wireless" | cut -d: -f2 | fzf --header "Priorizar e Conectar agora:")

    if [ -n "$escolha" ] && [ -n "$interface" ]; then
        # Reseta outras redes para prioridade 1 e a escolhida para 100
        nmcli -t -f TYPE,NAME connection show | grep "^802-11-wireless" | cut -d: -f2 | xargs -I {} sudo nmcli connection modify "{}" connection.autoconnect-priority 1
        sudo nmcli connection modify "$escolha" connection.autoconnect-priority 100

        echo "Alternando para: $escolha..."
        # Força a troca imediata
        sudo nmcli device disconnect "$interface" && sudo nmcli device connect "$interface"
        echo "Conectado em $escolha com prioridade máxima!"
    else
        echo "Operação cancelada ou interface wifi não encontrada."
    fi
}

# Seleciona arquivos com fzf e abre no LocalSend
alias lsend='files=$(fzf -m --preview "ls -lh {}") && [ -n "$files" ] && echo "$files" | xargs -d "\n" localsend'

# Extrator universal de arquivos compactados
ex() {
    if [ -f "$1" ]; then
        case "$1" in
            *.tar.bz2)   tar xjf "$1"   ;;
            *.tar.gz)    tar xzf "$1"   ;;
            *.bz2)       bunzip2 "$1"   ;;
            *.rar)       unrar x "$1"   ;;
            *.gz)        gunzip "$1"    ;;
            *.tar)       tar xf "$1"    ;;
            *.tbz2)      tar xjf "$1"   ;;
            *.tgz)       tar xzf "$1"   ;;
            *.zip)       unzip "$1"     ;;
            *.Z)         uncompress "$1";;
            *.7z)        7z x "$1"      ;;
            *)           echo "'$1' não pode ser extraído via ex()" ;;
        esac
    else
        echo "'$1' não é um arquivo válido"
    fi
}

# Converter documentos para EPUB otimizado para iPhone/Apple Books

convertepub() {
    # Verifica se o pandoc está instalado
    if ! command -v pandoc &> /dev/null; then
        echo "Erro: Pandoc não encontrado."
        echo "Instale com: yay -S pandoc-bin"
        return 1
    fi

    # Verifica se o usuário passou um arquivo
    if [ -z "$1" ]; then
        echo "Uso: convertepub arquivo.docx (ou .odt, .doc, .txt)"
        return 1
    fi

    # Verifica se o arquivo existe
    if [ ! -f "$1" ]; then
        echo "Erro: O arquivo '$1' não existe."
        return 1
    fi

    # Define nomes de entrada e saída
    local input_file="$1"
    local filename_no_ext="${input_file%.*}"
    local output_file="${filename_no_ext}.epub"

    echo "Iniciando conversão para iPhone (Apple Books)"
    echo "Entrada: $input_file"
    echo "Saída:   $output_file"

    # Limpa o nome do arquivo para o título (ex: "Livro_de_Teste" vira "Livro de Teste")
    local clean_title=$(echo "$filename_no_ext" | tr '_-' ' ')

    # Execução do Pandoc com parâmetros otimizados
    # Note a barra invertida \ ao final de cada linha para continuar o comando
    pandoc "$input_file" \
        -o "$output_file" \
        --to=epub3 \
        --toc \
        --split-level=1 \
        --metadata lang=pt-BR \
        --metadata title="$clean_title"

    # Verificação de sucesso
    if [ $? -eq 0 ]; then
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Sucesso! O arquivo '$output_file' está pronto."
        echo "Dica: Envie para o iPhone via iCloud ou PairDrop.net"
    else
        echo "Erro: Houve um problema na conversão."
    fi
}

# Converter documentos EPUB para Docx
# Função para extrair EPUB e converter para DOCX automaticamente
epubparadocx() {
    local FILE="$1"

    # Verifica se o arquivo foi passado e se existe
    if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
        echo "Erro: Forneça um arquivo .epub válido."
        echo "Uso: epubparadocx livro.epub"
        return 1
    fi

    # 1. Extrai o conteúdo usando seu comando de script
    # 2. Converte o HTML gerado para DOCX via Pandoc
    echo "Extraindo texto de: $FILE..."

    if epub2html "$FILE"; then
        local HTML_FILE="${FILE%.epub}.html"
        local DOCX_FILE="${FILE%.epub}.docx"

        echo "Convertendo para DOCX..."
        pandoc "$HTML_FILE" -o "$DOCX_FILE"

        if [ $? -eq 0 ]; then
            echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
            echo "Concluído! Arquivo para tradução: $DOCX_FILE"
            echo "Agora envie este DOCX para o Google Tradutor Documentos."
        else
            echo "Erro na conversão do Pandoc."
        fi
    else
        echo "Erro na extração do EPUB."
    fi
}

# Converter documentos PDF para Docx
# Função para extrair PDF e converter para DOCX automaticamente
pdfparadocx() {
    local FILE="$1"

    if [ -z "$FILE" ] || [ ! -f "$FILE" ]; then
        echo "Erro: Forneça um arquivo .pdf válido."
        return 1
    fi

    local VENV_PATH="$HOME/scr/venv/bin/activate"
    local SCRIPT_PATH="$HOME/scr/extrair_pdf.py"
    local HTML_FILE="${FILE%.pdf}.html"
    local DOCX_FILE="${FILE%.pdf}.docx"

    echo "Extraindo texto (otimizando para tradução)..."

    # Ativa venv e roda o script
    (
        source "$VENV_PATH"
        python "$SCRIPT_PATH" "$FILE"
    )

    if [ -f "$HTML_FILE" ]; then
        echo "Gerando DOCX leve via Pandoc..."

        # Otimização: Convertemos de HTML para DOCX limpando estilos inúteis
        pandoc "$HTML_FILE" -f html -t docx -o "$DOCX_FILE"

        rm "$HTML_FILE"

        # Verifica o tamanho final
        local SIZE=$(du -h "$DOCX_FILE" | cut -f1)
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "Concluído! Tamanho final: $SIZE"
        echo "Arquivo: $DOCX_FILE"
        echo "Pronto para o Google Tradutor (Limite 10MB)."
    else
        echo "Falha na extração do texto."
    fi
}

# Realizar busca que contenha o nome =

buscar() {
    fd -HI "$1" / 2>/dev/null || sudo find / -iname "*$1*" 2>/dev/null
}

#######################################################
# ALIASES (ATALHOS)
#######################################################

# Limpeza do sistema (com confirmação)
alias cleanup='echo "Limpando Capturas..." && \
    rm -f "$HOME/media/Capturas\ de\ tela/"* 2>/dev/null && \
    echo "Limpando Cache..." && \
    sudo paccache -rk2 && \
    echo "Removendo Órfãos..." && \
    yay -Sc --noconfirm && \
    (yay -Yc --noconfirm || true) && \
    echo "Removendo Órfãos Pacman..." && \
    (sudo pacman -Rns $(pacman -Qdtq) 2>/dev/null || echo "Nenhum órfão encontrado.") && \
    echo "Limpando Snapshots (mantendo os 3 últimos)..." && \
    sudo timeshift --list | grep -E "^[0-9]" | awk "{print \$3}" | head -n -3 | xargs -I {} sudo timeshift --delete --snapshot {} --scripted && \
    echo "Logs..." && \
    sudo journalctl --vacuum-time=30d && \
    (sudo find /var/log/timeshift/ -type f -mtime +7 -delete 2>/dev/null || true) && \
    echo "Status Final:" && \
    eza -lh --icons --group-directories-first /var/log/timeshift/ 2>/dev/null && \
    find ~/dl -name "snapshot_top_*.txt" -mtime +7 -delete && \
    echo "Limpando caches e thumbnails..." && \
    rm -rf ~/.cache/qutebrowser/qtsql/*.sqlite-wal ~/.cache/thumbnails/* ~/.config/micro/buffers/* && \
    echo "Concluído!"'


# Fazer backup de configuracoes
alias meubkp='tar -czvf ~/hyprland_backup_$(date +%Y%m%d).tar.gz ~/.config/hypr ~/.config/waybar ~/.config/dunst ~/.config/fuzzel ~/.config/qutebrowser ~/.local/bin/ ~/.config/foot ~/.config/lf  ~/.config/wal ~/.config/imv ~/.config/mpv /usr/share/meus_wallpapers/ ~/.bashrc ~/.inputrc'

# Remover órfãos manualmente (com aviso)
alias orphans='orphans=$(pacman -Qdtq); [ -n "$orphans" ] && sudo pacman -Rns $orphans'

# Produtividade básica
alias grep='grep --color=auto'
alias diff='diff --color=auto'
alias ip='ip -color=auto'
alias ebash='$EDITOR ~/.bashrc && source ~/.bashrc && clear && echo -e "\033[1;32m✓ Bashrc recarregado!\033[0m"'

# Navegação rápida
alias ..='cd ..'
alias ...='cd ../..'
alias ....='cd ../../..'

# Segurança (confirmação antes de sobrescrever)
alias cp='cp -ivp'
alias mv='mv -iv'
alias rm='rm -vI'

# Informações do sistema
alias df='df -h'
alias du='du -h'
alias free='free -h'

# --- Gerenciamento de USB (udisksctl) ---
# Monta e cria o atalho na Home
alias usb-in='udisksctl mount -b /dev/sdb1 && ln -s /run/media/farrezeb/* ~/USB'

# Desmonta, remove o atalho morto e desliga a porta USB do Mac
alias usb-out='udisksctl unmount -b /dev/sdb1 && rm ~/USB && udisksctl power-off -b /dev/sdb1'

# Formatar Pen-Driver
format-drive() {
  local DEVICE="$1"
  local NAME="$2"

  # Autodetecção aprimorada
  if [[ ! "$DEVICE" == /dev/* ]]; then
    NAME="$1"
    DEVICE=$(lsblk -p -d -n -o NAME,RM | grep " 1$" | awk '{print $1}' | grep -v "/dev/sda" | head -n 1)
  fi

  if [ -z "$DEVICE" ] || [ -z "$NAME" ]; then
    echo "Uso: format-drive <nome> ou format-drive /dev/sdX <nome>"
    return 1
  fi

  # Trava de segurança
  if [[ "$DEVICE" == "/dev/sda"* ]]; then
    echo "ERRO: Operação em /dev/sda bloqueada!"; return 1
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "ALVO: $DEVICE"
  echo "NOME: $NAME"
  echo "SISTEMA: exFAT"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

  read -rp "Tem certeza? Isso apagará TUDO! (y/N): " confirm
  if [[ "$confirm" =~ ^[Yy]$ ]]; then
    echo "Limpando assinaturas antigas..."
    sudo wipefs -a "$DEVICE"

    echo "Criando nova tabela de partição GPT..."
    # Removido o 'exfat' daqui para evitar erro de token inválido no parted
    sudo parted -s "$DEVICE" mklabel gpt mkpart primary 1MiB 100%

    echo "Sincronizando disco..."
    sudo partprobe "$DEVICE"
    sleep 2 # Tempo para o sistema criar o nó /dev/sdb1

    # Identifica a partição (sdb -> sdb1 ou nvme0n1 -> nvme0n1p1)
    local partition="$([[ $DEVICE == *"nvme"* ]] && echo "${DEVICE}p1" || echo "${DEVICE}1")"

    if [ -b "$partition" ]; then
      echo "Formatando partição $partition..."
      sudo mkfs.exfat -n "$NAME" "$partition"
      echo "✅ Concluído: $DEVICE formatado como '$NAME'."
    else
      echo "❌ ERRO: A partição $partition não foi encontrada. Tente reconectar o pendrive."
      return 1
    fi
  else
    echo "Operação cancelada."
  fi
}


# cp com barra de progresso usando rsync
cpp() {
  rsync -ah --progress "$@"
}

# Criar Iso Ventoy
alias criariso='sudo ventoyweb'

# Snapshot do top
alias printtop='ps -Heo user,pid,pcpu,pmem,args --sort=-pcpu | grep -v "\[.*\]" | head -n 50 > ~/dl/snapshot_ps_$(date +%Y%m%d_%H%M%S).txt && ls -lh ~/dl/snapshot_ps_*.txt | tail -1'
# Snapshot de processos específicos (Chrome/Qutebrowser)
alias printbrowser='ps aux | grep -E "qutebrowser|chrome|QtWebEngine" | grep -v grep > ~/dl/browser_$(date +%Y%m%d_%H%M%S).txt && echo "Salvo em ~/dl/browser_*.txt"'

########################################
# PATH
########################################
export PATH="$HOME/.local/bin:$HOME/scr:/usr/local/bin:$PATH"

########################################
# Toolchains / Version Managers
########################################
set +h   # Disable command hashing

########################################
# Bash Completion
########################################
if [[ ! -v BASH_COMPLETION_VERSINFO && -f /usr/share/bash-completion/bash_completion ]]; then
  source /usr/share/bash-completion/bash_completion
fi

# Github
alias gs='git status'
alias ga='git add'
alias gc='git commit'
alias gp='git push'
alias gl='git log --oneline --graph --all'

alias github='cd ~/archbook && \
  rm -f ~/archbook/packages/packages_list && \
  yay -Qq > ~/archbook/packages/packages_list && \
  rsync -ah --progress ~/.bashrc . && \
  rsync -ah --progress ~/.inputrc . && \
  rsync -ah --progress ~/.config/hypr/ .config/hypr/ && \
  rsync -ah --progress ~/.config/waybar/ .config/waybar/ && \
  rsync -ah --progress ~/.config/dunst/ .config/dunst/ && \
  rsync -ah --progress ~/.config/fuzzel/ .config/fuzzel/ && \
  rsync -ah --progress ~/.config/foot/ .config/foot/ && \
  rsync -ah --progress ~/.config/lf/ .config/lf/ && \
  rsync -ah --progress ~/.config/wal/ .config/wal/ && \
  rsync -ah --progress ~/.config/imv/ .config/imv/ && \
  rsync -ah --progress ~/.config/mpv/ .config/mpv/ && \
  rsync -ah --progress ~/.config/qutebrowser/ .config/qutebrowser/ && \
  rsync -ah --progress ~/.local/bin/ .local/bin/ && \
  git add . && \
  git commit -m "sync: $(date +%Y-%m-%d)" && \
  git pull --rebase origin main && \
  git push && \
  cd -'

# --- AUTOMAÇÃO YOUTUBE-DL (YT-DLP) ---

# Baixar um único vídeo ou playlist como MP3 (Melhor Qualidade)
alias ytmp3='yt-dlp -x --audio-format mp3 --audio-quality 0 -o "%(title)s.%(ext)s"'

# Baixar um único vídeo em MP4 (Melhor Qualidade)
alias ytmp4='yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(title)s.%(ext)s"'

# Baixar Playlist INTEIRA como MP3 (Organizada por número em pasta própria)
alias ytlist-mp3='yt-dlp -x --audio-format mp3 -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"'

# Baixar Playlist INTEIRA como VÍDEO MP4 (Organizada por número em pasta própria)
alias ytlist-mp4='yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" -o "%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s"'

# Baixar por minuto
alias yttmp3='yt-dlp --download-sections "*01:00-02:00" -x --audio-format mp3 "URL"'

# Visualizar senha Wi Fi
alias senhawifi='nmcli -s device wifi show-password'
alias wifi-on='nmcli radio wifi on'

# Wallpaper atual
#alias wall='cat ~/.cache/ultimo_wallpaper.txt'

# Mirrors
#mirrors-br tenta mirrors brasileiros
alias mirrors-br="sudo reflector --country Brazil --latest 5 --sort rate --save /etc/pacman.d/mirrorlist && yay -Syyu"

#mirrors-global pega os 10 mais rapidos do mundo atualiza
alias mirrors-global="sudo reflector --latest 10 --sort rate --save /etc/pacman.d/mirrorlist && yay -Syyu"

#mirrors-fix so corrige os mirrors sem atualizar util pra diagnosticar
alias mirrors-fix="sudo reflector --country 'Brazil,United States,Germany' --latest 10 --sort rate --save /etc/pacman.d/mirrorlist"

# EspoCRM aliases
alias espocrm-up="cd ~/espocrm-docker && docker compose up -d"
alias espocrm-down="cd ~/espocrm-docker && docker compose down"
alias espocrm-logs="cd ~/espocrm-docker && docker compose logs -f"
alias espocrm-status="cd ~/espocrm-docker && docker compose ps"
alias espocrm="~/.local/bin/espocrm.sh"

