-- Input Configuration
hl.config({
    input = {
        kb_layout = "us",
        kb_variant = "intl",
        follow_mouse = 2,
        float_switch_override_focus = 2,
    },
})

hl.gesture({
    fingers = 4,
    direction = "horizontal",
    action = "workspace"
})

hl.gesture({
    fingers = 3,
    direction = "down",
    action = "close"
})

hl.gesture({
    fingers = 3,
    direction = "up",
    action = "fullscreen"
})

hl.gesture({
    fingers = 3,
    direction = "left",
    action = "float"
})
