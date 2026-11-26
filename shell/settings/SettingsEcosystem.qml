pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell.Io

ScrollView {
    id: root
    clip: true
    contentWidth: availableWidth

    property bool busy: false
    property string outputReport: ""

    function runCommand(args: var): void {
        if (runner.running) return;
        root.busy = true;
        runner.command = [Session.controller].concat(args);
        runner.running = true;
    }

    Component.onCompleted: root.runCommand(["security", "status"])

    Process {
        id: runner
        stdout: StdioCollector {
            onStreamFinished: {
                root.busy = false;
                if (text.trim()) {
                    root.outputReport = text.trim();
                }
            }
        }
        stderr: StdioCollector {
            onStreamFinished: {
                if (text.trim()) {
                    root.outputReport = text.trim();
                }
            }
        }
        onExited: root.busy = false
    }

    ColumnLayout {
        width: root.availableWidth
        spacing: 14

        // 1. Security Shield & Application Privacy Sandbox
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "shield"
                    tint: PolyTheme.Theme.color("#a8d5bc")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.security_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.security_desc")
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        wrapMode: Text.Wrap
                    }
                }
            }

            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.security_audit_btn")
                    symbol: "shield"
                    primary: true
                    enabled: !root.busy
                    onClicked: root.runCommand(["security", "audit"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.security_harden_btn")
                    symbol: "lock"
                    enabled: !root.busy
                    onClicked: root.runCommand(["security", "harden"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.privacy_status_btn")
                    symbol: "check"
                    enabled: !root.busy
                    onClicked: root.runCommand(["privacy", "status"])
                }
            }
        }

        // 2. ALPORA Phone Connect (KDE Connect Ecosystem)
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "devices"
                    tint: PolyTheme.Theme.color("#9cc8df")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.phone_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.phone_desc")
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        wrapMode: Text.Wrap
                    }
                }
            }

            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.phone_list_btn")
                    symbol: "devices"
                    enabled: !root.busy
                    onClicked: root.runCommand(["phone", "list"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.phone_ring_btn")
                    symbol: "bell"
                    primary: true
                    enabled: !root.busy
                    onClicked: Desktop.request("phone", "ring")
                }
                AppearanceButton {
                    text: I18n.tr("settings.phone_ping_btn")
                    symbol: "check"
                    enabled: !root.busy
                    onClicked: Desktop.request("phone", "ping")
                }
                AppearanceButton {
                    text: I18n.tr("settings.phone_clip_btn")
                    symbol: "copy"
                    enabled: !root.busy
                    onClicked: Desktop.request("phone", "clip")
                }
            }
        }

        // 3. Game Mode, Windows .EXE Runner & Developer CLI Hub
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "performance"
                    tint: PolyTheme.Theme.color("#edb493")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.gamemode_tools_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.gamemode_tools_desc")
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        wrapMode: Text.Wrap
                    }
                }
                SettingsToggle {
                    checked: !!Desktop.data.gameMode
                    Accessible.name: I18n.tr("settings.gamemode_tools_title")
                    onToggled: Desktop.request("gamemode", checked ? "on" : "off")
                }
            }

            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.game_status_btn")
                    symbol: "performance"
                    enabled: !root.busy
                    onClicked: root.runCommand(["game", "status"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.dev_hub_btn")
                    symbol: "terminal"
                    enabled: !root.busy
                    onClicked: root.runCommand(["dev", "list"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.exe_presets_btn")
                    symbol: "window"
                    enabled: !root.busy
                    onClicked: root.runCommand(["exe", "list"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.dotfiles_status_btn")
                    symbol: "check"
                    enabled: !root.busy
                    onClicked: root.runCommand(["dotfiles", "status"])
                }
            }
        }

        // Live Output Card
        SettingsCard {
            visible: !!root.outputReport
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                Text {
                    Layout.fillWidth: true
                    text: I18n.tr("settings.live_report")
                    color: Session.accent
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                }
                IconButton {
                    symbol: "close"
                    implicitWidth: 24
                    implicitHeight: 24
                    onClicked: root.outputReport = ""
                }
            }
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: outText.implicitHeight + 20
                radius: 10
                color: Glass.tint(Session.background, 0.7)
                border.width: 1
                border.color: Glass.tint(Session.accent, 0.22)
                Text {
                    id: outText
                    anchors.fill: parent
                    anchors.margins: 10
                    text: root.outputReport
                    color: Session.foreground
                    font.family: Session.monoFontFamily || Session.fontFamily
                    font.pixelSize: 11
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
