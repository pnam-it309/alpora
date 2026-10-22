pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property var data: ({ brightness: 100, brightnessAvailable: false, dnd: false, dndAvailable: false, nightLight: false, nightLightAvailable: false, powerProfilesAvailable: false, powerProfiles: [], powerProfile: "", powerDegraded: "", airplaneAvailable: false, airplane: false, airplaneHardwareBlocked: false, airplaneManaged: false })
    property string error: ""
    property var pending: []
    readonly property bool changingSettings: (worker.running && worker.command.length > 2 && worker.command[2] !== "status") || pending.some(item => item[2] !== "status")

    function request(action: string, value: string): void {
        const task = [Session.controller, "control", action];
        if (value.length)
            task.push(value);
        if (action === "status" && (pending.some(item => item[2] === "status") || (worker.running && worker.command[2] === "status"))) return;
        if (action === "brightness") root.pending = root.pending.filter(item => item[2] !== "brightness");
        root.pending = root.pending.concat([task]);
        if (!worker.running) pump.restart();
    }
    Timer {
        id: pump
        interval: 0
        onTriggered: {
            if (worker.running || !root.pending.length) return;
            const task = root.pending[0]; root.pending = root.pending.slice(1);
            if (task[2] !== "status") root.error = "";
            worker.command = task; worker.running = true;
        }
    }

    // External backlight keys or mako commands are reflected while the popup is open.
    // Closed panels perform no periodic work.
    Timer {
        interval: 2500
        repeat: true
        running: Session.quickSettingsOpen
        onTriggered: if (!worker.running && !root.pending.length) root.request("status", "")
    }

    Process {
        id: worker
        stdout: StdioCollector {
            onStreamFinished: {
                if (!text.trim()) return;
                try { root.data = JSON.parse(text); }
                catch (failure) { console.error("Invalid desktop status:", String(failure)); }
            }
        }
        stderr: StdioCollector {
            onStreamFinished: {
                if (text.trim()) {
                    root.error = text.trim().replace(/^poly-shell: /, "");
                    console.error(root.error);
                }
            }
        }
        onExited: exitCode => {
            if (exitCode !== 0 && worker.command[2] !== "status" && !root.pending.some(item => item[2] === "status"))
                root.pending = root.pending.concat([[Session.controller, "control", "status"]]);
            if (root.pending.length) pump.restart();
        }
    }
}
