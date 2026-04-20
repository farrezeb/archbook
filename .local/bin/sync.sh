#!/usr/bin/env bash
set -euo pipefail

REPO="$HOME/archbook"
cd "$REPO"

# ─── Pacotes ────────────────────────────────────────────────────────────────
echo "→ Atualizando lista de pacotes..."
yay -Qq > ./packages/packages_list

# ─── Dotfiles soltos ────────────────────────────────────────────────────────
echo "→ Copiando dotfiles..."
rsync -ah ~/.bashrc .
rsync -ah ~/.inputrc .

# ─── Wallpapers ─────────────────────────────────────────────────────────────
echo "→ Copiando wallpapers..."
rsync -ah --delete /usr/share/meus_wallpapers/ wallpapers/

# ─── Pastas do .config ──────────────────────────────────────────────────────
echo "→ Copiando configs..."
for d in \
  hypr waybar dunst fuzzel foot lf wal imv mpv qutebrowser \
  bat btop zathura swaylock swayidle qt6ct nwg-look fastfetch micro; do
  if [ -d "$HOME/.config/$d" ]; then
    mkdir -p ".config/$d"
    rsync -ah --delete "$HOME/.config/$d/" ".config/$d/"
  fi
done

# ─── Arquivos soltos do .config ─────────────────────────────────────────────
echo "→ Copiando arquivos de config soltos..."
for f in mimeapps.list user-dirs.dirs; do
  [ -f "$HOME/.config/$f" ] && rsync -ah "$HOME/.config/$f" .config/
done

# ─── Scripts pessoais ───────────────────────────────────────────────────────
echo "→ Copiando scripts pessoais..."
rsync -ah --delete ~/.local/bin/ .local/bin/

# ─── EspoCRM — gera .env via pass ───────────────────────────────────────────
echo "→ Gerando .env do EspoCRM via pass..."
cat > "$HOME/espocrm-docker/.env" <<EOF
MARIADB_ROOT_PASSWORD=$(pass show "docker compose/mariadb_root_password" | head -1)
MARIADB_DATABASE=espocrm
MARIADB_USER=espocrm_fbx
MARIADB_PASSWORD=$(pass show "docker compose/mariadb_password" | head -1)
ESPOCRM_SITE_URL=http://archbook:8080
ESPOCRM_ADMIN_USERNAME=$(pass show espocrm/farrezeb | grep 'login:' | awk '{print $2}')
ESPOCRM_ADMIN_PASSWORD=$(pass show espocrm/farrezeb | head -1)
EOF

# ─── EspoCRM — sincroniza customizações e compose ───────────────────────────
echo "→ Copiando customizações do EspoCRM..."
mkdir -p espocrm/custom

if [ -d "$HOME/espocrm-docker/espocrm-data/custom" ]; then
  rsync -ah --delete "$HOME/espocrm-docker/espocrm-data/custom/" espocrm/custom/
else
  echo "  ⚠ Pasta custom do EspoCRM não encontrada, pulando..."
fi

if [ -f "$HOME/espocrm-docker/docker-compose.yml" ]; then
  rsync -ah "$HOME/espocrm-docker/docker-compose.yml" espocrm/
else
  echo "  ⚠ docker-compose.yml não encontrado, pulando..."
fi

# ─── Git ────────────────────────────────────────────────────────────────────
echo "→ Sincronizando com GitHub..."
git add .
git diff --cached --quiet && { echo "Nada a commitar."; exit 0; }
git commit -m "sync: $(date +%Y-%m-%d_%H:%M)"
git pull --rebase origin main
git push

echo "✓ Sync concluído."
