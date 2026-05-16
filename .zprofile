# Iniciar o Hyprland automaticamente ao logar no TTY1
#if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
#    exec Hyprland
#fi


if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    export XDG_CURRENT_DESKTOP=Hyprland
    export XDG_SESSION_TYPE=wayland
    export XDG_SESSION_DESKTOP=Hyprland
    # O comando abaixo inicia o Hyprland vinculado ao barramento de mensagens correto
#    exec dbus-run-session Hyprland

    exec start-hyprland
fi

