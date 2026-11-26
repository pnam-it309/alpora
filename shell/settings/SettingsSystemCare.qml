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
    property string commandOutput: ""

    function runAction(args: var): void {
        if (actionRunner.running) return;
        root.busy = true;
        actionRunner.command = [Session.controller].concat(args);
        actionRunner.running = true;
    }

    Component.onCompleted: root.runAction(["memory", "status"])

    Process {
        id: actionRunner
        stdout: StdioCollector {
            onStreamFinished: {
                root.busy = false;
                if (text.trim()) {
                    root.commandOutput = text.trim();
                }
            }
        }
        stderr: StdioCollector {
            onStreamFinished: {
                if (text.trim()) {
                    root.commandOutput = text.trim();
                }
            }
        }
        onExited: root.busy = false
    }

    ColumnLayout {
        width: root.availableWidth
        spacing: 14

        // 1. Memory Shield, zRAM & Workspace Eco Optimizer
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "performance"
                    tint: PolyTheme.Theme.color("#a8d5bc")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.memory_shield_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.memory_shield_desc")
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
                    text: I18n.tr("settings.memory_drop_btn")
                    symbol: "refresh"
                    primary: true
                    enabled: !root.busy
                    onClicked: root.runAction(["memory", "drop"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.memory_eco_btn")
                    symbol: "leaf"
                    enabled: !root.busy
                    onClicked: root.runAction(["memory", "eco"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.memory_status_btn")
                    symbol: "performance"
                    enabled: !root.busy
                    onClicked: root.runAction(["memory", "status"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.memory_zram_btn")
                    symbol: "shield"
                    enabled: !root.busy
                    onClicked: root.runAction(["memory", "setup-zram"])
                }
            }
        }

        // 2. CleanGuard Storage & Anti-Bloat Cache Cleaner
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "delete"
                    tint: PolyTheme.Theme.color("#edb493")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.storage_guard_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.storage_guard_desc")
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
                    text: I18n.tr("settings.storage_status_btn")
                    symbol: "devices"
                    enabled: !root.busy
                    onClicked: root.runAction(["storage", "status"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.storage_clean_btn")
                    symbol: "delete"
                    primary: true
                    enabled: !root.busy
                    onClicked: root.runAction(["storage", "clean"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.windows_drives_btn")
                    symbol: "window"
                    enabled: !root.busy
                    onClicked: root.runAction(["windows-drives", "list"])
                }
            }
        }

        // 3. Btrfs Instant System Snapshots & Rollback
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 12
                SettingsBadge {
                    symbol: "shield"
                    tint: PolyTheme.Theme.color("#9cc8df")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    Text {
                        text: I18n.tr("settings.snapshots_title")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 18
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: I18n.tr("settings.snapshots_desc")
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
                    text: I18n.tr("settings.snapshot_list_btn")
                    symbol: "calendar"
                    enabled: !root.busy
                    onClicked: root.runAction(["snapshot", "list"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.snapshot_create_btn")
                    symbol: "plus"
                    primary: true
                    enabled: !root.busy
                    onClicked: root.runAction(["snapshot", "create", "ALPORA Settings Manual Backup"])
                }
            }
        }

        // Live Output Terminal Console inside Settings
        SettingsCard {
            visible: !!root.commandOutput
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
                    onClicked: root.commandOutput = ""
                }
            }
            Rectangle {
                Layout.fillWidth: true
                implicitHeight: reportText.implicitHeight + 20
                radius: 10
                color: Glass.tint(Session.background, 0.7)
                border.width: 1
                border.color: Glass.tint(Session.accent, 0.22)
                Text {
                    id: reportText
                    anchors.fill: parent
                    anchors.margins: 10
                    text: root.commandOutput
                    color: Session.foreground
                    font.family: Session.monoFontFamily || Session.fontFamily
                    font.pixelSize: 11
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
