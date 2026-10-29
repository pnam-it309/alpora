pragma Singleton
import QtQuick
import Quickshell

Singleton {
    id: root

    property bool active: false
    property string targetScreen: ""

    function open(screen: string): void {
        targetScreen = screen || (Quickshell.screens.length ? Quickshell.screens[0].name : "");
        active = true;
    }

    function close(): void {
        active = false;
    }

    function toggle(screen: string): void {
        if (active) close();
        else open(screen);
    }

    function execute(action: string): void {
        close();
        if (action === "lock") {
            const home = Quickshell.env("HOME") || "";
            Quickshell.execDetached(["hyprlock", "-c", home + "/.config/hypr/hyprlock.conf"]);
        } else if (action === "suspend") {
            Quickshell.execDetached(["systemctl", "suspend"]);
        } else if (action === "reboot") {
            Quickshell.execDetached(["systemctl", "reboot"]);
        } else if (action === "poweroff") {
            Quickshell.execDetached(["systemctl", "poweroff"]);
        } else if (action === "logout") {
            const comp = WindowTracker.compositor;
            if (comp === "sway") Quickshell.execDetached(["swaymsg", "exit"]);
            else if (comp === "niri") Quickshell.execDetached(["niri", "msg", "action", "quit"]);
            else Quickshell.execDetached(["hyprctl", "dispatch", "exit"]);
        }
    }
}
