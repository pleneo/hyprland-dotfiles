-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃                 CachyOS Hyprland Lua Configuration          ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

-- Setup package.path for modular config
package.path = package.path .. ";" .. os.getenv("HOME") .. "/.config/hypr/lua/?.lua"

-- Helper globals for CLI and external dispatchers
_G.workspace = function(id)
    return hl.dsp.focus({ workspace = id })
end

_G.exec = function(cmd)
    return hl.dsp.exec_cmd(cmd)
end

-- Load Modules
require("monitors")
require("environment")
require("autostart")
require("input")
require("variables")
require("decorations")
require("animations")
require("keybinds")
require("windowrules")
