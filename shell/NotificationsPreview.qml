pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts

ColumnLayout {
    id: root
    signal expandRequested()
    readonly property var entries: BarState.notifications.map(item => ({item: item, archived: false}))
        .concat(BarState.visibleHistory.map(item => ({item: item, archived: true}))).slice(0, 2)
    spacing: 8
    SettingsRow {
        Layout.fillWidth: true; Layout.preferredHeight: 54
        symbol: BarState.dnd ? "bell-muted" : "bell"
        text: "Не беспокоить"
        subtitle: BarState.dnd ? "Включён · сообщения остаются в центре" : "Выключен · показывать всплывающие уведомления"
        selected: BarState.dnd; enabled: !BarState.notificationBusy
        onClicked: BarState.toggleDnd()
    }
    Text {
        visible: !!BarState.notificationError; text: BarState.notificationError
        Layout.fillWidth: true; color: Session.foreground; font.family: Session.fontFamily
        font.pixelSize: 10; wrapMode: Text.Wrap
    }
    Text {
        visible: root.entries.length > 0
        text: BarState.notifications.length ? "Активные · " + BarState.notifications.length : "Ранее · " + BarState.visibleHistory.length
        color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10
    }
    Repeater {
        model: root.entries
        NotificationCard {
            required property var modelData
            Layout.fillWidth: true; Layout.preferredHeight: implicitHeight
            notification: modelData.item; archived: modelData.archived; compact: true
        }
    }
    Text {
        visible: root.entries.length === 0
        Layout.fillWidth: true; Layout.preferredHeight: 54
        text: "Всё спокойно"; color: Session.muted; font.family: Session.fontFamily
        font.pixelSize: 12; horizontalAlignment: Text.AlignHCenter; verticalAlignment: Text.AlignVCenter
    }
    SettingsRow {
        Layout.fillWidth: true; Layout.preferredHeight: 40
        text: "Открыть все уведомления"; symbol: "bell"
        onClicked: root.expandRequested()
    }
}
