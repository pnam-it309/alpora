pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    required property var popup
    Layout.fillWidth: true
    Layout.fillHeight: true
    spacing: 10

    RowLayout {
        Layout.fillWidth: true
        spacing: 8
        Icon { name: "wifi"; implicitWidth: 20; implicitHeight: 20 }
        Text {
            Layout.fillWidth: true
            text: root.popup.selectedNetwork ? root.popup.selectedNetwork.name : (root.popup.customSsid || I18n.tr("quick.hidden_network"))
            color: Session.foreground
            font.family: Session.fontFamily
            font.pixelSize: 15
            font.weight: Font.Medium
            elide: Text.ElideRight
        }
    }

    Text {
        visible: !root.popup.selectedNetwork
        text: I18n.tr("wifi.enter_ssid")
        color: Session.muted
        font.family: Session.fontFamily
        font.pixelSize: 11
    }

    TextField {
        id: hiddenSsidInput
        visible: !root.popup.selectedNetwork
        Layout.fillWidth: true
        placeholderText: I18n.tr("wifi.hotspot_name")
        color: Session.foreground
        selectionColor: Session.accent
        font.family: Session.fontFamily
        font.pixelSize: 13
        padding: 10
        background: Rectangle {
            radius: 10
            color: Glass.tint(PolyTheme.Theme.color("#303939"), 0.5)
            border.width: 1
            border.color: hiddenSsidInput.activeFocus ? Session.accent : PolyTheme.Theme.color("#49534b")
        }
        onTextChanged: root.popup.customSsid = text.trim()
    }

    Rectangle {
        Layout.fillWidth: true
        implicitHeight: 36
        radius: 8
        color: Glass.tint(Session.surface, 0.3)
        border.width: 1
        border.color: Glass.tint(Session.accent, 0.15)
        RowLayout {
            anchors.fill: parent
            anchors.margins: 8
            spacing: 8
            Rectangle {
                implicitWidth: 16
                implicitHeight: 16
                radius: 4
                color: root.popup.isEnterprise ? Session.accent : "transparent"
                border.width: 1.5
                border.color: root.popup.isEnterprise ? Session.accent : Session.muted
                Icon { anchors.centerIn: parent; name: "check"; implicitWidth: 12; implicitHeight: 12; visible: root.popup.isEnterprise }
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("wifi.enterprise_checkbox")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 11
                elide: Text.ElideRight
            }
        }
        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: root.popup.isEnterprise = !root.popup.isEnterprise
        }
    }

    ColumnLayout {
        visible: root.popup.isEnterprise
        Layout.fillWidth: true
        spacing: 4
        Text { text: I18n.tr("wifi.enterprise_identity"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11 }
        TextField {
            id: identityField
            Layout.fillWidth: true
            placeholderText: "identity / username"
            color: Session.foreground
            selectionColor: Session.accent
            font.family: Session.fontFamily
            font.pixelSize: 13
            padding: 10
            background: Rectangle {
                radius: 10
                color: Glass.tint(PolyTheme.Theme.color("#303939"), 0.5)
                border.width: 1
                border.color: identityField.activeFocus ? Session.accent : PolyTheme.Theme.color("#49534b")
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        spacing: 4
        Text { text: I18n.tr("wifi.password_label"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11 }
        RowLayout {
            Layout.fillWidth: true
            spacing: 6
            Loader {
                id: passwordLoader
                Layout.fillWidth: true
                active: root.popup.opened && root.popup.page === "password"
                onLoaded: Qt.callLater(() => { if (root.popup.passwordInput) root.popup.passwordInput.forceActiveFocus(); })
                sourceComponent: TextField {
                    id: password
                    placeholderText: I18n.tr("wifi.password_placeholder")
                    echoMode: root.popup.showPassword ? TextInput.Normal : TextInput.Password
                    color: Session.foreground
                    selectionColor: Session.accent
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    padding: 10
                    background: Rectangle {
                        radius: 10
                        color: Glass.tint(PolyTheme.Theme.color("#303939"), 0.5)
                        border.width: 1
                        border.color: password.activeFocus ? Session.accent : PolyTheme.Theme.color("#49534b")
                    }
                    onAccepted: if (connectButton.enabled) connectButton.clicked()
                }
            }
            Rectangle {
                Layout.preferredWidth: 42
                Layout.preferredHeight: 38
                radius: 9
                color: Glass.tint(Session.surface, 0.4)
                border.width: 1
                border.color: Glass.tint(Session.accent, 0.2)
                Text {
                    anchors.centerIn: parent
                    text: root.popup.showPassword ? I18n.tr("wifi.hide_password") : I18n.tr("wifi.show_password")
                    color: Session.accent
                    font.family: Session.fontFamily
                    font.pixelSize: 10
                    font.weight: Font.Medium
                }
                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor
                    onClicked: root.popup.showPassword = !root.popup.showPassword
                }
            }
        }
    }

    Text {
        visible: !!root.popup.localError || !!Desktop.error
        Layout.fillWidth: true
        text: root.popup.localError || Desktop.error
        color: PolyTheme.Theme.color("#f18b82")
        font.family: Session.fontFamily
        font.pixelSize: 11
        wrapMode: Text.Wrap
    }

    RowLayout {
        Layout.fillWidth: true
        spacing: 10
        SettingsRow {
            id: connectButton
            Layout.fillWidth: true
            Layout.preferredWidth: 1
            text: I18n.tr("wifi.connect_button")
            symbol: "wifi"
            readonly property string activeSsid: root.popup.selectedNetwork ? root.popup.selectedNetwork.name : root.popup.customSsid
            readonly property string passVal: root.popup.passwordInput ? root.popup.passwordInput.text : ""
            readonly property string identVal: identityField ? identityField.text.trim() : ""
            enabled: activeSsid.length > 0 && (!root.popup.isEnterprise ? (passVal.length >= 8 || !root.popup.selectedNetwork) : (identVal.length > 0 && passVal.length > 0)) && !Desktop.changingSettings
            onClicked: {
                if (!enabled) return;
                root.popup.localError = "";
                if (root.popup.isEnterprise) {
                    Desktop.request("wifi-connect", JSON.stringify({ ssid: activeSsid, identity: identVal, password: passVal }));
                    root.popup.page = "wifi";
                } else if (root.popup.selectedNetwork) {
                    root.popup.selectedNetwork.connectWithPsk(passVal);
                    if (root.popup.passwordInput) root.popup.passwordInput.clear();
                    root.popup.page = "wifi";
                } else {
                    Desktop.request("wifi-connect", JSON.stringify({ ssid: activeSsid, password: passVal, hidden: true }));
                    root.popup.page = "wifi";
                }
            }
        }
        SettingsRow {
            Layout.preferredWidth: 80
            text: I18n.tr("common.cancel")
            symbol: "close"
            onClicked: { root.popup.localError = ""; root.popup.page = "wifi"; }
        }
    }
    Item { Layout.fillHeight: true }
}
