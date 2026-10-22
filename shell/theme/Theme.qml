pragma Singleton
import QtQuick
import ".." as Shell
import Quickshell

Singleton {
    id: root
    readonly property var palette: Shell.TimelineState.palette || Shell.Session.appearance.palette || null
    readonly property bool active: !!palette
    readonly property color accent: palette ? palette.accent : Shell.Session.accent
    readonly property color secondary: palette ? palette.secondary : "#edb493"
    readonly property color cool: palette ? palette.cool : "#9cc8df"
    readonly property string label: Shell.Session.appearance.label || "Alpine"
    function mix(a: color, b: color, t: real): color {
        return Qt.rgba(a.r*(1-t)+b.r*t, a.g*(1-t)+b.g*t, a.b*(1-t)+b.b*t, 1);
    }
    // Central compatibility map for the established Alpine materials. All QML
    // colors resolve through semantic theme roles without touching behavior modes.
    function color(value: string): color {
        let hex = value.slice(1);
        let alpha = 1;
        if (hex.length === 8) { alpha = parseInt(hex.slice(0, 2), 16) / 255; hex = hex.slice(2); }
        const r = parseInt(hex.slice(0, 2),16)/255;
        const g = parseInt(hex.slice(2, 4),16)/255;
        const b = parseInt(hex.slice(4, 6),16)/255;
        if (!root.palette) return Qt.rgba(r,g,b,alpha);
        const hi = Math.max(r,g,b), lo = Math.min(r,g,b), diff = hi-lo;
        const saturation = hi > 0 ? diff/hi : 0;
        let hue = diff === 0 ? 0 : hi === r ? ((g-b)/diff+6)%6 : hi === g ? (b-r)/diff+2 : (r-g)/diff+4;
        hue /= 6;
        const light = (r+g+b)/3;
        let output;
        if (saturation > 0.18 && hue < 0.045) output = Qt.rgba(r,g,b,1);
        else if (saturation > 0.10 && light > 0.48) {
            const base = hue >= 0.045 && hue < 0.17 ? root.secondary : hue > 0.43 && hue < 0.65 ? root.cool : root.accent;
            output = mix(base, root.palette.background, Math.max(0, 0.68-light)*0.65);
        }
        else if (light > 0.80) output = root.palette.text;
        else if (light > 0.54) output = root.palette.muted;
        else if (light > 0.33) output = mix(root.palette.surface, root.palette.accent, Math.min(0.4, 0.12+light-0.33));
        else if (light > 0.19) output = mix(root.palette.background, root.palette.surface, Math.min(0.95, 0.35+(light-0.19)*4));
        else if (light > 0.13) output = mix(root.palette.background, root.palette.surface, (light-0.13)*3);
        else output = mix(root.palette.background, "#000000", 0.18);
        // Typed local color ensures palette strings have numeric components.
        return withAlpha(output, alpha);
    }
    function withAlpha(value: color, alpha: real): color { return Qt.rgba(value.r,value.g,value.b,alpha); }
}
