-- Decorations Configuration
hl.config({
    decoration = {
        rounding = 12,
        active_opacity = 0.9,
        inactive_opacity = 0.8,

        blur = {
            enabled = true,
            size = 6,
            passes = 3,
            new_optimizations = true,
            ignore_opacity = true,
        },

        shadow = {
            enabled = true,
            range = 15,
            render_power = 3,
            color = 0x44000000,
        },
    },
})
