pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    spacing: 14

    Text {
        Layout.fillWidth: true
        text: I18n.tr("quick.airplane_desc")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    SettingsRow {
        Layout.fillWidth: true
        text: I18n.tr("quick.airplane_mode")
        symbol: "airplane"
        selected: !!Desktop.data.airplane
        subtitle: Desktop.data.airplaneManaged && !selected ? I18n.tr("quick.airplane_restore") : (selected ? I18n.tr("quick.airplane_on_desc") : I18n.tr("quick.airplane_off_desc"))
        enabled: Desktop.data.airplaneAvailable && !Desktop.changingSettings
        onClicked: Desktop.request("airplane", Desktop.data.airplane || Desktop.data.airplaneManaged ? "off" : "on")
    }

    Text {
        visible: !!Desktop.data.airplaneHardwareBlocked
        Layout.fillWidth: true
        text: I18n.tr("quick.airplane_hardware_rfkill")
        color: PolyTheme.Theme.color("#d9b38d")
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    Item { Layout.fillHeight: true }
}
