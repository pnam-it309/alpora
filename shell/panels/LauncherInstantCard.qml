pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

Rectangle {
    id: root
    property string icon
    property string title
    property string subtitle
    property bool emphasis: false
    signal activated
    Layout.fillWidth: true
    Layout.preferredHeight: 50
    radius: 12
    color: Glass.tint(Session.surface, 0.75)
    border.color: Session.accent
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.margins: 10
        spacing: 12

        Icon { name: root.icon; Layout.preferredWidth: 22; Layout.preferredHeight: 22 }
        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2
            Text {
                text: root.title
                color: root.emphasis ? Session.accent : Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: root.emphasis ? 15 : 13
                font.weight: root.emphasis ? Font.Bold : Font.DemiBold
                elide: root.emphasis ? Text.ElideNone : Text.ElideRight
                Layout.fillWidth: true
            }
            Text {
                text: root.subtitle
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 11
            }
        }
    }
    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor
        onClicked: root.activated()
    }
}
