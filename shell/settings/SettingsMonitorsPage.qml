pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    property var monitors: []
    spacing: 14
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
                        text: monitorCard.modelData.name
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
                    {
                        label: "100%",
                        val: 1.0
                    },
                    {
                        label: "125%",
                        val: 1.25
                    },
                    {
                        label: "150%",
                        val: 1.5
                    },
                    {
                        label: "175%",
                        val: 1.75
                    },
                    {
                        label: "200%",
                        val: 2.0
                    }
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
