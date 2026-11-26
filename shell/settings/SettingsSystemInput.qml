pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property string page
    spacing: 14

    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "power"
        Text {
            text: Session.batteryDescription
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Repeater {
            model: [
                {
                    key: "power-saver",
                    label: I18n.tr("quick.power_saver"),
                    icon: "leaf"
                },
                {
                    key: "balanced",
                    label: I18n.tr("quick.balanced"),
                    icon: "balance"
                },
                {
                    key: "performance",
                    label: I18n.tr("quick.performance"),
                    icon: "performance"
                }
            ]
            SettingsRow {
                required property var modelData
                Layout.fillWidth: true
                text: modelData.label
                symbol: modelData.icon
                selected: Desktop.data.powerProfile === modelData.key
                enabled: Desktop.data.powerProfilesAvailable && (Desktop.data.powerProfiles || []).includes(modelData.key) && !Desktop.changingSettings
                onClicked: Desktop.request("power-profile", modelData.key)
            }
        }
        Text {
            Layout.fillWidth: true
            visible: !Desktop.data.powerProfilesAvailable
            text: I18n.tr("settings.power_service_unavailable")
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 12
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "notifications"
        RowLayout {
            Layout.fillWidth: true
            SettingsBadge {
                symbol: "bell"
                tint: PolyTheme.Theme.color("#edb493")
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("notification.dnd")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 17
            }
            SettingsToggle {
                checked: !!Desktop.data.dnd
                enabled: Desktop.data.dndAvailable && !Desktop.changingSettings
                Accessible.name: I18n.tr("notification.dnd")
                onToggled: Desktop.request("dnd", "")
            }
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.dnd_desc")
            color: PolyTheme.Theme.color("#c2c9d1")
            wrapMode: Text.Wrap
            font.family: Session.fontFamily
            font.pixelSize: 13
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "modes"
        Text {
            text: I18n.tr("settings.operating_mode")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.operating_mode_desc")
            color: PolyTheme.Theme.color("#c2c9d1")
            wrapMode: Text.Wrap
            font.family: Session.fontFamily
            font.pixelSize: 13
        }
        RowLayout {
            AppearanceButton {
                text: "Work"
                symbol: "monitor"
                selected: Session.mode === "work"
                enabled: !Session.switching
                onClicked: Session.setMode("work")
            }
            AppearanceButton {
                text: "Vibe"
                symbol: "moon"
                selected: Session.mode === "vibe"
                enabled: !Session.switching
                onClicked: Session.setMode("vibe")
            }
        }
    }

    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "touchpad"
        Text {
            text: I18n.tr("settings.touchpad_title")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 19
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.touchpad_desc")
            wrapMode: Text.Wrap
            color: PolyTheme.Theme.color("#bec7ce")
            font.family: Session.fontFamily
            font.pixelSize: 12
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_tap_to_click")
                    color: PolyTheme.Theme.color("#eff1f4")
                    font.family: Session.fontFamily
                    font.pixelSize: 14
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_tap_to_click_desc")
                    color: PolyTheme.Theme.color("#bec7ce")
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
            }
            SettingsToggle {
                checked: !Session.settings.input || !Session.settings.input.touchpad || Session.settings.input.touchpad.tapToClick !== false
                Accessible.name: I18n.tr("settings.touchpad_tap_to_click")
                onToggled: Desktop.request("touchpad", JSON.stringify({
                    tapToClick: checked
                }))
            }
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_natural_scroll")
                    color: PolyTheme.Theme.color("#eff1f4")
                    font.family: Session.fontFamily
                    font.pixelSize: 14
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_natural_scroll_desc")
                    color: PolyTheme.Theme.color("#bec7ce")
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
            }
            SettingsToggle {
                checked: !Session.settings.input || !Session.settings.input.touchpad || Session.settings.input.touchpad.naturalScroll !== false
                Accessible.name: I18n.tr("settings.touchpad_natural_scroll")
                onToggled: Desktop.request("touchpad", JSON.stringify({
                    naturalScroll: checked
                }))
            }
        }
        RowLayout {
            Layout.fillWidth: true
            spacing: 12
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 2
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_dwt")
                    color: PolyTheme.Theme.color("#eff1f4")
                    font.family: Session.fontFamily
                    font.pixelSize: 14
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.touchpad_dwt_desc")
                    color: PolyTheme.Theme.color("#bec7ce")
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
            }
            SettingsToggle {
                checked: !Session.settings.input || !Session.settings.input.touchpad || Session.settings.input.touchpad.disableWhileTyping !== false
                Accessible.name: I18n.tr("settings.touchpad_dwt")
                onToggled: Desktop.request("touchpad", JSON.stringify({
                    disableWhileTyping: checked
                }))
            }
        }
        Text {
            text: I18n.tr("settings.pointer_speed")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 15
        }
        ControlSlider {
            Layout.fillWidth: true
            wheelEnabled: false
            from: -1.0
            to: 1.0
            stepSize: 0.1
            value: Session.settings.input && Session.settings.input.touchpad && typeof Session.settings.input.touchpad.sensitivity === "number" ? Session.settings.input.touchpad.sensitivity : 0.0
            onPressedChanged: if (!pressed)
                Desktop.request("touchpad", JSON.stringify({
                    sensitivity: Math.round(value * 10) / 10
                }))
        }
    }
}
