-- Keybindings Configuration
local mainMod = "SUPER"

-- Binds Behavior
hl.config({
    binds = {
        allow_workspace_cycles = true,
        workspace_back_and_forth = true,
        workspace_center_on = 1,
    },
})

-- Applications
hl.bind(mainMod .. " + RETURN", hl.dsp.exec_cmd("alacritty"))
hl.bind(mainMod .. " + SPACE", hl.dsp.exec_cmd("/home/lenin/.config/rofi/app-launcher.py"))
hl.bind(mainMod .. " + W", hl.dsp.exec_cmd("/home/lenin/Downloads/Wallpapers/gslapper-rofi.fish"))
hl.bind(mainMod .. " + E", hl.dsp.exec_cmd("thunar"))

-- Window Management
hl.bind(mainMod .. " + Q", hl.dsp.window.close())
hl.bind(mainMod .. " + V", hl.dsp.window.float({ action = "toggle" }))
hl.bind(mainMod .. " + F", hl.dsp.window.fullscreen({ state = "toggle" }))
hl.bind(mainMod .. " + Y", hl.dsp.window.pin())
hl.bind(mainMod .. " + J", hl.dsp.layout("togglesplit"))
hl.bind(mainMod .. " + P", hl.dsp.window.pseudo())

-- Clipboard Manager
hl.bind(mainMod .. " + ALT + V", hl.dsp.exec_cmd("/home/lenin/.config/rofi/cliphist.sh"))
hl.bind(mainMod .. " + C", hl.dsp.exec_cmd("/home/lenin/.config/rofi/cliphist.sh"))

-- Session / Waybar / Lock
hl.bind(mainMod .. " + SHIFT + M", hl.dsp.exec_cmd("loginctl terminate-user ''"))
hl.bind(mainMod .. " + L", hl.dsp.exec_cmd("hyprlock"))
hl.bind(mainMod .. " + O", hl.dsp.exec_cmd("killall -SIGUSR2 waybar"))

-- Gaps Toggle
hl.bind(mainMod .. " + SHIFT + G", hl.dsp.exec_cmd("hyprctl --batch 'keyword general:gaps_out 5;keyword general:gaps_in 3'"))
hl.bind(mainMod .. " + G", hl.dsp.exec_cmd("hyprctl --batch 'keyword general:gaps_out 0;keyword general:gaps_in 0'"))

-- Focus Navigation
hl.bind(mainMod .. " + left",  hl.dsp.focus({ direction = "left" }))
hl.bind(mainMod .. " + right", hl.dsp.focus({ direction = "right" }))
hl.bind(mainMod .. " + up",    hl.dsp.focus({ direction = "up" }))
hl.bind(mainMod .. " + down",  hl.dsp.focus({ direction = "down" }))

-- Move Active Window
hl.bind(mainMod .. " + SHIFT + left",  hl.dsp.window.move({ direction = "left" }))
hl.bind(mainMod .. " + SHIFT + right", hl.dsp.window.move({ direction = "right" }))
hl.bind(mainMod .. " + SHIFT + up",    hl.dsp.window.move({ direction = "up" }))
hl.bind(mainMod .. " + SHIFT + down",  hl.dsp.window.move({ direction = "down" }))

-- Groups
hl.bind(mainMod .. " + K", hl.dsp.group.toggle())
hl.bind(mainMod .. " + Tab", hl.dsp.group.next())

-- Workspaces 1-10
for i = 1, 10 do
    local key = i % 10
    hl.bind(mainMod .. " + " .. key, hl.dsp.focus({ workspace = i }))
    hl.bind(mainMod .. " + SHIFT + " .. key, hl.dsp.window.move({ workspace = i }))
    hl.bind(mainMod .. " + CTRL + " .. key, hl.dsp.window.move({ workspace = i }))
end

-- Workspace Scroll
hl.bind(mainMod .. " + mouse_down", hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + mouse_up",   hl.dsp.focus({ workspace = "e-1" }))
hl.bind(mainMod .. " + PERIOD",     hl.dsp.focus({ workspace = "e+1" }))
hl.bind(mainMod .. " + COMMA",      hl.dsp.focus({ workspace = "e-1" }))

-- Special Workspace
hl.bind(mainMod .. " + minus", hl.dsp.window.move({ workspace = "special" }))
hl.bind(mainMod .. " + equal", hl.dsp.workspace.toggle_special("special"))
hl.bind(mainMod .. " + F1",    hl.dsp.workspace.toggle_special("scratchpad"))

-- Mouse Window Drag & Resize
hl.bind(mainMod .. " + mouse:272", hl.dsp.window.drag(),   { mouse = true })
hl.bind(mainMod .. " + mouse:273", hl.dsp.window.resize(), { mouse = true })

-- Multimedia Controls
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("pactl set-sink-volume @DEFAULT_SINK@ +5% && pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\\d+(?=%)' | awk '{if($1>100) system(\"pactl set-sink-volume @DEFAULT_SINK@ 100%\")}' && pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\\d+(?=%)' | awk '{print $1}' | head -1 > /tmp/$HYPRLAND_INSTANCE_SIGNATURE.wob"), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("pactl set-sink-volume @DEFAULT_SINK@ -5% && pactl get-sink-volume @DEFAULT_SINK@ | grep -oP '\\d+(?=%)' | awk '{print $1}' | head -1 > /tmp/$HYPRLAND_INSTANCE_SIGNATURE.wob"), { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("amixer sset Master toggle | sed -En '/\\[on\\]/ s/.*[([0-9]+)%].*/\\1/ p; /\\[off\\]/ s/.*/0/p' | head -1 > /tmp/$HYPRLAND_INSTANCE_SIGNATURE.wob"), { locked = true, repeating = true })
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd("brightnessctl s +5%"),  { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd("brightnessctl s 5%-"), { locked = true, repeating = true })
hl.bind("XF86AudioPlay",        hl.dsp.exec_cmd("playerctl play-pause"), { locked = true })
hl.bind("XF86AudioNext",        hl.dsp.exec_cmd("playerctl next"),       { locked = true })
hl.bind("XF86AudioPrev",        hl.dsp.exec_cmd("playerctl previous"),   { locked = true })

-- Screenshots
hl.bind("Print", hl.dsp.exec_cmd("sh -c \"mkdir -p ~/Pictures/Screenshots && grim - | tee ~/Pictures/Screenshots/$(date +'%Y-%m-%d-%H%M%S').png | wl-copy\""))
hl.bind(mainMod .. " + Print", hl.dsp.exec_cmd("sh -c \"mkdir -p ~/Pictures/Screenshots && grim - | tee ~/Pictures/Screenshots/$(date +'%Y-%m-%d-%H%M%S').png | wl-copy\""))
hl.bind(mainMod .. " + SHIFT + Print", hl.dsp.exec_cmd("sh -c \"mkdir -p ~/Pictures/Screenshots && grim -g \\\"$(slurp)\\\" - | tee ~/Pictures/Screenshots/$(date +'%Y-%m-%d-%H%M%S').png | wl-copy\""))
hl.bind("SHIFT + Print", hl.dsp.exec_cmd("sh -c \"mkdir -p ~/Pictures/Screenshots && grim -g \\\"$(slurp)\\\" - | tee ~/Pictures/Screenshots/$(date +'%Y-%m-%d-%H%M%S').png | wl-copy\""))
