pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    anchors.fill: parent
    anchors.margins: 20
    spacing: 14

    Text {
        text: I18n.tr("welcome.themes_title")
        color: Session.foreground
        font.family: Session.fontFamily
        font.pixelSize: 16
        font.weight: Font.DemiBold
    }

    RowLayout {
        spacing: 12

        Button {
            text: I18n.trWith("welcome.themes_toggle_mode", {mode: Session.mode.toUpperCase()})
            Layout.preferredHeight: 36
            onClicked: Session.setMode("toggle")
            background: Rectangle {
                radius: 8
                color: Glass.tint(Session.accent, 0.25)
                border.width: 1
                border.color: Session.accent
            }
            contentItem: Text {
                text: I18n.trWith("welcome.themes_toggle_mode", {mode: Session.mode.toUpperCase()})
                color: Session.accent
                font.family: Session.fontFamily
                font.pixelSize: 12
                font.weight: Font.DemiBold
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }
    }

    Text {
        text: I18n.tr("welcome.themes_landscapes_heading")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 12
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 10

        Repeater {
            model: [
                {
                    id: "alpine",
                    name: I18n.tr("theme.alpine")
                },
                {
                    id: "moon-lake",
                    name: I18n.tr("theme.moon_lake")
                },
                {
                    id: "forest-mist",
                    name: I18n.tr("theme.forest_mist")
                },
                {
                    id: "warm-desert",
                    name: I18n.tr("theme.warm_desert")
                },
                {
                    id: "timeline",
                    name: I18n.tr("theme.timeline")
                }
            ]

            Button {
                required property var modelData
                Layout.fillWidth: true
                Layout.preferredHeight: 45
                onClicked: ThemeState.applyTheme(modelData.id)

                background: Rectangle {
                    radius: 8
                    color: Glass.tint(Session.surface, 0.8)
                    border.width: 1
                    border.color: parent.hovered ? Session.accent : Glass.tint(Session.foreground, 0.12)
                }

                contentItem: Text {
                    text: modelData.name
                    color: Session.foreground
                    font.family: Session.fontFamily
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                }
            }
        }
    }

    Item {
        Layout.fillHeight: true
    }
}
