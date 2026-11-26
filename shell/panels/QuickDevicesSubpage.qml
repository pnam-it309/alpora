pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 10

    GridLayout {
        Layout.fillWidth: true
        columns: 2
        rowSpacing: 8
        columnSpacing: 8

        HoverStatusTile {
            Layout.fillWidth: true
            title: "Wi-Fi"
            symbol: "wifi"
            detail: Desktop.data.wifiSsid || I18n.tr("common.disconnected")
            active: Desktop.data.wifiEnabled
            connected: !!Desktop.data.wifiSsid
            statusKind: "wifi"
            statusLevel: Desktop.data.wifiStrength || 0
            onClicked: root.popup.page = "wifi"
        }

        HoverStatusTile {
            Layout.fillWidth: true
            title: "Bluetooth"
            symbol: "bluetooth"
            detail: Desktop.data.bluetoothConnectedDevice || (Desktop.data.bluetoothEnabled ? I18n.tr("bluetooth.on") : I18n.tr("common.off"))
            active: Desktop.data.bluetoothEnabled
            connected: !!Desktop.data.bluetoothConnectedDevice
            statusKind: "bluetooth"
            onClicked: root.popup.page = "bluetooth"
        }

        HoverStatusTile {
            Layout.fillWidth: true
            title: I18n.tr("quick.sound_output")
            symbol: "volume"
            detail: Desktop.data.audioOutputDescription || I18n.tr("audio.output")
            active: !Desktop.data.audioMuted
            connected: true
            onClicked: root.popup.page = "output"
        }

        HoverStatusTile {
            Layout.fillWidth: true
            title: I18n.tr("quick.power_mode")
            symbol: "performance"
            detail: Desktop.data.powerProfile || "balanced"
            active: Desktop.data.powerProfile === "performance"
            connected: Desktop.data.powerProfilesAvailable
            onClicked: root.popup.page = "profiles"
        }
    }

    GlowSectionDivider { Layout.fillWidth: true }

    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.sound_output"); symbol: "volume"; onClicked: root.popup.page = "output" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.microphone"); symbol: "microphone"; onClicked: root.popup.page = "input" }
    SettingsRow { Layout.fillWidth: true; text: "Wi-Fi"; symbol: "wifi"; onClicked: root.popup.page = "wifi" }
    SettingsRow { Layout.fillWidth: true; text: "Bluetooth"; symbol: "bluetooth"; onClicked: root.popup.page = "bluetooth" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.mobile_hotspot"); symbol: "hotspot"; onClicked: root.popup.page = "hotspot" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.power_mode"); symbol: "performance"; onClicked: root.popup.page = "profiles" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.airplane_mode"); symbol: "airplane"; onClicked: root.popup.page = "airplane" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.night_light"); symbol: "moon-warm"; onClicked: root.popup.page = "nightlight" }
    SettingsRow { Layout.fillWidth: true; text: I18n.tr("quick.dnd"); symbol: "bell"; onClicked: root.popup.page = "dnd" }
    Item { Layout.fillHeight: true }
}
