pragma Singleton
import QtQuick
import ".."
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property var data: ({events: [], tasks: [], note: "", timer: {duration: 1500, remaining: 1500, endsAt: 0}})
    property string error: ""
    property bool loaded: false
    property var queue: []
    property double now: Date.now() / 1000
    readonly property bool running: data.timer.endsAt > 0
    readonly property int remaining: Math.max(0, running ? Math.ceil(data.timer.endsAt - now) : data.timer.remaining)
    readonly property string countdown: String(Math.floor(remaining / 60)).padStart(2, "0") + ":" + String(remaining % 60).padStart(2, "0")
    readonly property real progress: 1 - remaining / Math.max(1, data.timer.duration)
    readonly property bool busy: worker.running || queue.length > 0
    property var fired: ({})
    signal saved(string action)
    signal reminder(var event)
    // Local, offline reminders: notify once when an event enters its lead window.
    function checkReminders(): void {
        const stamp = Date.now();
        for (const item of (data.events || [])) {
            if (item.remind === undefined || fired[item.id]) continue;
            const start = new Date(item.date + "T" + item.time + ":00").getTime();
            if (isNaN(start) || stamp < start - item.remind * 60000 || stamp > start + 60000) continue;
            fired[item.id] = true;
            Quickshell.execDetached(["notify-send", "-a", "ALPORA", "-i", "appointment-soon", item.title,
                                     item.time + (item.remind > 0 ? " · " + I18n.trWith("day.reminder_in", {minutes: item.remind}) : "")]);
            reminder(item);
        }
    }
    function request(action: string, payload: var): void {
        if (IpcClient.socketConnected) {
            IpcClient.request("organizer.request", { action: action, payload: payload || {} }, (res, err) => {
                if (err || !res) {
                    root.error = err || I18n.tr("day.error_read");
                } else {
                    root.data = res;
                    root.now = Date.now() / 1000;
                    root.loaded = true;
                    root.error = "";
                    root.checkReminders();
                    root.saved(action);
                }
            });
            return;
        }
        const task = [Session.controller, "organizer", action, JSON.stringify(payload || {})];
        if (action === "note") root.queue = root.queue.filter(item => item[2] !== "note");
        root.queue = root.queue.concat([task]);
        if (!worker.running) pump.restart();
    }
    function dateKey(date: date): string {
        return Qt.formatDateTime(date, "yyyy-MM-dd");
    }
    function events(date: date): var {
        return data.events.filter(item => item.date === dateKey(date)).sort((a, b) => a.time.localeCompare(b.time));
    }
    function tasks(date: date): var { return data.tasks.filter(item => item.date === dateKey(date)); }
    function exportIcs(filePath: string): void {
        const path = filePath || (Quickshell.env("HOME") + "/alpora-planner.ics");
        request("export", { file: path });
    }
    function importIcs(filePath: string): void {
        const path = filePath || (Quickshell.env("HOME") + "/alpora-planner.ics");
        request("import", { file: path });
    }
    onSaved: action => {
        if (action === "export") {
            Quickshell.execDetached(["notify-send", "-a", "ALPORA", "-i", "document-export", I18n.tr("day.export_ics"), I18n.tr("day.ics_exported")]);
        } else if (action === "import") {
            Quickshell.execDetached(["notify-send", "-a", "ALPORA", "-i", "document-import", I18n.tr("day.import_ics"), I18n.tr("day.ics_imported")]);
        }
    }
    Timer {
        id: pump
        interval: 0
        onTriggered: {
            if (worker.running || !root.queue.length) return;
            const task = root.queue[0]; root.queue = root.queue.slice(1);
            root.error = ""; worker.command = task; worker.running = true;
        }
    }
    Timer {
        id: countdownTick
        interval: 1000; repeat: true; running: root.running
        onTriggered: {
            root.now = Date.now() / 1000;
            if (root.remaining === 0 && !worker.running) root.request("get", {});
        }
    }
    Connections {
        target: ClockState
        function onDateChanged(): void { root.checkReminders(); }
        function onResumed(): void {
            root.now = Date.now() / 1000;
            if (root.running) countdownTick.restart();
            if (root.running && root.remaining === 0) root.request("get", {});
        }
    }
    Process {
        id: worker
        stdout: StdioCollector {
            onStreamFinished: {
                if (!text.trim()) return;
                try { root.data = JSON.parse(text); root.now = Date.now() / 1000; root.loaded = true; root.checkReminders(); root.saved(worker.command[2]); }
                catch (_) { root.error = I18n.tr("day.error_read"); }
            }
        }
        stderr: StdioCollector {
            onStreamFinished: { if (text.trim()) root.error = text.trim().replace(/^poly-shell: /, ""); }
        }
        onExited: {
            if (root.queue.length) pump.restart();
        }
    }
    Component.onCompleted: request("get", {})
}
