pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Hyprland
import "OverviewGeometry.js" as Geometry

Singleton {
    id: root

    // Reference Counting: only track window lifecycle when UI subscribers are active.
    property int subscribers: 0
    readonly property bool active: subscribers > 0
    property var cachedGroups: []

    function subscribe(): void {
        subscribers++;
        if (subscribers === 1)
            refresh();
    }

    function unsubscribe(): void {
        subscribers = Math.max(0, subscribers - 1);
    }

    function key(value: string): string {
        return (value || "").toLowerCase().replace(/\.desktop$/, "").replace(/[^a-z0-9]/g, "");
    }

    function matches(entry: var, app: string): bool {
        if (!entry || !app) return false;
        return [entry.id, entry.startupClass, entry.icon].some(value => value && key(value) === key(app));
    }

    function computeGroups(): var {
        const favorites = AppCatalog.pinnedIds.map(id => AppCatalog.entries.find(e => e.id === id)).filter(e => !!e);
        const groups = favorites.map(e => ({id: e.id, entry: e, name: e.name, pinned: true, windows: [], active: false, urgent: false}));
        
        if (!Hyprland.toplevels) return groups;
        
        Hyprland.toplevels.values.forEach(t => {
            const data = t.lastIpcObject;
            if (!data) return;
            const workspace = t.workspace ? {id: t.workspace.id, name: t.workspace.name || String(t.workspace.id)}
                : {id: Number(data.workspace?.id || 0), name: String(data.workspace?.name || data.workspace?.id || "")};
            if (data.mapped === false || data.hidden || workspace.name.startsWith("special:")) return;
            const app = data.class || (t.wayland ? t.wayland.appId : "") || data.initialClass || "";
            const entry = favorites.find(e => matches(e, app)) || AppCatalog.entries.find(e => matches(e, app));
            const id = entry ? entry.id : "window:" + (app || t.address);
            let group = groups.find(g => g.id === id);
            if (!group) {
                group = {id: id, entry: entry || null, name: entry ? entry.name : app || t.title || I18n.tr("dock.app_fallback"), pinned: false, windows: [], active: false, urgent: false};
                groups.push(group);
            }
            group.windows.push({
                address: "0x" + t.address.replace(/^0x/, ""),
                title: t.title || group.name,
                workspace: workspace,
                active: t.activated,
                urgent: t.urgent,
                order: Number(data.focusHistoryID ?? 999)
            });
            group.active = group.active || t.activated;
            group.urgent = group.urgent || t.urgent;
        });

        groups.forEach(g => g.windows.sort((a, b) => a.order - b.order));
        return groups.filter(g => g.pinned).concat(groups.filter(g => !g.pinned).sort((a, b) => a.name.localeCompare(b.name)));
    }

    function refresh(): void {
        cachedGroups = computeGroups();
    }

    readonly property var groups: active ? cachedGroups : (cachedGroups.length ? cachedGroups : computeGroups())

    function group(id: string): var {
        return groups.find(g => g.id === id) || null;
    }

    // Compositor-agnostic dispatch wrapper (HAL)
    function focus(window: var): void {
        if (!window) return;
        const command = Geometry.dispatch("focus", window.workspace, window.address, Hyprland.usingLua);
        if (command) Hyprland.dispatch(command);
    }

    function close(window: var): void {
        if (!window) return;
        const command = Geometry.dispatch("close", window.workspace, window.address, Hyprland.usingLua);
        if (command) Hyprland.dispatch(command);
    }

    // Throttle / debounce updates only when UI subscribers are listening
    Connections {
        target: Hyprland
        enabled: root.active
        function onRawEvent(event): void {
            if (/^(openwindow|closewindow|movewindow|activewindow|workspace|fullscreen|changefloatingmode|urgent)/.test(event.name)) {
                lazyRefresh.restart();
            }
        }
    }

    Timer {
        id: lazyRefresh
        interval: 40
        onTriggered: if (root.active) root.refresh()
    }
}
