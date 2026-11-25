pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 12

    Text {
        Layout.fillWidth: true
        text: I18n.tr("wifi.hotspot_desc")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    SettingsRow {
        Layout.fillWidth: true
        text: I18n.tr("quick.mobile_hotspot")
        symbol: "hotspot"
        selected: !!Desktop.data.hotspot
        subtitle: Desktop.data.hotspot ? (Desktop.data.hotspotClients > 0 ? I18n.trWith("wifi.hotspot_devices", {count: Desktop.data.hotspotClients}) : I18n.tr("common.enabled")) : I18n.tr("common.disabled")
        enabled: Desktop.data.hotspotAvailable && !Desktop.changingSettings && !Desktop.data.airplane
        onClicked: Desktop.request("hotspot", Desktop.data.hotspot ? "off" : "on")
    }

    GlowSectionDivider {
        Layout.fillWidth: true
    }

    Text {
        text: I18n.tr("wifi.hotspot_name")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 11
    }

    TextField {
        id: hotspotSsidEdit
        Layout.fillWidth: true
        text: Desktop.data.hotspotSsid || "Alpora-Hotspot"
        color: Session.foreground
        selectionColor: Session.accent
        font.family: Session.fontFamily
        font.pixelSize: 13
        padding: 10
        background: Rectangle {
            radius: 10
            color: Glass.tint(PolyTheme.Theme.color("#303939"), 0.5)
            border.width: 1
            border.color: hotspotSsidEdit.activeFocus ? Session.accent : PolyTheme.Theme.color("#49534b")
        }
    }

    Text {
        text: I18n.tr("wifi.hotspot_password")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 11
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 6
        TextField {
            id: hotspotPasswordEdit
            Layout.fillWidth: true
            text: Desktop.data.hotspotPassword || ""
            echoMode: root.popup.showPassword ? TextInput.Normal : TextInput.Password
            color: Session.foreground
            selectionColor: Session.accent
            font.family: Session.fontFamily
            font.pixelSize: 13
            padding: 10
            background: Rectangle {
                radius: 10
                color: Glass.tint(PolyTheme.Theme.color("#303939"), 0.5)
                border.width: 1
                border.color: hotspotPasswordEdit.activeFocus ? Session.accent : PolyTheme.Theme.color("#49534b")
            }
        }

        Rectangle {
            Layout.preferredWidth: 42
            Layout.preferredHeight: 38
            radius: 9
            color: Glass.tint(Session.surface, 0.4)
            border.width: 1
            border.color: Glass.tint(Session.accent, 0.2)
            Text {
                anchors.centerIn: parent
                text: root.popup.showPassword ? I18n.tr("wifi.hide_password") : I18n.tr("wifi.show_password")
                color: Session.accent
                font.family: Session.fontFamily
                font.pixelSize: 10
                font.weight: Font.Medium
            }
            MouseArea {
                anchors.fill: parent
                cursorShape: Qt.PointingHandCursor
                onClicked: root.popup.showPassword = !root.popup.showPassword
            }
        }
    }

    Text {
        text: I18n.tr("wifi.hotspot_band")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 11
    }

    SettingsRow {
        Layout.fillWidth: true
        text: I18n.tr("wifi.hotspot_save")
        symbol: "check"
        enabled: hotspotSsidEdit.text.trim().length > 0 && hotspotPasswordEdit.text.trim().length >= 8 && !Desktop.changingSettings
        onClicked: {
            Desktop.request("hotspot", JSON.stringify({ ssid: hotspotSsidEdit.text.trim(), password: hotspotPasswordEdit.text.trim(), active: Desktop.data.hotspot }));
        }
    }

    Item { Layout.fillHeight: true }
}
