pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    anchors.fill: parent
    anchors.margins: 16
    contentWidth: availableWidth

    ColumnLayout {
        width: parent.width
        spacing: 10

        Repeater {
            model: [
                {
                    key: "Super + Space",
                    desc: I18n.tr("welcome.sc_spotlight")
                },
                {
                    key: "Super + V",
                    desc: I18n.tr("welcome.sc_clipboard")
                },
                {
                    key: "Super + I",
                    desc: I18n.tr("welcome.sc_quick_settings")
                },
                {
                    key: "Super + ~",
                    desc: I18n.tr("welcome.sc_quake_terminal")
                },
                {
                    key: "Super + Return",
                    desc: I18n.tr("welcome.sc_standard_terminal")
                },
                {
                    key: "Super + E",
                    desc: I18n.tr("welcome.sc_file_manager")
                },
                {
                    key: "Super + Tab",
                    desc: I18n.tr("welcome.sc_overview")
                },
                {
                    key: "Super + W",
                    desc: I18n.tr("welcome.sc_mode_switch")
                },
                {
                    key: "Super + Q",
                    desc: I18n.tr("welcome.sc_close_window")
                },
                {
                    key: "Super + Shift + S",
                    desc: I18n.tr("welcome.sc_screenshot")
                }
            ]

            Rectangle {
                required property var modelData
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                radius: 8
                color: Glass.tint(Session.surface, 0.6)
                border.width: 1
                border.color: Glass.tint(Session.foreground, 0.06)

                RowLayout {
                    anchors.fill: parent
                    anchors.margins: 8
                    spacing: 12

                    Rectangle {
                        radius: 6
                        color: Glass.tint(Session.accent, 0.22)
                        Layout.preferredWidth: 160
                        Layout.preferredHeight: 26

                        Text {
                            anchors.centerIn: parent
                            text: modelData.key
                            color: Session.accent
                            font.family: "monospace"
                            font.pixelSize: 11
                            font.weight: Font.DemiBold
                        }
                    }

                    Text {
                        Layout.fillWidth: true
                        text: modelData.desc
                        color: Session.foreground
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        elide: Text.ElideRight
                    }
                }
            }
        }
    }
}
