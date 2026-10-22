-- ALPORA managed session v1
-- Defaults for a complete session; individual settings remain in ~/.config/poly-shell.
local config = os.getenv("XDG_CONFIG_HOME") or (os.getenv("HOME") .. "/.config")
local root = config .. "/hypr/"
local launcher = os.getenv("HOME") .. "/.local/bin/poly-shell"
local state = (os.getenv("XDG_STATE_HOME") or (os.getenv("HOME") .. "/.local/state")) .. "/poly-shell/"
local function quoted(value) return "'" .. value:gsub("'", "'\\''") .. "'" end
local function run(key, command, flags)
    hl.bind(key, hl.dsp.exec_cmd(command), flags or {})
end
hl.monitor({output="", mode="preferred", position="auto", scale=1})
hl.env("QT_QPA_PLATFORMTHEME", "gtk3")
hl.env("QT_STYLE_OVERRIDE", "Fusion")
hl.env("XDG_CURRENT_DESKTOP", "Hyprland")
hl.env("XCURSOR_THEME", "Bibata-Modern-Ice")
hl.env("XCURSOR_SIZE", "24")
hl.config({
    general={layout="dwindle",gaps_in=5,gaps_out=12,border_size=2,resize_on_border=true},
    decoration={rounding=20,blur={enabled=false,size=3,passes=1,noise=0.012},
        shadow={enabled=true,range=12,render_power=3,color=0x55121819}},
    animations={enabled=true},
    input={kb_layout="us,ru",kb_options="grp:win_space_toggle",follow_mouse=1,
        touchpad={natural_scroll=true,tap_to_click=true}},
    dwindle={preserve_split=true},
    misc={disable_hyprland_logo=true,force_default_wallpaper=0},
    cursor={enable_hyprcursor=false},
})
hl.layer_rule({name="alpora-glass",match={namespace="^poly-shell(-.*)?$"},blur=true,ignore_alpha=0.2,no_anim=true})
hl.layer_rule({name="alpora-notifications",match={namespace="^notifications$"},blur=true,ignore_alpha=0.2})
-- Starts only in this Hyprland session. No machine-wide desktop replacement.
hl.on("hyprland.start", function()
    hl.exec_cmd("systemctl --user import-environment WAYLAND_DISPLAY DISPLAY HYPRLAND_INSTANCE_SIGNATURE XDG_CURRENT_DESKTOP XCURSOR_THEME XCURSOR_SIZE")
    hl.exec_cmd("dbus-update-activation-environment --systemd WAYLAND_DISPLAY DISPLAY HYPRLAND_INSTANCE_SIGNATURE XDG_CURRENT_DESKTOP XCURSOR_THEME XCURSOR_SIZE")
    hl.exec_cmd("systemctl --user start hyprpolkitagent.service")
    hl.exec_cmd("mako -c " .. quoted(state .. "mako-theme.conf"))
    hl.exec_cmd("hypridle -c " .. quoted(root .. "alpora-hypridle.conf"))
    hl.exec_cmd(quoted(launcher) .. " start")
    hl.exec_cmd(quoted(launcher) .. " wallpaper")
end)
run("SUPER + Return", "foot")
run("SUPER + Q", "foot")
run("SUPER + E", "nautilus --new-window")
run("SUPER + B", "firefox")
run("SUPER + L", "hyprlock -c " .. quoted(root .. "hyprlock.conf"))
run("SUPER + N", "nm-connection-editor")
run("SUPER + A", "pavucontrol")
run("SUPER + SHIFT + E", "hyprshutdown")
run("Print", quoted(root .. "screenshot.sh"))
for key, target in pairs({R="launcher",I="quick-settings",M="notifications",V="clipboard",Tab="overview"}) do
    hl.bind("SUPER + " .. key,hl.dsp.global("poly-shell:"..target))
end
hl.bind("SUPER + C",hl.dsp.window.close())
hl.bind("SUPER + SHIFT + V",hl.dsp.window.float({action="toggle"}))
hl.bind("SUPER + J",hl.dsp.layout("togglesplit"))
for _,direction in ipairs({"left","right","up","down"}) do
    hl.bind("SUPER + "..direction,hl.dsp.focus({direction=direction}))
end
for i=1,10 do
    hl.bind("SUPER + "..(i%10),hl.dsp.focus({workspace=i}))
    hl.bind("SUPER + SHIFT + "..(i%10),hl.dsp.window.move({workspace=i}))
end
hl.bind("SUPER + mouse:272",hl.dsp.window.drag(),{mouse=true})
hl.bind("SUPER + mouse:273",hl.dsp.window.resize(),{mouse=true})
hl.gesture({fingers=3,direction="horizontal",action="workspace"})
local overviewGesture = dofile(root .. "alpora-overview.lua")
hl.gesture({fingers=3,direction="up",action=overviewGesture("up")})
hl.gesture({fingers=3,direction="down",action=overviewGesture("down")})
local palette = io.open(root .. "poly-shell-theme.lua", "r")
if palette then palette:close(); dofile(root .. "poly-shell-theme.lua") end
run("XF86AudioRaiseVolume","wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+",{locked=true,repeating=true})
run("XF86AudioLowerVolume","wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-",{locked=true,repeating=true})
run("XF86AudioMute","wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle",{locked=true})
run("XF86AudioMicMute","wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle",{locked=true})
run("XF86MonBrightnessUp","brightnessctl set +5%",{locked=true,repeating=true})
run("XF86MonBrightnessDown","brightnessctl set 5%-",{locked=true,repeating=true})
run("XF86AudioPlay","playerctl play-pause",{locked=true})
run("XF86AudioNext","playerctl next",{locked=true})
run("XF86AudioPrev","playerctl previous",{locked=true})
