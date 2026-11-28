pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    spacing: 12

    Text {
        Layout.fillWidth: true
        text: I18n.tr("settings.gamemode_tools_desc")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
        wrapMode: Text.Wrap
    }

    QuickTile {
        Layout.fillWidth: true
        title: I18n.tr("gamemode.title")
        subtitle: Desktop.data.gameMode ? I18n.tr("gamemode.status_on") : I18n.tr("gamemode.status_off")
        symbol: "performance"
        active: !!Desktop.data.gameMode
        enabled: !Desktop.changingSettings
        onClicked: Desktop.request("gamemode", Desktop.data.gameMode ? "off" : "on")
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: optimizationsColumn.implicitHeight + 16
        radius: 12
        color: Glass.tint(Session.surface, 0.5)
        border.width: 1
        border.color: Desktop.data.gameMode ? Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.4) : Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.12)

        ColumnLayout {
            id: optimizationsColumn
            anchors.fill: parent
            anchors.margins: 10
            spacing: 6

            Text {
                text: I18n.tr("gamemode.optimizations")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 13
                font.weight: Font.Medium
            }

            RowLayout {
                spacing: 8
                Rectangle {
                    implicitWidth: 6
                    implicitHeight: 6
                    radius: 3
                    color: Desktop.data.gameMode ? Session.accent : Session.muted
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("gamemode.cpu_performance")
                    color: Desktop.data.gameMode ? Session.foreground : Session.muted
                    font.family: Session.fontFamily
                    font.pixelSize: 11
                }
            }

            RowLayout {
                spacing: 8
                Rectangle {
                    implicitWidth: 6
                    implicitHeight: 6
                    radius: 3
                    color: Desktop.data.gameMode ? Session.accent : Session.muted
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("gamemode.hyprland_boost")
                    color: Desktop.data.gameMode ? Session.foreground : Session.muted
                    font.family: Session.fontFamily
                    font.pixelSize: 11
                }
            }

            RowLayout {
                spacing: 8
                Rectangle {
                    implicitWidth: 6
                    implicitHeight: 6
                    radius: 3
                    color: Desktop.data.gameMode ? Session.accent : Session.muted
                }
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("gamemode.dnd_active")
                    color: Desktop.data.gameMode ? Session.foreground : Session.muted
                    font.family: Session.fontFamily
                    font.pixelSize: 11
                }
            }
        }
    }

    Text {
        text: "Hoyoverse & Wine Profiles:"
        color: Session.foreground
        font.family: Session.fontFamily
        font.pixelSize: 12
        font.weight: Font.Medium
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 8
        Repeater {
            model: [
                { id: "zzz", label: "ZZZ" },
                { id: "starrail", label: "Star Rail" },
                { id: "genshin", label: "Genshin" }
            ]
            AppearanceButton {
                required property var modelData
                Layout.fillWidth: true
                text: modelData.label
                onClicked: {
                    Session.closeQuickSettings();
                    root.popup.launchTerminal(["poly-shell", "game", "hoyo", modelData.id]);
                }
            }
        }
    }

    Item { Layout.fillHeight: true }
}
