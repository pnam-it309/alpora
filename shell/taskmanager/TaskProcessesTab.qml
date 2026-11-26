pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

Item {
    id: root
    property var processesData: []
    property string searchText: ""
    property int selectedPid: -1
    signal selected(int pid, string name)
    ColumnLayout {
        anchors.fill: parent; anchors.margins: 14; spacing: 10
        // Table header
        Rectangle {
            Layout.fillWidth: true; Layout.preferredHeight: 28; radius: 4
            color: Glass.tint(Session.surface, 0.5)
            RowLayout {
                anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12
                Text { Layout.fillWidth: true; text: I18n.tr("tasks.col_name"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
                Text { Layout.preferredWidth: 70; text: I18n.tr("tasks.col_pid"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
                Text { Layout.preferredWidth: 90; text: I18n.tr("tasks.col_status"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
                Text { Layout.preferredWidth: 80; text: I18n.tr("tasks.col_cpu"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
                Text { Layout.preferredWidth: 90; text: I18n.tr("tasks.col_memory"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
                Text { Layout.preferredWidth: 90; text: I18n.tr("tasks.col_user"); color: Session.muted; font.pixelSize: 11; font.weight: Font.DemiBold }
            }
        }
        // Process List
        ListView {
            id: processList
            Layout.fillWidth: true; Layout.fillHeight: true; clip: true; spacing: 3
            model: root.processesData.filter(p => !root.searchText || p.name.toLowerCase().includes(root.searchText.toLowerCase()))
            delegate: Rectangle {
                required property var modelData
                width: processList.width; height: 34; radius: 5
                color: root.selectedPid === modelData.pid ? Glass.tint(Session.accent, 0.22) : pMouse.containsMouse ? Glass.tint(Session.surface, 0.6) : "transparent"
                border.width: root.selectedPid === modelData.pid ? 1 : 0
                border.color: Glass.tint(Session.accent, 0.45)

                RowLayout {
                    anchors.fill: parent; anchors.leftMargin: 12; anchors.rightMargin: 12
                    Text { Layout.fillWidth: true; text: parent.modelData.name; color: Session.foreground; font.pixelSize: 12; elide: Text.ElideRight }
                    Text { Layout.preferredWidth: 70; text: String(parent.modelData.pid); color: Session.muted; font.pixelSize: 11 }
                    Text { Layout.preferredWidth: 90; text: parent.modelData.status; color: Session.muted; font.pixelSize: 11 }
                    Text { Layout.preferredWidth: 80; text: parent.modelData.cpu_percent + "%"; color: parent.modelData.cpu_percent > 15 ? Session.accent : Session.foreground; font.pixelSize: 11 }
                    Text { Layout.preferredWidth: 90; text: parent.modelData.memory_mb + " MB"; color: Session.foreground; font.pixelSize: 11 }
                    Text { Layout.preferredWidth: 90; text: parent.modelData.user; color: Session.muted; font.pixelSize: 11 }
                }
                MouseArea {
                    id: pMouse
                    anchors.fill: parent; hoverEnabled: true
                    onClicked: { root.selected(parent.modelData.pid, parent.modelData.name); }
                }
            }
        }
    }
}
