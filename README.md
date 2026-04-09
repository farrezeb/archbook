# Archbook — Dotfiles do MacBook A1278

## Hardware
- MacBook A1278 (2012)
- Arch Linux + Hyprland (Wayland)
- Intel HD 4000 + NVIDIA GeForce 320M

## Stack
- WM: Hyprland
- Bar: Waybar
- Terminal: Foot
- Shell: Bash
- Browser: Qutebrowser
- Launcher: Fuzzel
- Editor: Micro
- File Manager: lf
- Notificações: Dunst
- Cores: Pywal
- Senhas: pass + GPG

## Restaurar em uma nova instalação

### 1. Clonar o repositório
```bash
git clone git@github.com:farrezeb/archbook.git ~/archbook
```

### 1.1 Para salvar uma cópia da sua lista de pacotes atualmente instalada:
```bash
yay -Qq > packages_list
```

### 2. Instalar pacotes essenciais
```bash
sudo pacman -S hyprland waybar foot fuzzel dunst micro lf imv mpv \
  pass pass-otp wl-clipboard python-pywal qutebrowser
```

### 2.2 Reinstall yay
```bash
yay -S $(cat packages_list)
```

### 3. Aplicar dotfiles
```bash
cd ~/archbook
cp .bashrc ~/.bashrc
cp .inputrc ~/.inputrc
cp -r .config/* ~/.config/
cp -r .local/bin/* ~/.local/bin/
sudo cp -r wallpapers/* /usr/share/meus_wallpapers/
chmod +x ~/.local/bin/*
source ~/.bashrc
```

### 4. Restaurar chave GPG e senhas
```bash
gpg --import chave-gpg-backup.asc
git clone git@github.com:farrezeb/password-store.git ~/.password-store
```
