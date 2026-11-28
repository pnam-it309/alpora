pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

RowLayout {
    id: root
    spacing: 8
    Layout.fillWidth: true

    // -10s
    Rectangle {
        Layout.preferredWidth: 30
        Layout.preferredHeight: 30
        radius: 15
        color: Glass.tint(Session.surface, 0.6)
        border.width: 1
        border.color: Glass.tint(Session.foreground, 0.1)

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: if (VideoPipState.player && VideoPipState.player.canSeek) VideoPipState.player.position -= 10
        }

        Text {
            anchors.centerIn: parent
            text: "-10s"
            color: Session.foreground
            font.pixelSize: 9
        }
    }

    // Play/Pause
    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 30
        radius: 15
        color: Session.accent

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: if (VideoPipState.player) VideoPipState.player.togglePlaying()
        }

        RowLayout {
            anchors.centerIn: parent
            spacing: 5

            Icon {
                name: VideoPipState.player && VideoPipState.player.isPlaying ? "pause-dark" : "play-dark"
                Layout.preferredWidth: 14
                Layout.preferredHeight: 14
                color: Session.background
            }

            Text {
                text: VideoPipState.player && VideoPipState.player.isPlaying ? "Pause" : "Play"
                color: Session.background
                font.family: Session.fontFamily
                font.pixelSize: 11
                font.weight: Font.Bold
            }
        }
    }

    // +10s
    Rectangle {
        Layout.preferredWidth: 30
        Layout.preferredHeight: 30
        radius: 15
        color: Glass.tint(Session.surface, 0.6)
        border.width: 1
        border.color: Glass.tint(Session.foreground, 0.1)

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: if (VideoPipState.player && VideoPipState.player.canSeek) VideoPipState.player.position += 10
        }

        Text {
            anchors.centerIn: parent
            text: "+10s"
            color: Session.foreground
            font.pixelSize: 9
        }
    }
}
