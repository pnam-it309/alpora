pragma Singleton
import QtQuick
import ".."
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property bool enabled: false
    property string folder: ""
    property string effectiveFolder: ""
    property int intervalMinutes: 15
    property bool shuffle: false
    property string error: ""
    property string action: ""
    property var response: null
    readonly property bool busy: worker.running
    function load(): void { request("slideshow-get", {}); }
    function configure(change: var): void { request("slideshow-set", change); }
    function next(): void { request("slideshow-next", {}); }
    function request(name: string, payload: var): void {
        if (busy) return;
        root.action = name; root.response = null; root.error = "";
        worker.command = [Session.controller, "theme", name, JSON.stringify(payload)];
        worker.running = true;
    }
    Timer {
        interval: Math.max(1, root.intervalMinutes) * 60000
        repeat: true
        running: root.enabled
        onTriggered: root.next()
    }
    Process {
        id: worker
        stdout: StdioCollector { onStreamFinished: { try { root.response = JSON.parse(text); } catch (_) { root.error = I18n.tr("theme.error_collection"); } } }
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.error = text.trim().replace(/^poly-shell: /, "") }
        onExited: exitCode => {
            if (exitCode !== 0 || !root.response) { if (!root.error) root.error = I18n.tr("theme.error_action"); return; }
            const r = root.response;
            if (root.action === "slideshow-next") { ThemeState.refresh(); return; }
            root.enabled = r.enabled === true;
            root.folder = r.folder || "";
            root.effectiveFolder = r.effectiveFolder || "";
            root.intervalMinutes = r.intervalMinutes || 15;
            root.shuffle = r.shuffle === true;
        }
    }
    Component.onCompleted: load()
}
