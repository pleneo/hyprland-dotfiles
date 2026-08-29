-- Variables and Layout with Dynamic Pywal Colors
local home = os.getenv("HOME")
local colors_file = home .. "/.cache/wal/colors.json"

local col_active1 = "rgba(33ccffee)"
local col_active2 = "rgba(00ff99ee)"
local col_inactive = "rgba(202028aa)"

local f = io.open(colors_file, "r")
if f then
    local content = f:read("*all")
    f:close()
    local c2 = content:match('"color2"%s*:%s*"#([%x%w]+)"')
    local c4 = content:match('"color4"%s*:%s*"#([%x%w]+)"')
    local c0 = content:match('"color0"%s*:%s*"#([%x%w]+)"')
    if c2 and c4 then
        col_active1 = "rgba(" .. c2 .. "ee)"
        col_active2 = "rgba(" .. c4 .. "ee)"
    end
    if c0 then
        col_inactive = "rgba(" .. c0 .. "aa)"
    end
end

hl.config({
    general = {
        gaps_in = 3,
        gaps_out = 5,
        border_size = 3,
        col = {
            active_border = { colors = { col_active1, col_active2 }, angle = 45 },
            inactive_border = col_inactive,
        },
        layout = "dwindle",
        snap = {
            enabled = true,
        },
    },

    misc = {
        font_family = "Fira Sans",
        splash_font_family = "Fira Sans",
        disable_hyprland_logo = true,
        enable_swallow = true,
        swallow_regex = "^(nautilus|nemo|thunar|btrfs-assistant.)$",
        focus_on_activate = true,
        vrr = 2,
    },

    render = {
        direct_scanout = true,
    },

    dwindle = {
        special_scale_factor = 0.8,
        preserve_split = true,
    },

    master = {
        new_status = "master",
        special_scale_factor = 0.8,
    },
})
