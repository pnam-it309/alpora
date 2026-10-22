pragma ComponentBehavior: Bound
import QtQuick
import Quickshell
import Quickshell.Io
import Quickshell.Wayland
import Quickshell.Hyprland
import "WidgetGeometry.js" as Geometry

Scope {
    id: root
    required property var modelData
    readonly property real width: modelData ? modelData.width : 0
    readonly property real height: modelData ? modelData.height : 0
    readonly property real safeTop: Session.visual.barTop + Session.visual.barHeight + Math.max(20, Session.visual.barBottom + 12)
    readonly property var config: WidgetState.values
    readonly property string targetScreen: Quickshell.screens.find(s => s.name === config.screen)?.name || (Quickshell.screens.length ? Quickshell.screens[0].name : "")
    readonly property bool visible: !!modelData && Session.loaded && WidgetState.loaded && modelData.name === targetScreen && (config.clock.enabled || config.weather.enabled || config.music.enabled)
    function bounds(kind: string): var { return Geometry.bounds(kind, config[kind], width, height, safeTop); }
    property var clients: []
    readonly property var monitor: modelData ? Hyprland.monitorFor(modelData) : null
    function exposed(kind: string): bool {
        if (!modelData) return false;
        const b = bounds(kind);
        const workspace = monitor && monitor.activeWorkspace ? monitor.activeWorkspace.id : -1;
        return !clients.some(c => {
            if (!c.mapped || c.hidden || (!c.pinned && (!c.workspace || c.workspace.id !== workspace))) return false;
            if (!c.at || !c.size) return false;
            const x = c.at[0] - root.modelData.x, y = c.at[1] - root.modelData.y;
            const overlapWidth = Math.max(0, Math.min(x + c.size[0], b.x + b.width) - Math.max(x, b.x));
            const overlapHeight = Math.max(0, Math.min(y + c.size[1], b.y + b.height) - Math.max(y, b.y));
            return overlapWidth * overlapHeight >= b.width * b.height * 0.97;
        });
    }
    // Query only after compositor events, never on an animation-frame timer.
    Connections {
        target: Hyprland
        function onRawEvent(event): void {
            if (/^(openwindow|closewindow|movewindow|activewindow|workspace|focusedmon|fullscreen|changefloatingmode|pin|configreloaded)/.test(event.name)) visibilityRefresh.restart();
        }
    }
    Timer { id: visibilityRefresh; interval: 180; onTriggered: if (!clientReader.running) clientReader.running = true }
    Process {
        id: clientReader; command: ["hyprctl", "-j", "clients"]
        stdout: StdioCollector { onStreamFinished: { try { root.clients = JSON.parse(text); } catch (_) {} } }
    }
    Component.onCompleted: visibilityRefresh.start()
    Variants {
        model: ["clock", "weather", "music"]
        // Each card has its own small surface: animating a cloud must not
        // repaint a full-screen transparent buffer and its compositor blur.
        // qmllint disable uncreatable-type
        PanelWindow {
            // qmllint enable uncreatable-type
            id: card
            required property string modelData
            readonly property var box: root.bounds(modelData)
            screen: root.modelData
            anchors { top: true; left: true }
            // Installed Wayland metadata marks Margins opaque; its runtime
            // grouped properties are required for live layer-shell positioning.
            // qmllint disable missing-property
            margins { top: Math.max(0, Math.round(card.box.y) - 8); left: Math.max(0, Math.round(card.box.x) - 8) }
            // qmllint enable missing-property
            implicitWidth: Math.ceil(box.width) + 16; implicitHeight: Math.ceil(box.height) + 16
            color: "transparent"
            visible: root.visible && root.config[modelData].enabled
            WlrLayershell.layer: WlrLayer.Bottom
            // The shell's broad glass rule enables live compositor blur.
            // These mostly opaque animated cards use their own namespace.
            WlrLayershell.namespace: "poly-desktop-widget"
            WlrLayershell.keyboardFocus: WlrKeyboardFocus.None
            exclusionMode: ExclusionMode.Ignore; exclusiveZone: 0
            mask: Region { item: widgetLoader }
            Loader {
                id: widgetLoader
                x: Math.min(8, card.box.x); y: Math.min(8, card.box.y)
                width: card.box.width; height: card.box.height
                active: card.visible
                sourceComponent: card.modelData === "clock" ? clockComponent : card.modelData === "weather" ? weatherComponent : musicComponent
            }
            Component {
                id: clockComponent
                Item { DesktopClock { width: 460; height: 200; scale: card.box.width / width; transformOrigin: Item.TopLeft; motionActive: card.visible && root.exposed(card.modelData) } }
            }
            Component {
                id: weatherComponent
                Item { DesktopWeather { scale: card.box.width / width; transformOrigin: Item.TopLeft; motionActive: card.visible && root.exposed(card.modelData) } }
            }
            Component {
                id: musicComponent
                Item { DesktopMusic { width: 370; height: 190; scale: card.box.width / width; transformOrigin: Item.TopLeft; motionActive: card.visible && root.exposed(card.modelData) } }
            }
        }
    }
    IpcHandler {
        target: "desktop-widgets-" + (root.modelData ? root.modelData.name : "disconnected")
        function status(): string { return JSON.stringify({visible: root.visible, screen: root.targetScreen, width: root.width, height: root.height, clock: root.bounds("clock"), weather: root.bounds("weather"), music: root.bounds("music"), exposed: {clock: root.exposed("clock"), weather: root.exposed("weather"), music: root.exposed("music")}, animations: !!root.config.animations && Session.visual.widgetAnimations && !Motion.reduced}); }
    }
}
