pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    spacing: 12

    Text {
        Layout.fillWidth: true
        text: Desktop.data.powerProfilesAvailable ? I18n.tr("quick.power_profiles_desc") : I18n.tr("quick.power_profiles_unavailable")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    Repeater {
        model: [
            {key: "power-saver", label: I18n.tr("quick.power_saver"), detail: I18n.tr("quick.power_saver_desc"), icon: "leaf"},
            {key: "balanced", label: I18n.tr("quick.balanced"), detail: I18n.tr("quick.balanced_desc"), icon: "balance"},
            {key: "performance", label: I18n.tr("quick.performance"), detail: I18n.tr("quick.performance_desc"), icon: "performance"}
        ]
        QuickTile {
            required property var modelData
            Layout.fillWidth: true
            title: modelData.label
            subtitle: modelData.detail
            symbol: modelData.icon
            active: Desktop.data.powerProfile === modelData.key
            enabled: Desktop.data.powerProfilesAvailable && (Desktop.data.powerProfiles || []).includes(modelData.key) && !Desktop.changingSettings
            onClicked: Desktop.request("power-profile", modelData.key)
        }
    }

    Text {
        visible: !!Desktop.data.powerDegraded
        Layout.fillWidth: true
        text: I18n.tr("quick.power_throttled")
        color: PolyTheme.Theme.color("#d9b38d")
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    Item { Layout.fillHeight: true }
}
