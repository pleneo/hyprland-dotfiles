-- ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
-- ┃                 CachyOS Hyprland Lua Configuration          ┃
-- ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

-- Setup package.path for modular config
package.path = package.path .. ";" .. os.getenv("HOME") .. "/.config/hypr/lua/?.lua"

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
