pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    required property var popup
    spacing: 12

    Text {
        text: root.popup.powerAction ? I18n.trWith("quick.confirm_action", {action: root.popup.powerAction === "poweroff" ? I18n.tr("quick.shutdown") : I18n.tr("quick.reboot")}) : I18n.tr("quick.choose_action")
        color: Session.foreground
        font.family: Session.fontFamily
        font.pixelSize: 14
    }

    SettingsRow {
        text: I18n.tr("quick.reboot")
        symbol: "refresh"
        Layout.fillWidth: true
        onClicked: root.popup.powerAction = "reboot"
    }

    SettingsRow {
        text: I18n.tr("quick.shutdown")
        symbol: "power"
        Layout.fillWidth: true
        onClicked: root.popup.powerAction = "poweroff"
    }

    SettingsRow {
        text: I18n.tr("common.confirm")
        selected: true
        symbol: "check"
        visible: !!root.popup.powerAction
        Layout.fillWidth: true
        onClicked: {
            Quickshell.execDetached(["systemctl", root.popup.powerAction]);
            Session.closeQuickSettings();
        }
    }

    Item { Layout.fillHeight: true }
}
