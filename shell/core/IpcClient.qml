pragma Singleton
import QtQuick
import ".."
import Quickshell
import Quickshell.Io

Singleton {
    id: root

    property string lastError: ""
    property bool busy: queue.length > 0 || currentTask !== null
    property int queueLength: queue.length
    readonly property bool socketConnected: ipcSocket.connected

    signal actionCompleted(string subcommand, string action, bool success, var result, string error)
    signal errorOccurred(string message)
    signal eventReceived(string eventName, var eventData)

    // Internal task queue for CLI fallback
    property var queue: []
    property var currentTask: null

    // Socket RPC state
    property var pendingRequests: ({})
    property int nextReqId: 1

    function request(action: string, params: var, callback: var, originSubcommand: var, originAction: var): void {
        const cb = (typeof callback === "function") ? callback : null;
        if (!ipcSocket.connected) {
            // Intelligent CLI fallback when socket is disconnected
            const p = (params && typeof params === "object") ? params : {};
            if (action === "apps.snapshot") {
                send("running-apps", ["snapshot", JSON.stringify(p.windows || [])], cb);
                return;
            }
            if (action === "apps.signal") {
                send("running-apps", ["signal", String(p.pid || 0), String(p.start_ticks || 0), String(p.sig || "TERM")], cb);
                return;
            }
            if (action === "widgets.weather") {
                send("widgets", ["weather"], cb);
                return;
            }
            if (action === "metrics.snapshot") {
                send("widgets", ["metrics"], cb);
                return;
            }
            if (action === "organizer.request") {
                send("organizer", [p.action || "get", JSON.stringify(p.payload || {})], cb);
                return;
            }
            if (action === "timeline.get") {
                send("timeline", ["get"], cb);
                return;
            }
            if (action === "timeline.set") {
                send("timeline", ["set", JSON.stringify(p.payload || {})], cb);
                return;
            }
            if (action === "desktop.control") {
                const act = p.action || "status";
                const valArgs = (p.value !== undefined && p.value !== null) ? [act, String(p.value)] : [act];
                send("control", valArgs, cb);
                return;
            }
            if (action === "desktop.status") {
                send("control", ["status"], cb);
                return;
            }
            if (action === "window.cascade") {
                send("control", ["cascade"], cb);
                return;
            }
            if (action === "window.float_toggle") {
                send("control", ["float-toggle"], cb);
                return;
            }
            if (action === "arcade.scores") {
                send("arcade", ["scores"], cb);
                return;
            }
            if (action === "arcade.record") {
                send("arcade", ["record", String(p.game || ""), String(p.score || 0)], cb);
                return;
            }

            // Fallback via CLI ipc command for generic endpoints
            const pStr = (params !== undefined && params !== null) ? (typeof params === "string" ? params : JSON.stringify(params)) : "{}";
            send("ipc", [action, pStr], cb);
            return;
        }

        const reqId = root.nextReqId++;
        root.pendingRequests[reqId] = {
            action: action,
            subcommand: originSubcommand || "socket",
            subaction: originAction || action,
            callback: cb,
            timestamp: Date.now()
        };

        const payload = JSON.stringify({
            id: reqId,
            action: action,
            params: params || {}
        });

        try {
            ipcSocket.write(payload + "\n");
            ipcSocket.flush();
        } catch (sockErr) {
            delete root.pendingRequests[reqId];
            if (cb) cb(null, String(sockErr));
        }
    }

    function send(subcommand: string, args: var, callback: var): void {
        const cmdArgs = Array.isArray(args) ? args : (args !== undefined && args !== null && String(args).length > 0 ? [String(args)] : []);
        const cb = (typeof callback === "function") ? callback : null;

        // Route to socket RPC if connected and mapping exists
        if (ipcSocket.connected) {
            if (subcommand === "ipc" && cmdArgs.length > 0) {
                let parsedParams = {};
                if (cmdArgs.length > 1) {
                    try { parsedParams = JSON.parse(cmdArgs[1]); } catch (_) { parsedParams = cmdArgs[1]; }
                }
                request(cmdArgs[0], parsedParams, cb, "ipc", cmdArgs[0]);
                return;
            }
            if (subcommand === "widgets") {
                if (cmdArgs[0] === "metrics") {
                    request("metrics.snapshot", {}, cb, "widgets", "metrics");
                    return;
                }
                if (cmdArgs[0] === "weather") {
                    request("widgets.weather", {}, cb, "widgets", "weather");
                    return;
                }
            }
            if (subcommand === "arcade" && cmdArgs[0] === "scores") {
                request("arcade.scores", {}, cb, "arcade", "scores");
                return;
            }
            if (subcommand === "control") {
                if (cmdArgs[0] === "cascade") {
                    request("window.cascade", {}, cb, "control", "cascade");
                    return;
                }
                if (cmdArgs[0] === "float-toggle") {
                    request("window.float_toggle", {}, cb, "control", "float-toggle");
                    return;
                }
                const act = cmdArgs.length > 0 ? cmdArgs[0] : "status";
                const val = cmdArgs.length > 1 ? cmdArgs[1] : null;
                request("desktop.control", { action: act, value: val }, cb, "control", act);
                return;
            }
            if (subcommand === "organizer") {
                const act = cmdArgs.length > 0 ? cmdArgs[0] : "get";
                let payload = {};
                if (cmdArgs.length > 1) {
                    try { payload = JSON.parse(cmdArgs[1]); } catch (_) { payload = cmdArgs[1]; }
                }
                request("organizer.request", { action: act, payload: payload }, cb, "organizer", act);
                return;
            }
            if (subcommand === "timeline") {
                const act = cmdArgs.length > 0 ? cmdArgs[0] : "get";
                if (act === "get") {
                    request("timeline.get", {}, cb, "timeline", "get");
                    return;
                }
                if (act === "set") {
                    let payload = {};
                    if (cmdArgs.length > 1) {
                        try { payload = JSON.parse(cmdArgs[1]); } catch (_) { payload = cmdArgs[1]; }
                    }
                    request("timeline.set", { payload: payload }, cb, "timeline", "set");
                    return;
                }
            }
        }

        // Deduplication for high-frequency control actions in CLI queue
        if (subcommand === "control" && cmdArgs.length > 0) {
            const act = cmdArgs[0];
            if (act === "brightness" || act === "status" || act === "ui-scale") {
                queue = queue.filter(t => !(t.subcommand === "control" && t.args.length > 0 && t.args[0] === act));
            }
        }

        const task = {
            subcommand: subcommand,
            args: cmdArgs,
            callback: cb,
            timestamp: Date.now()
        };

        queue.push(task);
        if (!worker.running) {
            pump.restart();
        }
    }

    function exec(commandList: var): void {
        if (!commandList || !commandList.length) return;
        try {
            Quickshell.execDetached(commandList);
        } catch (e) {
            const msg = String(e);
            console.error("IpcClient.exec failed:", msg);
            root.lastError = msg;
            root.errorOccurred(msg);
        }
    }

    function handleSocketMessage(line: string): void {
        const trimmed = line.trim();
        if (!trimmed) return;
        try {
            const msg = JSON.parse(trimmed);
            if (msg.event) {
                root.eventReceived(msg.event, msg.data || {});
                if (msg.domain && String(msg.domain).length > 0 && String(msg.event).indexOf(msg.domain + ".") !== 0) {
                    root.eventReceived(msg.domain + "." + msg.event, msg.data || {});
                }
                return;
            }
            if (msg.id !== undefined && root.pendingRequests[msg.id]) {
                const req = root.pendingRequests[msg.id];
                delete root.pendingRequests[msg.id];
                const success = !!msg.success;
                const result = msg.data !== undefined ? msg.data : null;
                const errText = success ? "" : (msg.error || "RPC error");

                if (req.callback) {
                    try {
                        req.callback(result, errText);
                    } catch (cbErr) {
                        console.error("IpcClient socket callback error:", String(cbErr));
                    }
                }
                root.actionCompleted(req.subcommand || "socket", req.subaction || req.action || "", success, result, errText);
            }
        } catch (err) {
            console.error("IpcClient socket parse error:", String(err));
        }
    }

    Socket {
        id: ipcSocket
        path: Session.socketPath
        connected: false
        parser: SplitParser {
            splitMarker: "\n"
            onRead: data => root.handleSocketMessage(data)
        }
        onConnectionStateChanged: {
            if (!connected) {
                reconnectTimer.restart();
            }
        }
        onError: err => {
            reconnectTimer.restart();
        }
    }

    Timer {
        id: reconnectTimer
        interval: 2500
        repeat: false
        onTriggered: {
            if (!ipcSocket.connected && Session.socketPath.length > 0) {
                ipcSocket.connected = true;
            }
        }
    }

    Timer {
        id: timeoutCleaner
        interval: 5000
        repeat: true
        running: true
        onTriggered: {
            const now = Date.now();
            const expiredIds = [];
            for (const id in root.pendingRequests) {
                if (now - root.pendingRequests[id].timestamp > 10000) {
                    expiredIds.push(id);
                }
            }
            for (let i = 0; i < expiredIds.length; i++) {
                const id = expiredIds[i];
                const req = root.pendingRequests[id];
                delete root.pendingRequests[id];
                if (req.callback) {
                    try { req.callback(null, "Request timeout"); } catch (_) {}
                }
            }
        }
    }

    Timer {
        id: pump
        interval: 0
        onTriggered: {
            if (worker.running || !root.queue.length) return;
            root.currentTask = root.queue.shift();
            root.queueLength = root.queue.length;

            const fullCommand = [Session.controller, root.currentTask.subcommand].concat(root.currentTask.args);
            worker.command = fullCommand;
            worker.running = true;
        }
    }

    Process {
        id: worker
        stdout: StdioCollector {
            id: outCollector
        }
        stderr: StdioCollector {
            id: errCollector
        }
        onExited: exitCode => {
            const task = root.currentTask;
            const stdoutText = outCollector.text.trim();
            const stderrText = errCollector.text.trim().replace(/^poly-shell:\s*/, "");
            const success = exitCode === 0;

            let parsedResult = null;
            if (stdoutText.length > 0) {
                try {
                    parsedResult = JSON.parse(stdoutText);
                } catch (_) {
                    parsedResult = stdoutText;
                }
            }

            if (!success && stderrText.length > 0) {
                root.lastError = stderrText;
                root.errorOccurred(stderrText);
                console.error("IpcClient error [" + (task ? task.subcommand : "") + "]:", stderrText);
            }

            if (task && task.callback) {
                try {
                    task.callback(parsedResult, success ? "" : (stderrText || "Exit code " + exitCode));
                } catch (cbErr) {
                    console.error("IpcClient callback error:", String(cbErr));
                }
            }

            if (task) {
                const actionName = task.args.length > 0 ? task.args[0] : "";
                root.actionCompleted(task.subcommand, actionName, success, parsedResult, success ? "" : stderrText);
            }

            root.currentTask = null;
            if (root.queue.length > 0) {
                pump.restart();
            }
        }
    }

    Component.onCompleted: {
        if (Session.socketPath.length > 0) {
            ipcSocket.connected = true;
        }
    }
}
