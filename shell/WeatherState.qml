pragma Singleton
import QtQuick
import Quickshell
import Quickshell.Io

Singleton {
    id: root
    property var data: ({})
    property string error: ""
    property string requestedLocation: ""
    readonly property bool active: WidgetState.loaded && WidgetState.values.weather.enabled && Quickshell.screens.length > 0
    readonly property bool busy: reader.running
    readonly property var current: data.coordinates && data.coordinates[0] === WidgetState.values.location.latitude && data.coordinates[1] === WidgetState.values.location.longitude ? data.current || null : null
    function refresh(): void {
        if (reader.running) return;
        requestedLocation = JSON.stringify(WidgetState.values.location);
        reader.running = true;
    }
    function label(code: int): string {
        if (code === 0) return I18n.tr("weather.clear");
        if (code < 3) return I18n.tr("weather.partly_cloudy");
        if (code === 3) return I18n.tr("weather.cloudy");
        if (code < 50) return I18n.tr("weather.fog");
        if (code < 60) return I18n.tr("weather.drizzle");
        if (code < 70) return I18n.tr("weather.rain");
        if (code < 80 || code === 85 || code === 86) return I18n.tr("weather.snow");
        if (code < 85) return I18n.tr("weather.heavy_rain");
        return I18n.tr("weather.thunder");
    }
    function day(value: string): string {
        const localeMap = {"ru": "ru_RU", "vi": "vi_VN", "en": "en_US"};
        return new Date(value + "T12:00:00").toLocaleDateString(Qt.locale(localeMap[I18n.locale] || "ru_RU"), "ddd");
    }
    onActiveChanged: if (active) refresh()
    Connections {
        target: WidgetState
        function onValuesChanged(): void { if (root.active) root.refresh(); }
    }
    Timer { interval: root.error ? 60000 : 1800000; repeat: true; running: root.active; onTriggered: root.refresh() }
    Process {
        id: reader
        command: [Session.controller, "widgets", "weather"]
        stdout: StdioCollector { onStreamFinished: {
            try { root.data = JSON.parse(text); root.error = root.data.error || ""; }
            catch (_) { root.error = I18n.tr("weather.error"); }
        } }
        stderr: StdioCollector { onStreamFinished: if (text.trim()) root.error = text.trim().replace(/^poly-shell: /, "") }
        onExited: if (root.active && root.requestedLocation !== JSON.stringify(WidgetState.values.location)) Qt.callLater(root.refresh)
    }
}
