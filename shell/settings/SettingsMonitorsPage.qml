pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts
import QtQuick.Controls
import Quickshell

ColumnLayout {
    id: root
    property var monitors: []
    spacing: 14

    // Interactive Display Canvas: Visual layout of monitors
    SettingsCard {
        Layout.fillWidth: true
        visible: root.monitors.length > 0
        Text {
            text: I18n.tr("settings.projection_modes")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("monitors.interactive_desc")
            color: PolyTheme.Theme.color("#bec7ce")
            font.family: Session.fontFamily
            font.pixelSize: 12
            wrapMode: Text.Wrap
        }
        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 140
            radius: 10
            color: PolyTheme.Theme.color("#1a221e")
            border.width: 1
            border.color: PolyTheme.Theme.color("#36423c")
            clip: true

            Item {
                id: monitorLayoutArea
                anchors.centerIn: parent
                readonly property real minX: root.monitors.reduce((acc, m) => Math.min(acc, m.x || 0), 0)
                readonly property real maxX: root.monitors.reduce((acc, m) => Math.max(acc, (m.x || 0) + (m.width || 1920)), 1920)
                readonly property real totalWidth: Math.max(1, maxX - minX)
                readonly property real scaleFactor: Math.min(380 / totalWidth, 100 / 1080)
                width: totalWidth * scaleFactor
                height: 1080 * scaleFactor

                Repeater {
                    model: root.monitors
                    Rectangle {
                        id: screenBox
                        required property var modelData
                        x: ((modelData.x || 0) - monitorLayoutArea.minX) * monitorLayoutArea.scaleFactor
                        y: (modelData.y || 0) * monitorLayoutArea.scaleFactor
                        width: Math.max(60, (modelData.width || 1920) * monitorLayoutArea.scaleFactor)
                        height: Math.max(40, (modelData.height || 1080) * monitorLayoutArea.scaleFactor)
                        radius: 6
                        color: modelData.focused ? Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.28) : PolyTheme.Theme.color("#28342e")
                        border.width: modelData.focused ? 1.5 : 1
                        border.color: modelData.focused ? Session.accent : PolyTheme.Theme.color("#48564f")

                        Column {
                            anchors.centerIn: parent
                            spacing: 2
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: screenBox.modelData.name
                                color: Session.foreground
                                font.family: Session.fontFamily
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }
                            Text {
                                anchors.horizontalCenter: parent.horizontalCenter
                                text: Math.round(screenBox.modelData.refreshRate) + "Hz"
                                color: Session.muted
                                font.family: Session.fontFamily
                                font.pixelSize: 9
                            }
                        }
                    }
                }
            }
        }
    }

    // Monitor cards with available refresh rate and resolution options
    Repeater {
        model: root.monitors
        SettingsCard {
            id: monitorCard
            required property var modelData
            Layout.fillWidth: true

            RowLayout {
                Layout.fillWidth: true
                SettingsBadge {
                    symbol: "monitor"
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: monitorCard.modelData.name + (monitorCard.modelData.focused ? " · " + I18n.tr("common.active") : "")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 17
                    }
                    Text {
                        Layout.fillWidth: true
                        text: monitorCard.modelData.description
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        wrapMode: Text.Wrap
                    }
                }
            }

            Text {
                text: monitorCard.modelData.width + " × " + monitorCard.modelData.height + " · " + Math.round(monitorCard.modelData.refreshRate) + " " + I18n.tr("common.hz") + " · " + I18n.tr("monitors.scale") + " " + monitorCard.modelData.scale
                color: PolyTheme.Theme.color("#d3d9db")
                font.family: Session.fontFamily
                font.pixelSize: 13
            }

            Text {
                text: I18n.tr("monitors.position") + ": " + monitorCard.modelData.x + ", " + monitorCard.modelData.y
                color: PolyTheme.Theme.color("#bec7ce")
                font.family: Session.fontFamily
                font.pixelSize: 12
            }

            // Quick display refresh rate presets
            Flow {
                Layout.fillWidth: true
                spacing: 6
                visible: Array.isArray(monitorCard.modelData.availableModes) && monitorCard.modelData.availableModes.length > 1
                Repeater {
                    model: {
                        const modes = monitorCard.modelData.availableModes || [];
                        const uniqueHz = [];
                        modes.slice(0, 5).forEach(m => {
                            if (!uniqueHz.includes(m)) uniqueHz.push(m);
                        });
                        return uniqueHz;
                    }
                    AppearanceButton {
                        required property string modelData
                        text: modelData.replace(/@\d+\.\d+Hz/, m => " · " + Math.round(parseFloat(m.slice(1))) + "Hz")
                        selected: modelData.includes(String(Math.round(monitorCard.modelData.refreshRate)))
                        onClicked: {
                            const name = monitorCard.modelData.name;
                            const res = modelData.split("@")[0];
                            const hz = modelData.split("@")[1]?.replace("Hz", "") || "60";
                            const pos = monitorCard.modelData.x + "x" + monitorCard.modelData.y;
                            const scale = monitorCard.modelData.scale || 1;
                            Quickshell.execDetached(["hyprctl", "keyword", "monitor", name + "," + res + "@" + hz + "," + pos + "," + scale]);
                        }
                    }
                }
            }
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        Text {
            Layout.fillWidth: true
            text: I18n.tr("monitors.hyprland_notice")
            wrapMode: Text.Wrap
            color: PolyTheme.Theme.color("#c2c9d1")
            font.family: Session.fontFamily
            font.pixelSize: 13
        }
        ControlSlider {
            Layout.fillWidth: true
            wheelEnabled: false
            visible: Desktop.data.brightnessAvailable
            from: 5
            to: 100
            stepSize: 1
            value: Desktop.data.brightness
            Accessible.name: I18n.tr("quick.screen_brightness")
            onPressedChanged: if (!pressed)
                Desktop.request("brightness", String(Math.round(value)))
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        Text {
            text: I18n.tr("settings.ui_scale")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.ui_scale_desc")
            wrapMode: Text.Wrap
            color: PolyTheme.Theme.color("#bec7ce")
            font.family: Session.fontFamily
            font.pixelSize: 12
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 8
            Repeater {
                model: [
                    { label: "100%", val: 1.0 },
                    { label: "125%", val: 1.25 },
                    { label: "150%", val: 1.5 },
                    { label: "175%", val: 1.75 },
                    { label: "200%", val: 2.0 }
                ]
                AppearanceButton {
                    required property var modelData
                    Layout.fillWidth: true
                    text: modelData.label
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
            SettingsBadge {
                symbol: "moon-warm"
                tint: PolyTheme.Theme.color("#edb493")
            }
            ColumnLayout {
                Layout.fillWidth: true
                Text {
                    text: I18n.tr("quick.night_light")
                    color: PolyTheme.Theme.color("#eff1f4")
                    font.family: Session.fontFamily
                    font.pixelSize: 17
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.projection_modes")
                    color: PolyTheme.Theme.color("#bec7ce")
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
            }
            SettingsToggle {
                checked: !!Desktop.data.nightLight
                enabled: Desktop.data.nightLightAvailable && !Desktop.changingSettings
                Accessible.name: I18n.tr("quick.night_light")
                onToggled: Desktop.request("nightlight", "")
            }
        }
        Flow {
            Layout.fillWidth: true
            spacing: 8
            Repeater {
                model: [
                    {mode: "extend", label: I18n.tr("settings.proj_extend")},
                    {mode: "mirror", label: I18n.tr("settings.proj_mirror")},
                    {mode: "internal", label: I18n.tr("settings.proj_internal")},
                    {mode: "external", label: I18n.tr("settings.proj_external")}
                ]
                AppearanceButton {
                    required property var modelData
                    text: modelData.label
                    symbol: "monitor"
                    onClicked: Quickshell.execDetached([Session.controller, "project", modelData.mode])
                }
            }
        }
    }
}
