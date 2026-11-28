pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls

Button {
    id: root
    property string screenName: ""

    implicitWidth: 28
    implicitHeight: 28
    padding: 0
    hoverEnabled: true
    focusPolicy: Qt.StrongFocus
    Accessible.name: I18n.tr("arcade.play_mode")

    background: Rectangle {
        radius: Math.min(14, Session.visual.barRadius)
        color: root.down
            ? Glass.tint(Session.accent, 0.45)
            : (ArcadeState.active
                ? Glass.tint(Session.accent, 0.32)
                : (root.hovered ? Glass.tint(Session.surface, 0.65) : Glass.tint(Session.surface, 0.25)))
        border.width: ArcadeState.active ? 1 : Session.visual.barBorder
        border.color: ArcadeState.active
            ? Session.accent
            : (root.hovered ? Glass.tint(Session.foreground, 0.20) : Glass.tint(Session.foreground, 0.08))

        Behavior on color { ColorAnimation { duration: Motion.responseMs } }
        Behavior on border.color { ColorAnimation { duration: Motion.responseMs } }
    }

    contentItem: Item {
        Icon {
            anchors.centerIn: parent
            name: "gamepad"
            width: 15
            height: 15
        }

        // Active indicator dot
        Rectangle {
            visible: ArcadeState.active
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: 4
            width: 5
            height: 5
            radius: 2.5
            color: Session.accent
        }
    }

    onClicked: ArcadeState.toggle(root.screenName)
}
