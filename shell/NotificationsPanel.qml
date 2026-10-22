pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    property real expansion: 1
    signal expandRequested()
    readonly property var entries: BarState.notifications.map(item => ({item: item, archived: false}))
        .concat(BarState.visibleHistory.map(item => ({item: item, archived: true})))
    readonly property real previewHeight: 136 + Math.min(entries.length, 2) * 70 + (entries.length ? 0 : 54)
    spacing: 8
    SettingsRow {
        Layout.fillWidth: true; Layout.preferredHeight: 54
        symbol: BarState.dnd ? "bell-muted" : "bell"
        text: "Не беспокоить"
        subtitle: BarState.dnd ? "Включён · сообщения остаются в центре" : "Выключен · показывать всплывающие уведомления"
        selected: BarState.dnd; enabled: !BarState.notificationBusy
        onClicked: BarState.toggleDnd()
    }
    Text { visible: !!BarState.notificationError; Layout.fillWidth: true; text: BarState.notificationError; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 10; wrapMode: Text.Wrap }
    ScrollView {
        id: scroll
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 0
        contentWidth: availableWidth; clip: true
        Column {
            width: scroll.availableWidth; spacing: 0
            Repeater {
                model: panel.entries
                Item {
                    id: row
                    required property var modelData
                    required property int index
                    readonly property real presence: index < 2 ? 1 : panel.expansion
                    readonly property bool heading: index === 0 || (modelData.archived && index === BarState.notifications.length)
                    width: parent.width; height: (card.implicitHeight + 8 + (heading ? 20 : 0)) * presence
                    clip: true
                    Text {
                        visible: row.heading
                        text: row.modelData.archived ? "Ранее · " + BarState.visibleHistory.length : "Активные · " + BarState.notifications.length
                        color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10
                    }
                    NotificationCard {
                        id: card
                        x: 4; y: (row.heading ? 20 : 0) + 4; width: parent.width - 8; height: implicitHeight
                        notification: row.modelData.item; archived: row.modelData.archived
                        detailProgress: panel.expansion
                    }
                }
            }
            Column {
                visible: panel.entries.length === 0
                width: parent.width; topPadding: 16 + 16 * panel.expansion; spacing: 10
                Icon { anchors.horizontalCenter: parent.horizontalCenter; name: "bell"; width: 24; height: 24 }
                Text { width: parent.width; text: "Всё спокойно"; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 13; horizontalAlignment: Text.AlignHCenter }
            }
        }
    }
    Item {
        Layout.fillWidth: true; Layout.minimumHeight: 0; Layout.preferredHeight: 40 * (1 - panel.expansion)
        clip: true
        SettingsRow { width: parent.width; height: 40; text: "Открыть все уведомления"; symbol: "bell"; enabled: panel.expansion < 0.1; onClicked: panel.expandRequested() }
    }
    Item {
        Layout.fillWidth: true; Layout.minimumHeight: 0; Layout.preferredHeight: 34 * panel.expansion
        clip: true
        RowLayout {
            width: parent.width; height: 34
            DayAction { text: "Закрыть активные"; visible: BarState.notifications.length > 0; enabled: !BarState.notificationBusy; onClicked: BarState.dismissAll() }
            Item { Layout.fillWidth: true }
            DayAction { text: "Очистить историю"; visible: BarState.visibleHistory.length > 0; onClicked: BarState.hideHistory() }
        }
    }
}
