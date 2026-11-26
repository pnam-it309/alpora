pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    signal closeRequested
    anchors.fill: parent
    anchors.margins: 20
    spacing: 12

    Text {
        text: I18n.tr("welcome.doctor_title")
        color: Session.foreground
        font.family: Session.fontFamily
        font.pixelSize: 16
        font.weight: Font.DemiBold
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 10

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 8
            color: Glass.tint(Session.surface, 0.7)
            border.width: 1
            border.color: Glass.tint(Session.foreground, 0.08)

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 4
                Text {
                    text: I18n.tr("welcome.doctor_compositor")
                    color: Session.muted
                    font.pixelSize: 11
                }
                Text {
                    text: "Hyprland (Wayland)"
                    color: Session.foreground
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 8
            color: Glass.tint(Session.surface, 0.7)
            border.width: 1
            border.color: Glass.tint(Session.foreground, 0.08)

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 4
                Text {
                    text: I18n.tr("welcome.doctor_shell")
                    color: Session.muted
                    font.pixelSize: 11
                }
                Text {
                    text: "Quickshell Qt6"
                    color: Session.foreground
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
            }
        }

        Rectangle {
            Layout.fillWidth: true
            Layout.preferredHeight: 64
            radius: 8
            color: Glass.tint(Session.surface, 0.7)
            border.width: 1
            border.color: Glass.tint(Session.foreground, 0.08)

            ColumnLayout {
                anchors.centerIn: parent
                spacing: 4
                Text {
                    text: I18n.tr("welcome.doctor_audio")
                    color: Session.muted
                    font.pixelSize: 11
                }
                Text {
                    text: "PipeWire / WirePlumber"
                    color: Session.foreground
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
            }
        }
    }

    RowLayout {
        spacing: 12

        Button {
            text: I18n.tr("welcome.doctor_open_settings")
            Layout.preferredHeight: 36
            onClicked: {
                Quickshell.execDetached([Session.controller, "settings"]);
                root.closeRequested();
            }
            background: Rectangle {
                radius: 8
                color: Glass.tint(Session.accent, 0.25)
                border.width: 1
                border.color: Session.accent
            }
            contentItem: Text {
                text: I18n.tr("welcome.doctor_open_settings")
                color: Session.accent
                font.family: Session.fontFamily
                font.pixelSize: 12
                font.weight: Font.DemiBold
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        Button {
            text: I18n.tr("welcome.doctor_open_tasks")
            Layout.preferredHeight: 36
            onClicked: {
                Quickshell.execDetached([Session.controller, "task-manager"]);
            }
            background: Rectangle {
                radius: 8
                color: Glass.tint(Session.foreground, 0.08)
                border.width: 1
                border.color: Glass.tint(Session.foreground, 0.15)
            }
            contentItem: Text {
                text: I18n.tr("welcome.doctor_open_tasks")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 12
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Item {
        Layout.fillHeight: true
    }
}
