pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    property var monitors: []
    property var activeLayout: []
    property int selectedIndex: 0
    property bool saveSuccess: false
    spacing: 14

    onMonitorsChanged: {
        if (!Array.isArray(monitors) || monitors.length === 0) return;
        const initial = [];
        for (let i = 0; i < monitors.length; ++i) {
            const m = monitors[i];
            initial.push({
                id: m.id !== undefined ? m.id : i,
                name: m.name || ("Display-" + i),
                description: m.description || "",
                width: m.width || 1920,
                height: m.height || 1080,
                refreshRate: m.refreshRate || 60.0,
                x: m.x !== undefined ? m.x : 0,
                y: m.y !== undefined ? m.y : 0,
                scale: m.scale || 1.0,
                focused: !!m.focused,
                availableModes: m.availableModes || []
            });
        }
        activeLayout = initial;
    }

    function normalizeLayout(list: var): var {
        if (!list || !list.length) return list;
        const minX = Math.min(...list.map(m => m.x || 0));
        const minY = Math.min(...list.map(m => m.y || 0));
        for (let i = 0; i < list.length; ++i) {
            list[i].x = Math.max(0, (list[i].x || 0) - minX);
            list[i].y = Math.max(0, (list[i].y || 0) - minY);
        }
        return list;
    }

    function snapPosition(idx: int, targetX: real, targetY: real): var {
        let bestX = targetX, bestY = targetY;
        const cur = activeLayout[idx];
        if (!cur) return { x: Math.round(targetX), y: Math.round(targetY) };
        const curW = cur.width || 1920, curH = cur.height || 1080, threshold = 120;
        for (let i = 0; i < activeLayout.length; ++i) {
            if (i === idx) continue;
            const o = activeLayout[i], oW = o.width || 1920, oH = o.height || 1080;
            if (Math.abs(targetX - (o.x + oW)) < threshold) bestX = o.x + oW;
            else if (Math.abs(targetX + curW - o.x) < threshold) bestX = o.x - curW;
            else if (Math.abs(targetX - o.x) < threshold) bestX = o.x;
            if (Math.abs(targetY - (o.y + oH)) < threshold) bestY = o.y + oH;
            else if (Math.abs(targetY + curH - o.y) < threshold) bestY = o.y - curH;
            else if (Math.abs(targetY - o.y) < threshold) bestY = o.y;
        }
        return { x: Math.round(bestX), y: Math.round(bestY) };
    }

    function nudgePosition(idx: int, dx: int, dy: int): void {
        const list = JSON.parse(JSON.stringify(activeLayout));
        if (list[idx]) {
            list[idx].x = (list[idx].x || 0) + dx;
            list[idx].y = (list[idx].y || 0) + dy;
            activeLayout = normalizeLayout(list);
        }
    }

    function applyLayoutPreset(preset: string): void {
        if (activeLayout.length < 2) return;
        const list = JSON.parse(JSON.stringify(activeLayout));
        const pri = list[0], sec = list[1];
        if (preset === "left") { pri.x = 0; pri.y = 0; sec.x = pri.width; sec.y = 0; }
        else if (preset === "right") { sec.x = 0; sec.y = 0; pri.x = sec.width; pri.y = 0; }
        else if (preset === "top") { sec.x = 0; sec.y = 0; pri.x = 0; pri.y = sec.height; }
        else if (preset === "bottom") { pri.x = 0; pri.y = 0; sec.x = 0; sec.y = pri.height; }
        activeLayout = normalizeLayout(list);
    }

    function updateScale(idx: int, scaleVal: real): void {
        const list = JSON.parse(JSON.stringify(activeLayout));
        if (list[idx]) { list[idx].scale = scaleVal; activeLayout = list; }
    }

    function updateRefresh(idx: int, modeStr: string): void {
        const list = JSON.parse(JSON.stringify(activeLayout));
        if (list[idx]) {
            const parts = modeStr.split("@");
            if (parts.length === 2) {
                const resParts = parts[0].split("x");
                if (resParts.length === 2) {
                    const w = parseInt(resParts[0], 10), h = parseInt(resParts[1], 10);
                    if (!isNaN(w) && w > 0) list[idx].width = w;
                    if (!isNaN(h) && h > 0) list[idx].height = h;
                }
                const hzVal = parseFloat(parts[1].replace("Hz", ""));
                if (!isNaN(hzVal)) list[idx].refreshRate = hzVal;
            }
            activeLayout = list;
        }
    }

    function applyAndPersist(): void {
        AudioFeedback.playTock();
        const payload = JSON.stringify(activeLayout);
        Quickshell.execDetached([Session.controller, "monitor", "apply", payload]);
        root.saveSuccess = true;
        saveTimer.restart();
    }

    Timer { id: saveTimer; interval: 3500; onTriggered: root.saveSuccess = false }

    // Interactive Display Canvas: Visual layout of monitors
    SettingsCard {
        Layout.fillWidth: true
        visible: root.activeLayout.length > 0
        Text {
            text: I18n.tr("settings.monitors")
            color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 17; font.weight: Font.DemiBold
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("monitors.interactive_desc") + " " + I18n.tr("monitors.drag_hint")
            color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12; wrapMode: Text.Wrap
        }
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 160; radius: 10
            color: Session.surface; border.width: 1
            border.color: Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.12); clip: true

            Item {
                id: monitorLayoutArea
                anchors.centerIn: parent
                readonly property real minX: root.activeLayout.length ? Math.min(...root.activeLayout.map(m => m.x || 0)) : 0
                readonly property real maxX: root.activeLayout.length ? Math.max(...root.activeLayout.map(m => (m.x || 0) + (m.width || 1920))) : 1920
                readonly property real minY: root.activeLayout.length ? Math.min(...root.activeLayout.map(m => m.y || 0)) : 0
                readonly property real maxY: root.activeLayout.length ? Math.max(...root.activeLayout.map(m => (m.y || 0) + (m.height || 1080))) : 1080
                readonly property real totalWidth: Math.max(1, maxX - minX)
                readonly property real totalHeight: Math.max(1, maxY - minY)
                readonly property real scaleFactor: Math.min(380 / totalWidth, 120 / totalHeight)
                width: totalWidth * scaleFactor; height: totalHeight * scaleFactor

                Repeater {
                    model: root.activeLayout
                    Rectangle {
                        id: screenBox
                        required property var modelData
                        required property int index
                        readonly property bool isSelected: root.selectedIndex === index
                        Binding on x {
                            when: !dragArea.drag.active
                            value: ((screenBox.modelData.x || 0) - monitorLayoutArea.minX) * monitorLayoutArea.scaleFactor
                        }
                        Binding on y {
                            when: !dragArea.drag.active
                            value: ((screenBox.modelData.y || 0) - monitorLayoutArea.minY) * monitorLayoutArea.scaleFactor
                        }
                        width: Math.max(70, (modelData.width || 1920) * monitorLayoutArea.scaleFactor)
                        height: Math.max(46, (modelData.height || 1080) * monitorLayoutArea.scaleFactor)
                        radius: 6
                        color: isSelected ? Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.35)
                                          : (modelData.focused ? Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.20) : Qt.rgba(Session.surface.r, Session.surface.g, Session.surface.b, 0.8))
                        border.width: isSelected ? 2 : 1
                        border.color: isSelected ? Session.accent : (modelData.focused ? Session.accent : Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.25))

                        Column {
                            anchors.centerIn: parent; spacing: 2
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: screenBox.modelData.name
                                color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 11; font.weight: Font.DemiBold
                            }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: Math.round(screenBox.modelData.refreshRate) + "Hz · " + screenBox.modelData.scale + "x"
                                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 9
                            }
                        }

                        MouseArea {
                            id: dragArea
                            anchors.fill: parent; drag.target: screenBox; drag.axis: Drag.XAndYAxis
                            onClicked: root.selectedIndex = screenBox.index
                            onReleased: {
                                const rawX = screenBox.x / monitorLayoutArea.scaleFactor + monitorLayoutArea.minX;
                                const rawY = screenBox.y / monitorLayoutArea.scaleFactor + monitorLayoutArea.minY;
                                const snapped = root.snapPosition(screenBox.index, rawX, rawY);
                                const list = JSON.parse(JSON.stringify(root.activeLayout));
                                if (list[screenBox.index]) {
                                    list[screenBox.index].x = snapped.x;
                                    list[screenBox.index].y = snapped.y;
                                    root.activeLayout = root.normalizeLayout(list);
                                }
                            }
                        }
                    }
                }
            }
        }

        // Quick layout presets
        RowLayout {
            Layout.fillWidth: true; spacing: 8; visible: root.activeLayout.length > 1
            Text { text: I18n.tr("monitors.layout_presets") + ":"; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
            AppearanceButton { text: I18n.tr("monitors.primary_left"); onClicked: root.applyLayoutPreset("left") }
            AppearanceButton { text: I18n.tr("monitors.primary_right"); onClicked: root.applyLayoutPreset("right") }
            AppearanceButton { text: I18n.tr("monitors.secondary_top"); onClicked: root.applyLayoutPreset("top") }
            AppearanceButton { text: I18n.tr("monitors.secondary_bottom"); onClicked: root.applyLayoutPreset("bottom") }
        }

        // Apply and save action
        RowLayout {
            Layout.fillWidth: true; spacing: 10
            AppearanceButton { text: I18n.tr("monitors.apply_and_save"); symbol: "check"; selected: true; onClicked: root.applyAndPersist() }
            Text { visible: root.saveSuccess; text: "✓ " + I18n.tr("monitors.saved_success"); color: Session.accent; font.family: Session.fontFamily; font.pixelSize: 12; font.weight: Font.Medium }
        }
    }

    // Monitor cards with per-monitor position nudges, scale, and refresh rate options
    Repeater {
        model: root.activeLayout
        SettingsCard {
            id: monitorCard
            required property var modelData
            required property int index
            readonly property bool isSelected: root.selectedIndex === index
            Layout.fillWidth: true

            RowLayout {
                Layout.fillWidth: true
                SettingsBadge { symbol: "monitor" }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text { text: monitorCard.modelData.name + (monitorCard.modelData.focused ? " · " + I18n.tr("common.active") : ""); color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 17 }
                    Text { Layout.fillWidth: true; text: monitorCard.modelData.description; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12; wrapMode: Text.Wrap }
                }
            }

            Text {
                text: monitorCard.modelData.width + " × " + monitorCard.modelData.height + " · " + Math.round(monitorCard.modelData.refreshRate) + " " + I18n.tr("common.hz") + " · " + I18n.tr("monitors.scale") + " " + monitorCard.modelData.scale + "x"
                color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 13
            }

            // Position coordinate and fine-tuning offset buttons
            RowLayout {
                Layout.fillWidth: true; spacing: 8
                Text { text: I18n.tr("monitors.position") + ": " + monitorCard.modelData.x + ", " + monitorCard.modelData.y; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Item { Layout.fillWidth: true }
                Text { text: "X:"; color: Session.muted; font.pixelSize: 11; font.family: Session.fontFamily }
                AppearanceButton { text: "-100"; onClicked: root.nudgePosition(monitorCard.index, -100, 0) }
                AppearanceButton { text: "+100"; onClicked: root.nudgePosition(monitorCard.index, 100, 0) }
                Text { text: "Y:"; color: Session.muted; font.pixelSize: 11; font.family: Session.fontFamily }
                AppearanceButton { text: "-100"; onClicked: root.nudgePosition(monitorCard.index, 0, -100) }
                AppearanceButton { text: "+100"; onClicked: root.nudgePosition(monitorCard.index, 0, 100) }
            }

            // Per-monitor scale selection
            ColumnLayout {
                Layout.fillWidth: true; spacing: 4
                Text { text: I18n.tr("monitors.display_scale") + ":"; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                RowLayout {
                    spacing: 8
                    Repeater {
                        model: [
                            { label: "1.0x", val: 1.0 }, { label: "1.25x", val: 1.25 },
                            { label: "1.5x", val: 1.5 }, { label: "1.75x", val: 1.75 }, { label: "2.0x", val: 2.0 }
                        ]
                        AppearanceButton {
                            required property var modelData
                            text: modelData.label; selected: Math.abs(monitorCard.modelData.scale - modelData.val) < 0.05
                            onClicked: root.updateScale(monitorCard.index, modelData.val)
                        }
                    }
                }
            }

            // Quick display refresh rate presets
            ColumnLayout {
                Layout.fillWidth: true; spacing: 4
                visible: Array.isArray(monitorCard.modelData.availableModes) && monitorCard.modelData.availableModes.length > 1
                Text { text: I18n.tr("monitors.refresh_rate") + ":"; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Flow {
                    Layout.fillWidth: true; spacing: 6
                    Repeater {
                        model: {
                            const modes = monitorCard.modelData.availableModes || [];
                            const uniqueHz = [];
                            modes.slice(0, 6).forEach(m => { if (!uniqueHz.includes(m)) uniqueHz.push(m); });
                            return uniqueHz;
                        }
                        AppearanceButton {
                            required property string modelData
                            text: modelData.replace(/@\d+\.\d+Hz/, m => " · " + Math.round(parseFloat(m.slice(1))) + "Hz")
                            selected: modelData.includes(String(Math.round(monitorCard.modelData.refreshRate)))
                            onClicked: root.updateRefresh(monitorCard.index, modelData)
                        }
                    }
                }
            }
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        Text {
            Layout.fillWidth: true; text: I18n.tr("monitors.hyprland_notice"); wrapMode: Text.Wrap
            color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 13
        }
        ControlSlider {
            Layout.fillWidth: true; wheelEnabled: false; visible: Desktop.data.brightnessAvailable
            from: 5; to: 100; stepSize: 1; value: Desktop.data.brightness; Accessible.name: I18n.tr("quick.screen_brightness")
            onPressedChanged: if (!pressed) Desktop.request("brightness", String(Math.round(value)))
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        Text { text: I18n.tr("settings.ui_scale"); color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 17 }
        Text { Layout.fillWidth: true; text: I18n.tr("settings.ui_scale_desc"); wrapMode: Text.Wrap; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
        RowLayout {
            Layout.fillWidth: true; spacing: 8
            Repeater {
                model: [
                    { label: "100%", val: 1.0 }, { label: "125%", val: 1.25 },
                    { label: "150%", val: 1.5 }, { label: "175%", val: 1.75 }, { label: "200%", val: 2.0 }
                ]
                AppearanceButton {
                    required property var modelData
                    Layout.fillWidth: true; text: modelData.label
                    selected: Math.abs((Session.settings && Session.settings.bar && Session.settings.bar.uiScale ? Session.settings.bar.uiScale : 1.0) - modelData.val) < 0.05
                    onClicked: Desktop.request("ui-scale", String(modelData.val))
                }
            }
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        RowLayout {
            Layout.fillWidth: true
            SettingsBadge { symbol: "moon-warm"; tint: Session.accent }
            ColumnLayout {
                Layout.fillWidth: true
                Text { text: I18n.tr("quick.night_light"); color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 17 }
                Text { Layout.fillWidth: true; text: I18n.tr("settings.projection_modes"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12; wrapMode: Text.Wrap }
            }
            SettingsToggle {
                checked: !!Desktop.data.nightLight
                enabled: Desktop.data.nightLightAvailable && !Desktop.changingSettings
                Accessible.name: I18n.tr("quick.night_light")
                onToggled: Desktop.request("nightlight", "")
            }
        }
        Flow {
            Layout.fillWidth: true; spacing: 8
            Repeater {
                model: [
                    {mode: "extend", label: I18n.tr("settings.proj_extend")},
                    {mode: "mirror", label: I18n.tr("settings.proj_mirror")},
                    {mode: "internal", label: I18n.tr("settings.proj_internal")},
                    {mode: "external", label: I18n.tr("settings.proj_external")}
                ]
                AppearanceButton {
                    required property var modelData
                    text: modelData.label; symbol: "monitor"
                    onClicked: Quickshell.execDetached([Session.controller, "project", modelData.mode])
                }
            }
        }
    }
}
