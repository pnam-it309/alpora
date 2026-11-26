pragma ComponentBehavior: Bound
import QtQuick
import "../"
import QtQuick.Layouts

ColumnLayout {
    id: root
    spacing: 6
    readonly property bool idle: !SlideshowState.busy
    RowLayout {
        Layout.fillWidth: true; spacing: 9
        Icon { name: "wallpaper"; Layout.preferredWidth: 18; Layout.preferredHeight: 18 }
        ColumnLayout {
            Layout.fillWidth: true; spacing: 2
            Text { text: I18n.tr("theme.slideshow"); color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12; font.weight: Font.DemiBold }
            Text {
                Layout.fillWidth: true
                text: SlideshowState.error || SlideshowState.effectiveFolder || I18n.tr("theme.slideshow_hint")
                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10; elide: Text.ElideMiddle; textFormat: Text.PlainText
            }
        }
        AppearanceButton {
            text: I18n.tr("theme.slideshow_use_folder"); implicitHeight: 28
            enabled: root.idle && ThemeState.activeFolder !== ""
            onClicked: SlideshowState.configure({folder: ThemeState.activeFolder})
        }
        SettingsToggle {
            checked: SlideshowState.enabled; enabled: root.idle
            Accessible.name: I18n.tr("theme.slideshow")
            onToggled: SlideshowState.configure({enabled: checked})
        }
    }
    RowLayout {
        Layout.fillWidth: true; spacing: 6
        Repeater {
            model: [5, 15, 30, 60]
            AppearanceButton {
                required property int modelData
                text: modelData + " " + I18n.tr("theme.slideshow_min"); implicitHeight: 28
                selected: SlideshowState.intervalMinutes === modelData
                enabled: root.idle
                onClicked: SlideshowState.configure({intervalMinutes: modelData})
            }
        }
        AppearanceButton {
            text: I18n.tr("theme.slideshow_shuffle"); symbol: "check"; implicitHeight: 28
            selected: SlideshowState.shuffle; enabled: root.idle
            onClicked: SlideshowState.configure({shuffle: !SlideshowState.shuffle})
        }
        Item { Layout.fillWidth: true }
        AppearanceButton {
            text: I18n.tr("theme.slideshow_next"); implicitHeight: 28
            enabled: root.idle && !ThemeState.busy
            onClicked: SlideshowState.next()
        }
    }
}
