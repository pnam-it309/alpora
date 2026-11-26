pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    property bool restarting: false
    signal restartRequested
    anchors.fill: parent
    anchors.margins: 20
    spacing: 16

    Text {
        text: I18n.tr("welcome.ime_title")
        color: Session.foreground
        font.family: Session.fontFamily
        font.pixelSize: 16
        font.weight: Font.DemiBold
    }

    Text {
        text: I18n.tr("welcome.ime_desc")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.WordWrap
        Layout.fillWidth: true
    }

    // Test input box
    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: 50
        radius: 10
        color: Glass.tint(Session.surface, 0.8)
        border.width: 1
        border.color: Session.accent

        RowLayout {
            anchors.fill: parent
            anchors.margins: 10
            spacing: 10

            Text {
                text: I18n.tr("welcome.ime_test")
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 12
            }

            TextField {
                id: testField
                Layout.fillWidth: true
                placeholderText: I18n.tr("welcome.ime_placeholder")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 13
                background: Item {}
            }
        }
    }

    RowLayout {
        spacing: 12

        Button {
            text: I18n.tr("welcome.ime_restart_btn")
            Layout.preferredHeight: 36
            onClicked: root.restartRequested()
            background: Rectangle {
                radius: 8
                color: parent.hovered ? Glass.tint(Session.accent, 0.3) : Glass.tint(Session.foreground, 0.1)
                border.width: 1
                border.color: Glass.tint(Session.accent, 0.4)
            }
            contentItem: Text {
                text: I18n.tr("welcome.ime_restart_btn")
                color: Session.accent
                font.family: Session.fontFamily
                font.pixelSize: 12
                font.weight: Font.Medium
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        Text {
            text: root.restarting ? I18n.tr("welcome.ime_starting") : I18n.tr("welcome.ime_ready")
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 11
        }
    }

    Item {
        Layout.fillHeight: true
    }
}
