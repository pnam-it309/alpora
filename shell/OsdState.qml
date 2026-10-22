pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Hyprland

Singleton {
    id: root
    property bool opened: false
    property string screenName: ""
    property string kind: "volume"
    property real value: 0
    property bool muted: false
    readonly property string title: kind === "brightness" ? "Яркость" : kind === "microphone" ? "Микрофон" : "Громкость"
    readonly property string symbol: kind === "brightness" ? "sun" : kind === "microphone" ? (muted ? "microphone-muted" : "microphone") : (muted ? "muted" : "volume")
    function show(next: string, amount: real, silenced: bool): void {
        if (!["volume", "microphone", "brightness"].includes(next) || !isFinite(amount)) return;
        const monitor = Hyprland.focusedMonitor;
        screenName = monitor ? monitor.name : (Quickshell.screens.length ? Quickshell.screens[0].name : "");
        kind = next; value = Math.max(0, amount); muted = silenced;
        opened = true; expiry.restart();
    }
    Timer { id: expiry; interval: 1500; onTriggered: root.opened = false }
}
