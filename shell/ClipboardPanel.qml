pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: panel
    spacing: 10
    readonly property string query: search.text
    readonly property bool searchFocused: search.activeFocus
    readonly property int selectedIndex: clips.currentIndex
    readonly property var entries: ClipboardState.entries.filter(item =>
        (!pinnedOnly.checked || item.pinned) && (item.preview + " " + item.mime).toLocaleLowerCase().includes(search.text.toLocaleLowerCase()))
    function prepareOpen(): void { search.text = ""; clips.currentIndex = 0; search.forceActiveFocus(); }
    function choose(): void { const entry = entries[clips.currentIndex]; if (entry) ClipboardState.request("copy", entry.id); }
    onEntriesChanged: clips.currentIndex = Math.max(0, Math.min(clips.currentIndex, entries.length - 1))
    DayField {
        id: search
        Layout.fillWidth: true
        placeholderText: "Поиск в истории…"
        Accessible.name: "Поиск в буфере обмена"
        onTextChanged: clips.currentIndex = 0
        onAccepted: panel.choose()
        Keys.onDownPressed: clips.currentIndex = Math.min(panel.entries.length - 1, clips.currentIndex + 1)
        Keys.onUpPressed: clips.currentIndex = Math.max(0, clips.currentIndex - 1)
    }
    RowLayout {
        Layout.fillWidth: true; spacing: 6
        DayAction {
            id: pinnedOnly
            checkable: true; primary: checked
            text: checked ? "Закреплённые" : "Все записи"
            Accessible.name: "Показать только закреплённые"
        }
        Item { Layout.fillWidth: true }
        Text { text: panel.entries.length + " / " + ClipboardState.entries.length; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11 }
        DayAction {
            text: ClipboardState.paused ? "Продолжить" : "Пауза"
            primary: ClipboardState.paused
            Accessible.name: ClipboardState.paused ? "Возобновить запись истории" : "Приостановить запись истории"
            enabled: ClipboardState.ready && !ClipboardState.busy
            onClicked: ClipboardState.request("pause", "")
        }
    }
    Text {
        visible: !!ClipboardState.error || ClipboardState.paused
        Layout.fillWidth: true
        text: ClipboardState.error || "Запись истории приостановлена"
        textFormat: Text.PlainText; wrapMode: Text.Wrap
        color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11
    }
    ListView {
        id: clips
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 0
        model: panel.entries; spacing: 8; clip: true
        boundsBehavior: Flickable.StopAtBounds
        ScrollBar.vertical: ScrollBar { policy: ScrollBar.AsNeeded }
        onCurrentIndexChanged: if (currentIndex >= 0) positionViewAtIndex(currentIndex, ListView.Contain)
        delegate: ClipboardEntry {
            required property var modelData
            required property int index
            width: clips.width; height: implicitHeight
            entry: modelData
            selected: clips.currentIndex === index
            onActivated: clips.currentIndex = index
        }
        Column {
            anchors.centerIn: parent; width: parent.width - 32; spacing: 10
            visible: panel.entries.length === 0
            Icon { anchors.horizontalCenter: parent.horizontalCenter; name: "clipboard"; width: 32; height: 32 }
            Text { width: parent.width; text: search.text || pinnedOnly.checked ? "Ничего не найдено" : "Здесь появится скопированное"; horizontalAlignment: Text.AlignHCenter; wrapMode: Text.Wrap; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 13 }
            Text { width: parent.width; text: "Тексты и изображения · до 200 записей"; horizontalAlignment: Text.AlignHCenter; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11 }
        }
    }
    RowLayout {
        Layout.fillWidth: true
        Text { Layout.fillWidth: true; text: "Выбрать → Ctrl+V\n↑ ↓ — выбор · Enter — скопировать"; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10 }
        DayAction {
            text: "Очистить историю"
            Accessible.name: "Очистить историю, сохранив закреплённые"
            enabled: ClipboardState.ready && !ClipboardState.busy && ClipboardState.entries.some(e => !e.pinned)
            onClicked: ClipboardState.request("clear", "")
            ToolTip.visible: hovered
            ToolTip.text: "Закреплённые записи останутся"
        }
    }
}
