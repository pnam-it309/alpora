pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../logic/StatusLogic.js" as StatusLogic
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Networking

ScrollView {
    id: root
    property string page: "wifi"
    property var monitors: []
    property url wallpaper: ""
    property var selectedNetwork: null
    property bool isEnterprise: false
    property string localError: ""
    signal navigate(string page)
    signal chooseWallpaper
    signal restoreWallpaper
    clip: true
    contentWidth: availableWidth
    function terminal(args: var): void {
        Quickshell.execDetached((Session.settings.apps.terminal || ["kitty"]).concat(["-e"]).concat(args));
    }
    onPageChanged: {
        selectedNetwork = null;
        isEnterprise = false;
        password.clear();
        localError = "";
    }
    Binding {
        target: Session.wifiDevice
        property: "scannerEnabled"
        value: root.visible && root.page === "wifi" && Session.wifiEnabled
        when: !!Session.wifiDevice
        restoreMode: Binding.RestoreBindingOrValue
    }
    ColumnLayout {
        width: root.availableWidth
        spacing: 14
        SettingsCard {
            Layout.fillWidth: true
            visible: root.page === "wifi" || root.page === "bluetooth"
            RowLayout {
                Layout.fillWidth: true
                SettingsBadge {
                    symbol: root.page === "wifi" ? "wifi" : "bluetooth"
                    tint: root.page === "wifi" ? PolyTheme.Theme.color("#b8ce9f") : PolyTheme.Theme.color("#9cc8df")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: root.page === "wifi" ? I18n.tr("wifi.wireless_network") : "Bluetooth"
                        color: PolyTheme.Theme.color("#f0f1f5")
                        font.family: Session.fontFamily
                        font.pixelSize: 17
                    }
                    Text {
                        text: root.page === "wifi" ? (Session.wifiDevice ? I18n.tr("wifi.available_networks_and_connection") : I18n.tr("wifi.adapter_not_found")) : (Session.bluetoothAdapter ? I18n.tr("bluetooth.paired_devices") : I18n.tr("bluetooth.adapter_not_found"))
                        color: PolyTheme.Theme.color("#bec6ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                    }
                }
                SettingsToggle {
                    checked: root.page === "wifi" ? Session.wifiEnabled : Session.bluetoothEnabled
                    enabled: root.page === "wifi" ? !!Session.wifiDevice : !!Session.bluetoothAdapter && !Desktop.changingSettings
                    Accessible.name: root.page === "wifi" ? I18n.tr("wifi.enable_wifi") : I18n.tr("bluetooth.enable_bluetooth")
                    onToggled: root.page === "wifi" ? Session.toggleWifi() : Session.toggleBluetooth()
                }
            }
        }
        Repeater {
            model: root.page === "wifi" && Session.wifiEnabled && Session.wifiDevice ? Session.wifiDevice.networks.values : []
            SettingsRow {
                id: networkRow
                required property var modelData
                Layout.fillWidth: true
                symbol: "wifi"
                text: modelData.name || I18n.tr("quick.hidden_network")
                selected: modelData.connected
                statusKind: modelData.stateChanging ? "wifi-connecting" : "wifi"
                statusLevel: StatusLogic.wifiLevel(modelData.signalStrength)
                statusBusy: modelData.stateChanging
                statusWarning: modelData.connected && Session.wifiStatus.warning
                statusLabel: I18n.trWith("quick.signal_level", {
                    level: statusLevel
                })
                subtitle: modelData.stateChanging ? I18n.tr("quick.connecting") : modelData.connected ? I18n.tr("quick.connected") : ""
                enabled: !modelData.stateChanging
                onClicked: {
                    if (modelData.connected)
                        return;
                    root.localError = "";
                    if (modelData.known || [WifiSecurityType.Open, WifiSecurityType.Owe].includes(modelData.security)) {
                        modelData.connect();
                    } else if ([WifiSecurityType.Wpa2Psk, WifiSecurityType.WpaPsk, WifiSecurityType.Sae].includes(modelData.security)) {
                        root.selectedNetwork = modelData;
                        root.isEnterprise = false;
                        password.clear();
                        password.forceActiveFocus();
                    } else {
                        root.selectedNetwork = modelData;
                        root.isEnterprise = true;
                        password.clear();
                        password.forceActiveFocus();
                    }
                }
                Connections {
                    target: networkRow.modelData
                    function onConnectionFailed(reason): void {
                        root.localError = String(reason);
                    }
                }
            }
        }
        SettingsCard {
            Layout.fillWidth: true
            visible: root.page === "wifi" && !!root.selectedNetwork
            Text {
                text: I18n.tr("wifi.password_label") + ": " + (root.selectedNetwork ? root.selectedNetwork.name : "")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 14
            }
            TextField {
                id: enterpriseIdentity
                visible: root.isEnterprise
                Layout.fillWidth: true
                placeholderText: I18n.tr("wifi.enterprise_identity")
                echoMode: TextInput.Normal
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 14
                padding: 12
                background: Rectangle {
                    radius: 9
                    color: PolyTheme.Theme.color("#252c33")
                    border.color: enterpriseIdentity.activeFocus ? PolyTheme.Theme.color("#b5c99d") : PolyTheme.Theme.color("#596166")
                }
            }
            TextField {
                id: password
                Layout.fillWidth: true
                placeholderText: I18n.tr("wifi.password_placeholder")
                echoMode: TextInput.Password
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 14
                padding: 12
                background: Rectangle {
                    radius: 9
                    color: PolyTheme.Theme.color("#252c33")
                    border.color: password.activeFocus ? PolyTheme.Theme.color("#b5c99d") : PolyTheme.Theme.color("#596166")
                }
                onAccepted: if (connectButton.enabled)
                    connectButton.clicked()
            }
            AppearanceButton {
                id: connectButton
                text: I18n.tr("wifi.connect_button")
                symbol: "wifi"
                primary: true
                enabled: (!root.isEnterprise ? (password.text.length >= 8 && password.text.length <= 63) : (enterpriseIdentity.text.trim().length > 0 && password.text.length > 0))
                onClicked: {
                    if (!root.selectedNetwork)
                        return;
                    if (root.isEnterprise) {
                        Desktop.request("wifi-connect", JSON.stringify({
                            ssid: root.selectedNetwork.name,
                            identity: enterpriseIdentity.text.trim(),
                            password: password.text
                        }));
                    } else {
                        root.selectedNetwork.connectWithPsk(password.text);
                    }
                    password.clear();
                    root.selectedNetwork = null;
                    root.isEnterprise = false;
                }
            }
        }
        Text {
            Layout.fillWidth: true
            visible: root.page === "wifi" && Session.wifiEnabled && Session.wifiDevice && !Session.wifiDevice.networks.values.length
            text: I18n.tr("wifi.searching_networks")
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 13
        }
        AppearanceButton {
            visible: root.page === "wifi"
            text: I18n.tr("quick.mobile_hotspot")
            symbol: "hotspot"
            onClicked: Desktop.request("hotspot", Desktop.data.hotspot ? "off" : "on")
        }
        Repeater {
            model: root.page === "bluetooth" && Session.bluetoothAdapter ? Session.bluetoothAdapter.devices.values.filter(d => d.paired) : []
            SettingsRow {
                required property var modelData
                Layout.fillWidth: true
                symbol: "bluetooth"
                text: modelData.name
                selected: modelData.connected
                subtitle: modelData.connected ? I18n.tr("bluetooth.connected_disconnect_hint") : I18n.tr("bluetooth.paired_connect_hint")
                enabled: Session.bluetoothEnabled
                onClicked: modelData.connected = !modelData.connected
            }
        }
        SettingsCard {
            Layout.fillWidth: true
            visible: root.page === "bluetooth"
            Text {
                Layout.fillWidth: true
                text: I18n.tr("bluetooth.pairing_notice")
                wrapMode: Text.Wrap
                color: PolyTheme.Theme.color("#c2c9d1")
                font.family: Session.fontFamily
                font.pixelSize: 13
            }
            AppearanceButton {
                text: I18n.tr("bluetooth.connect_new")
                symbol: "plus"
                enabled: Session.bluetoothEnabled
                onClicked: root.terminal(["bluetoothctl"])
            }
        }
        SettingsMonitorsPage {
            Layout.fillWidth: true
            visible: root.page === "monitors"
            monitors: root.monitors
        }
        SettingsCard {
            Layout.fillWidth: true
            visible: root.page === "wallpaper"
            SettingsImage {
                Layout.fillWidth: true
                Layout.preferredHeight: 285
                source: root.wallpaper
                sourceSize: Qt.size(1100, 570)
            }
            Text {
                text: I18n.tr("settings.desktop_wallpaper")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 19
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.wallpaper_desc")
                wrapMode: Text.Wrap
                color: PolyTheme.Theme.color("#c2c9d1")
                font.family: Session.fontFamily
                font.pixelSize: 13
            }
            RowLayout {
                AppearanceButton {
                    text: I18n.tr("settings.change_wallpaper")
                    symbol: "wallpaper"
                    primary: true
                    onClicked: root.chooseWallpaper()
                }
                AppearanceButton {
                    text: I18n.tr("settings.restore_alpine")
                    symbol: "refresh"
                    onClicked: root.restoreWallpaper()
                }
            }
        }
        SettingsSoundPage {
            Layout.fillWidth: true
            visible: root.page === "sound"
        }
        SettingsSystemInput {
            Layout.fillWidth: true
            visible: ["power", "notifications", "modes", "touchpad"].includes(root.page)
            page: root.page
        }
        SettingsPanelPage {
            Layout.fillWidth: true
            visible: ["panel", "input", "devices"].includes(root.page)
            page: root.page
            onNavigate: page => root.navigate(page)
        }
        Text {
            Layout.fillWidth: true
            visible: !!root.localError
            text: root.localError
            color: PolyTheme.Theme.color("#f0b297")
            font.family: Session.fontFamily
            font.pixelSize: 13
            wrapMode: Text.Wrap
        }
    }
}
