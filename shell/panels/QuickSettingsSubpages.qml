pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../logic/StatusLogic.js" as StatusLogic
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell.Networking

ColumnLayout {
    id: root
    required property var popup
    spacing: 12
    opacity: popup.pageMotion.opacity
    transformOrigin: Item.Top

    RowLayout {
        IconButton {
            symbol: "chevron-left"
            hint: I18n.tr("common.back")
            implicitWidth: 30
            implicitHeight: 30
            onClicked: { root.popup.page = "main"; root.popup.powerAction = ""; }
        }
        Text {
            text: root.popup.title
            color: Session.foreground
            font.family: Session.fontFamily
            font.pixelSize: 15
        }
        Item { Layout.fillWidth: true }
        IconButton {
            symbol: "close"
            hint: I18n.tr("common.close")
            implicitWidth: 30
            implicitHeight: 30
            onClicked: Session.closeQuickSettings()
        }
    }

    ScrollView {
        id: deviceScroll
        Layout.fillWidth: true
        Layout.fillHeight: true
        visible: ["wifi", "bluetooth", "output", "input"].includes(root.popup.page)
        clip: true
        contentWidth: availableWidth

        Column {
            width: deviceScroll.availableWidth
            spacing: 8

            SettingsRow {
                width: parent.width
                visible: root.popup.page === "wifi"
                symbol: "wifi"
                text: Session.wifiEnabled ? I18n.tr("wifi.enabled") : I18n.tr("wifi.disabled")
                statusKind: Session.wifiStatus.kind
                statusLevel: Session.wifiStatus.level
                statusBusy: Session.wifiStatus.busy
                statusWarning: Session.wifiStatus.warning
                subtitle: I18n.tr("quick.click_to_toggle")
                selected: Session.wifiEnabled
                enabled: !!Session.wifiDevice
                onClicked: Session.toggleWifi()
            }

            SettingsRow {
                width: parent.width
                visible: root.popup.page === "bluetooth"
                symbol: "bluetooth"
                text: Session.bluetoothEnabled ? I18n.tr("bluetooth.on") : I18n.tr("bluetooth.off")
                subtitle: I18n.tr("quick.click_to_toggle")
                selected: Session.bluetoothEnabled
                enabled: !!Session.bluetoothAdapter
                onClicked: Session.toggleBluetooth()
            }

            Repeater {
                model: root.popup.page === "wifi" && Session.wifiEnabled && Session.wifiDevice ? Session.wifiDevice.networks.values : []
                SettingsRow {
                    id: networkRow
                    required property var modelData
                    width: parent.width
                    text: modelData.name || I18n.tr("quick.hidden_network")
                    symbol: "wifi"
                    selected: modelData.connected
                    statusKind: modelData.stateChanging ? "wifi-connecting" : "wifi"
                    statusLevel: StatusLogic.wifiLevel(modelData.signalStrength)
                    statusBusy: modelData.stateChanging
                    statusWarning: modelData.connected && Session.wifiStatus.warning
                    statusLabel: I18n.trWith("quick.signal_level", {level: statusLevel})
                    subtitle: modelData.stateChanging ? I18n.tr("quick.connecting") : modelData.connected ? I18n.tr("quick.connected") : ""
                    enabled: !modelData.stateChanging
                    onClicked: {
                        if (modelData.connected) return;
                        root.popup.selectedNetwork = modelData;
                        root.popup.customSsid = "";
                        root.popup.localError = "";
                        if (modelData.known || modelData.security === WifiSecurityType.Open || modelData.security === WifiSecurityType.Owe) {
                            modelData.connect();
                        } else if ([WifiSecurityType.Wpa2Psk, WifiSecurityType.WpaPsk, WifiSecurityType.Sae].includes(modelData.security)) {
                            root.popup.isEnterprise = false;
                            root.popup.page = "password";
                        } else {
                            root.popup.isEnterprise = true;
                            root.popup.page = "password";
                        }
                    }
                    Connections {
                        target: networkRow.modelData
                        function onConnectionFailed(reason): void { root.popup.localError = "Wi-Fi: " + ConnectionFailReason.toString(reason); }
                    }
                }
            }

            Repeater {
                model: root.popup.page === "bluetooth" && Session.bluetoothAdapter ? Session.bluetoothAdapter.devices.values.filter(device => device.paired) : []
                RowLayout {
                    id: btDeviceRow
                    required property var modelData
                    width: parent.width
                    spacing: 4
                    SettingsRow {
                        Layout.fillWidth: true
                        symbol: "bluetooth"
                        text: btDeviceRow.modelData.name || btDeviceRow.modelData.address
                        selected: btDeviceRow.modelData.connected
                        subtitle: btDeviceRow.modelData.connected ? I18n.tr("bluetooth.connected_disconnect_hint") : I18n.tr("bluetooth.paired_connect_hint")
                        enabled: Session.bluetoothEnabled
                        onClicked: {
                            if (btDeviceRow.modelData.connected) btDeviceRow.modelData.disconnect();
                            else btDeviceRow.modelData.connect();
                        }
                    }
                    IconButton {
                        symbol: "delete"
                        hint: I18n.tr("bluetooth.unpair")
                        implicitWidth: 32
                        implicitHeight: 32
                        onClicked: btDeviceRow.modelData.forget()
                    }
                }
            }

            Repeater {
                model: root.popup.page === "input" ? Session.inputs : root.popup.page === "output" ? Session.outputs : []
                SettingsRow {
                    required property var modelData
                    width: parent.width
                    symbol: root.popup.page === "input" ? "microphone" : "volume"
                    text: modelData.nickname || modelData.description || modelData.name
                    subtitle: selected ? I18n.tr("common.enabled") : I18n.tr("quick.select_device")
                    selected: modelData === (root.popup.page === "input" ? Session.source : Session.sink)
                    enabled: modelData.ready
                    onClicked: { if (root.popup.page === "input") Session.selectInput(modelData); else Session.selectOutput(modelData); }
                }
            }

            Text {
                width: parent.width
                visible: (root.popup.page === "input" && !Session.inputs.length) || (root.popup.page === "output" && !Session.outputs.length)
                text: I18n.tr("audio.no_devices")
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 12
                padding: 8
            }

            // Per-Application Audio Streams (Pipewire)
            Column {
                width: parent.width
                visible: root.popup.page === "output" && Session.audioStreams && Session.audioStreams.length > 0
                spacing: 8

                Item { width: parent.width; height: 12 }
                GlowSectionDivider { width: parent.width }
                Text {
                    text: I18n.tr("audio.app_streams")
                    color: Session.foreground
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    font.weight: Font.Medium
                    padding: 4
                }

                Repeater {
                    model: Session.audioStreams
                    HoverControl {
                        required property var modelData
                        width: parent.width
                        label: (modelData.properties && (modelData.properties["application.name"] || modelData.properties["node.description"])) || modelData.name || "App"
                        symbol: (modelData.properties && modelData.properties["application.icon-name"]) || "volume"
                        detail: (modelData.properties && modelData.properties["media.name"]) || ""
                        value: modelData.audio ? modelData.audio.volume : 0
                        muted: modelData.audio ? modelData.audio.muted : false
                        hasMute: true
                        onAdjusted: v => {
                            if (modelData.audio) {
                                modelData.audio.volume = v;
                                if (v > 0) modelData.audio.muted = false;
                            }
                        }
                        onMuteRequested: {
                            if (modelData.audio) {
                                modelData.audio.muted = !modelData.audio.muted;
                            }
                        }
                    }
                }
            }
        }
    }

    SettingsRow {
        visible: root.popup.page === "wifi"
        Layout.fillWidth: true
        text: I18n.tr("quick.mobile_hotspot")
        subtitle: Desktop.data.hotspot ? (Desktop.data.hotspotClients > 0 ? I18n.trWith("wifi.hotspot_devices", {count: Desktop.data.hotspotClients}) : I18n.tr("common.enabled")) : I18n.tr("common.disabled")
        symbol: "hotspot"
        onClicked: root.popup.page = "hotspot"
    }

    SettingsRow {
        visible: root.popup.page === "wifi"
        Layout.fillWidth: true
        text: I18n.tr("wifi.add_hidden")
        symbol: "plus"
        onClicked: { root.popup.selectedNetwork = null; root.popup.customSsid = ""; root.popup.isEnterprise = false; root.popup.localError = ""; root.popup.page = "password"; }
    }

    SettingsRow {
        visible: root.popup.page === "bluetooth"
        Layout.fillWidth: true
        text: I18n.tr("bluetooth.pair_new")
        symbol: "bluetooth"
        enabled: Session.bluetoothEnabled
        onClicked: root.popup.launchTerminal(["bluetoothctl"])
    }

    // Password connection subpage
    QuickPasswordSubpage {
        visible: root.popup.page === "password"
        popup: root.popup
    }

    // Hotspot subpage
    QuickHotspotSubpage {
        visible: root.popup.page === "hotspot"
        popup: root.popup
    }

    // Devices subpage
    QuickDevicesSubpage {
        visible: root.popup.page === "settings"
        popup: root.popup
    }

    // Power Profiles subpage
    QuickProfilesSubpage {
        visible: root.popup.page === "profiles"
        popup: root.popup
    }

    QuickGameModeSubpage {
        visible: root.popup.page === "gamemode"
        popup: root.popup
    }

    // Airplane subpage
    QuickAirplaneSubpage {
        visible: root.popup.page === "airplane"
        popup: root.popup
    }

    // Nightlight / DND subpage
    ColumnLayout {
        visible: root.popup.page === "nightlight" || root.popup.page === "dnd"
        Layout.fillWidth: true
        Layout.fillHeight: true
        spacing: 16
        Text {
            Layout.fillWidth: true
            text: root.popup.page === "nightlight" ? I18n.tr("quick.night_light") : I18n.tr("settings.dnd_desc")
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 13
            wrapMode: Text.Wrap
        }
        SettingsRow {
            Layout.fillWidth: true
            symbol: root.popup.page === "nightlight" ? "moon-warm" : "bell"
            text: root.popup.title
            selected: root.popup.page === "nightlight" ? Desktop.data.nightLight : Desktop.data.dnd
            subtitle: selected ? I18n.tr("quick.airplane_on_desc") : I18n.tr("quick.airplane_off_desc")
            enabled: root.popup.page === "nightlight" ? Desktop.data.nightLightAvailable : Desktop.data.dndAvailable
            onClicked: Desktop.request(root.popup.page === "nightlight" ? "nightlight" : "dnd", "")
        }
        Item { Layout.fillHeight: true }
    }

    // Power Actions subpage
    QuickPowerActionsSubpage {
        visible: root.popup.page === "power"
        popup: root.popup
    }
}

