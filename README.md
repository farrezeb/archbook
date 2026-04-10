# Archbook — (Fernando Bezerra <https://fernandobezerra.xyz>'s dotfiles)

## Hardware
- MacBook A1278 (2012)
- Arch Linux + Hyprland (Wayland)
- Intel HD 4000 + NVIDIA GeForce 320M

 PC: MacBook A1278
󰣇 OS: Arch Linux x86_64
 Kernel: Linux 6.18.21-1-lts
󰃭 Installed: 01/12/2025
 WM: Hyprland 0.54.3 (Wayla)
 Term: foot 1.26.1
 Shell: bash 5.3.9
 CPU: Intel(R) Core(TM) i5-z
 RAM: 16 GiB
󰋊 Disk: 62.78 GiB / 930.51 Gs

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
- Video: Mpv
- Imagens: Imv

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
