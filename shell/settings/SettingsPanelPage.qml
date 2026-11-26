pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property string page
    signal navigate(string page)
    spacing: 14
    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "panel"
        Text {
            text: I18n.tr("settings.font_family")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.font_desc") + " (" + Session.fontFamily + ")"
            wrapMode: Text.Wrap
            color: PolyTheme.Theme.color("#bec7ce")
            font.family: Session.fontFamily
            font.pixelSize: 12
        }
        Flow {
            Layout.fillWidth: true
            spacing: 6
            Repeater {
                model: ["Noto Sans", "Inter", "Roboto", "Cantarell", "JetBrains Mono", "Fira Code", "DejaVu Sans"]
                AppearanceButton {
                    required property string modelData
                    text: modelData
                    selected: Session.fontFamily === modelData
                    onClicked: Desktop.request("font", modelData)
                }
            }
        }
    }
    SettingsCard {
        Layout.fillWidth: true
        visible: root.page === "panel"
        Text {
            text: I18n.tr("settings.operating_mode")
            color: PolyTheme.Theme.color("#eff1f4")
            font.family: Session.fontFamily
            font.pixelSize: 17
        }
        Text {
            Layout.fillWidth: true
            text: I18n.tr("settings.operating_mode_desc")
            color: PolyTheme.Theme.color("#bec7ce")
            font.family: Session.fontFamily
            font.pixelSize: 12
            wrapMode: Text.Wrap
        }
        RowLayout {
            spacing: 10
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
        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: I18n.tr("quick.night_light")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 14
            }
            SettingsToggle {
                checked: !!Desktop.data.nightLight
                enabled: Desktop.data.nightLightAvailable && !Desktop.changingSettings
                Accessible.name: I18n.tr("quick.night_light")
                onToggled: Desktop.request("nightlight", "")
            }
        }
        RowLayout {
            Layout.fillWidth: true
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.caffeine_mode")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 14
            }
            SettingsToggle {
                checked: !!Desktop.data.caffeine
                Accessible.name: I18n.tr("settings.caffeine_mode")
                onToggled: Desktop.request("caffeine", checked ? "on" : "off")
            }
        }
    }
    SettingsCard {
        Layout.fillWidth: true
        visible: ["panel", "input", "devices"].includes(root.page)
        Text {
            Layout.fillWidth: true
            text: root.page === "panel" ? I18n.tr("settings.nav_panel_hint") : root.page === "input" ? I18n.tr("settings.nav_input_hint") : I18n.tr("settings.nav_devices_hint")
            color: PolyTheme.Theme.color("#c2c9d1")
            font.family: Session.fontFamily
            font.pixelSize: 14
            wrapMode: Text.Wrap
        }
        Flow {
            Layout.fillWidth: true
            spacing: 10
            AppearanceButton {
                text: root.page === "panel" ? I18n.tr("settings.open_appearance") : "Bluetooth"
                symbol: root.page === "panel" ? "palette" : "bluetooth"
                primary: true
                onClicked: root.navigate(root.page === "panel" ? "appearance" : "bluetooth")
            }
            AppearanceButton {
                visible: root.page === "panel"
                text: I18n.tr("settings.widgets")
                symbol: "devices"
                onClicked: root.navigate("widgets")
            }
        }
    }
}
