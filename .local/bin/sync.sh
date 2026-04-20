#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/archbook"
cd "$REPO"

echo "→ Atualizando lista de pacotes..."
yay -Qq > ./packages/packages_list

echo "→ Copiando dotfiles..."
rsync -ah ~/.bashrc .
rsync -ah ~/.inputrc .

echo "→ Copiando wallpapers..."
rsync -ah --delete /usr/share/meus_wallpapers/ wallpapers/

echo "→ Copiando configs..."
for d in hypr waybar dunst fuzzel foot lf wal imv mpv qutebrowser; do
  [ -d "$HOME/.config/$d" ] && \
    rsync -ah --delete "$HOME/.config/$d/" ".config/$d/"
done

echo "→ Copiando scripts pessoais..."
rsync -ah --delete ~/.local/bin/ .local/bin/

echo "→ Sincronizando com GitHub..."
git add .
git diff --cached --quiet && { echo "Nada a commitar."; exit 0; }
git commit -m "sync: $(date +%Y-%m-%d_%H:%M)"
git pull --rebase origin main
git push
echo "✓ Sync concluído."
