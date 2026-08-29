-- Window Rules and Workspace Rules Configuration

-- Floating Rules
hl.window_rule({ name = "pavucontrol-float", match = { class = "org.pulseaudio.pavucontrol" }, float = true })
hl.window_rule({ name = "pip-float", match = { title = "Picture[- ]in[- ][Pp]icture" }, float = true })
hl.window_rule({ name = "file-dialogs-save", match = { title = "^Save File$" }, float = true })
hl.window_rule({ name = "file-dialogs-open", match = { title = "^Open File$" }, float = true })
hl.window_rule({ name = "blueman-float", match = { class = "blueman-manager" }, float = true })
hl.window_rule({ name = "portal-float", match = { class = "^(xdg-desktop-portal-.*)$" }, float = true })
hl.window_rule({ name = "polkit-float", match = { class = ".*polkit.*" }, float = true })
hl.window_rule({ name = "cachy-hello", match = { class = "CachyOSHello" }, float = true })
hl.window_rule({ name = "zenity-float", match = { class = "zenity" }, float = true })
hl.window_rule({ name = "steam-updater", match = { title = "^Steam - Self Updater$" }, float = true })

-- Opacity Rules
hl.window_rule({ name = "fm-opacity", match = { class = "^(thunar|nemo)$" }, opacity = 0.92 })
hl.window_rule({ name = "discord-opacity", match = { class = "^(discord|armcord|webcord)$" }, opacity = 0.96 })

-- Dragging fix for XWayland
hl.window_rule({
    name = "fix-xwayland-drags",
    match = { class = "^$", title = "^$", xwayland = true, float = true, fullscreen = false, pin = false },
    no_focus = true,
})

-- Spotify Dynamic Island Popup
hl.window_rule({
    name = "spotify-popup-rule",
    match = { class = ".*(spotify-island-popup|spotify_popup).*" },
    float = true,
    pin = true,
    rounding = 20,
    border_size = 2,
    move = "740 68",
    size = "440 148",
})

-- Smart Gaps Workspaces
hl.workspace_rule({ workspace = "w[tv1-10]", gaps_out = 5, gaps_in = 3 })
hl.workspace_rule({ workspace = "f[1]", gaps_out = 5, gaps_in = 3 })
