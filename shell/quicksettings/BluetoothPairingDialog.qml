pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import ".."

Item {
    id: root

    property string deviceMac: ""
    property string deviceName: ""
    property string passkey: ""
    property bool pairing: false
    property string errorMessage: ""
    property bool isPasskeyConfirmation: passkey.length > 0

    signal confirmed(string pin)
    signal cancelled()

    implicitWidth: 360
    implicitHeight: 280

    Rectangle {
        id: bg
        anchors.fill: parent
        color: Session.surface
        radius: 12
        border.width: 1
        border.color: Qt.rgba(1, 1, 1, 0.1)

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 20
            spacing: 16

            // Header
            RowLayout {
                Layout.fillWidth: true
                spacing: 12

                Rectangle {
                    Layout.preferredWidth: 36
                    Layout.preferredHeight: 36
                    radius: 18
                    color: Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.15)

                    Text {
                        anchors.centerIn: parent
                        text: "\uf293"
                        font.family: "Font Awesome 6 Free, Symbols Nerd Font"
                        font.pixelSize: 18
                        color: Session.accent
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 2

                    Text {
                        text: I18n.tr("bluetooth.pair_device")
                        font.pixelSize: 15
                        font.weight: Font.DemiBold
                        color: Session.foreground
                    }

                    Text {
                        text: root.deviceName.length > 0 ? root.deviceName : root.deviceMac
                        font.pixelSize: 13
                        color: Session.muted
                        elide: Text.ElideRight
                        Layout.fillWidth: true
                    }
                }
            }

            // Body content
            ColumnLayout {
                Layout.fillWidth: true
                Layout.fillHeight: true
                spacing: 10

                Text {
                    visible: root.isPasskeyConfirmation
                    text: I18n.tr("bluetooth.confirm_passkey")
                    font.pixelSize: 13
                    color: Session.muted
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Rectangle {
                    visible: root.isPasskeyConfirmation
                    Layout.alignment: Qt.AlignHCenter
                    Layout.preferredWidth: 180
                    Layout.preferredHeight: 44
                    radius: 8
                    color: Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.05)
                    border.width: 1
                    border.color: Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.1)

                    Text {
                        anchors.centerIn: parent
                        text: root.passkey
                        font.pixelSize: 22
                        font.weight: Font.Bold
                        font.letterSpacing: 4
                        color: Session.accent
                    }
                }

                Text {
                    visible: !root.isPasskeyConfirmation
                    text: I18n.tr("bluetooth.enter_pin")
                    font.pixelSize: 13
                    color: Session.muted
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }

                Rectangle {
                    visible: !root.isPasskeyConfirmation
                    Layout.fillWidth: true
                    Layout.preferredHeight: 38
                    radius: 8
                    color: Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.05)
                    border.width: 1
                    border.color: pinInput.activeFocus ? Session.accent : Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.15)

                    TextInput {
                        id: pinInput
                        anchors.fill: parent
                        anchors.leftMargin: 12
                        anchors.rightMargin: 12
                        verticalAlignment: TextInput.AlignVCenter
                        font.pixelSize: 14
                        color: Session.foreground
                        clip: true
                        echoMode: TextInput.Normal
                        inputMethodHints: Qt.ImhDigitsOnly
                    }
                }

                Text {
                    visible: root.errorMessage.length > 0
                    text: root.errorMessage
                    font.pixelSize: 12
                    color: Qt.rgba(0.9, 0.3, 0.3, 1.0)
                    wrapMode: Text.WordWrap
                    Layout.fillWidth: true
                }
            }

            // Actions
            RowLayout {
                Layout.fillWidth: true
                spacing: 10

                Rectangle {
                    id: cancelBtn
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    radius: 6
                    color: cancelMouse.containsPress ? Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.15)
                                                    : Qt.rgba(Session.foreground.r, Session.foreground.g, Session.foreground.b, 0.08)

                    Text {
                        anchors.centerIn: parent
                        text: I18n.tr("common.cancel")
                        font.pixelSize: 13
                        font.weight: Font.Medium
                        color: Session.foreground
                    }

                    MouseArea {
                        id: cancelMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: root.cancelled()
                    }
                }

                Rectangle {
                    id: confirmBtn
                    Layout.fillWidth: true
                    Layout.preferredHeight: 36
                    radius: 6
                    color: !root.pairing ? (confirmMouse.containsPress ? Qt.darker(Session.accent, 1.2) : Session.accent)
                                        : Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.4)

                    Text {
                        anchors.centerIn: parent
                        text: root.pairing ? I18n.tr("bluetooth.pairing")
                                           : (root.isPasskeyConfirmation ? I18n.tr("bluetooth.confirm") : I18n.tr("bluetooth.pair"))
                        font.pixelSize: 13
                        font.weight: Font.DemiBold
                        color: Session.surface
                    }

                    MouseArea {
                        id: confirmMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        enabled: !root.pairing
                        onClicked: {
                            root.confirmed(pinInput.text.trim())
                        }
                    }
                }
            }
        }
    }
}
