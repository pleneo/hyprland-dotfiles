source /usr/share/cachyos-fish-config/cachyos-config.fish

# overwrite greeting
# potentially disabling fastfetch
#function fish_greeting
#    # smth smth
#end

fish_add_path /home/lenin/.spicetify

if status is-interactive
    if not set -q SSH_AUTH_SOCK
        # Inicia o ssh-agent se ele ainda não estiver em execução
        ssh-agent -c | source
    end

    keychain --quiet --eval $HOME/.ssh/id_ed25519_github 2>/dev/null | source

    # Faz o Fish usar o agente SSH carregado
    if test -f $HOME/.keychain/(hostname)-fish
        source $HOME/.keychain/(hostname)-fish 2>/dev/null
    end

    # Inicializar Starship Prompt
    if type -q starship
        starship init fish | source
    end
end

# bass source /home/lenin/.config/nvm/nvm.sh
export PATH="/home/lenin/.cmake-deps/cmake/linux/x64/bin:$PATH" # Added by JetBrains IDE


# Added by Antigravity CLI installer
set -gx PATH "/home/lenin/.local/bin" $PATH
