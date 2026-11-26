pragma Singleton
import QtQuick
import ".."
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property var items: []
    property var localImages: []
    property var localFolders: []
    property string activeFolder: ""
    property string selectedId: "alpine"
    property string baseId: "alpine"
    property bool automatic: true
    property bool baseAutomatic: true
    property bool loaded: false
    property string error: ""
    property string message: ""
    property var response: null
    property string action: ""
    property bool wallpaperTransitioning: false
    Timer { id: wallpaperHandoff; interval: 1500; onTriggered: root.wallpaperTransitioning = false }
    signal pickUnavailable()
    readonly property bool busy: worker.running
    readonly property bool dirty: loaded && (selectedId !== baseId || automatic !== baseAutomatic)
    readonly property var selected: items.find(item => item.id === selectedId) || null
    function refresh(): void { if (!busy) request("list", activeFolder ? {folder: activeFolder} : {}); }
    function browseFolder(folder: string): void {
        if (busy) return;
        activeFolder = folder;
        request("list", folder ? {folder: folder} : {});
    }
    function select(ident: string): void { if (!busy && items.some(item => item.id === ident)) { selectedId = ident; error = ""; message = ""; } }
    function cancel(): void { if (!busy) { selectedId = baseId; automatic = baseAutomatic; error = ""; message = ""; } }
    function apply(): void { if (!busy && selected && dirty) request("apply", {id: selectedId, colorsFromWallpaper: automatic}); }
    function importImage(path: string): void {
        if (!busy && path.trim().length > 0) {
            request("import", {image: path.trim(), apply: true, colorsFromWallpaper: automatic});
        }
    }
    function pickImage(): void { if (!busy) request("pick", {}); }
    function removeCustom(ident: string): void {
        if (!busy && ident.startsWith("custom-")) {
            request("remove", {id: ident});
        }
    }
    function request(next: string, payload: var): void {
        if (next === "apply") {
            wallpaperHandoff.stop();
            root.wallpaperTransitioning = payload.id === "timeline" && !!payload.transition && !Motion.reduced;
        }
        root.action = next; root.response = null; root.error = ""; root.message = "";
        worker.command = [Session.controller, "theme", next, JSON.stringify(payload)];
        worker.running = true;
    }
    Process {
        id: worker
        stdout: StdioCollector { onStreamFinished: { try { root.response = JSON.parse(text); } catch (_) { root.error = I18n.tr("theme.error_collection"); } } }
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.error = text.trim().replace(/^poly-shell: /, "") }
        onExited: exitCode => {
            if (exitCode !== 0 || !root.response) { root.wallpaperTransitioning = false; if (!root.error) root.error = I18n.tr("theme.error_action"); return; }
            if (root.wallpaperTransitioning) wallpaperHandoff.restart();
            if (root.action === "pick") {
                const picked = root.response.path || "";
                if (root.response.unavailable) root.pickUnavailable();
                else if (picked) Qt.callLater(() => root.importImage(picked));
                return;
            }
            const keepDraft = root.loaded && root.dirty && root.action === "list";
            root.items = root.response.items || [];
            if (Array.isArray(root.response.localImages)) root.localImages = root.response.localImages;
            if (Array.isArray(root.response.localFolders)) root.localFolders = root.response.localFolders;
            if (typeof root.response.activeFolder === "string") root.activeFolder = root.response.activeFolder;
            root.baseId = root.response.selected;
            root.baseAutomatic = root.response.colorsFromWallpaper;
            if (!keepDraft) { root.selectedId = root.response.imported || root.baseId; root.automatic = root.baseAutomatic; }
            root.loaded = true;
            if (root.action === "apply") root.message = I18n.tr("theme.applied");
            if (root.action === "import") root.message = I18n.tr("theme.applied");
        }
    }
    Component.onCompleted: refresh()
    IpcHandler {
        target: "themes"
        function select(id: string): void { root.select(id); }
        function apply(): void { root.apply(); }
        function cancel(): void { root.cancel(); }
        function refresh(): void { root.refresh(); }
        function status(): string { return JSON.stringify({selected: root.selectedId, saved: root.baseId, automatic: root.automatic, dirty: root.dirty, busy: root.busy, count: root.items.length, localCount: root.localImages.length, error: root.error, message: root.message}); }
    }
}
