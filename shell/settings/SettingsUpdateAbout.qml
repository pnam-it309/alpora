pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io

ScrollView {
    id: root
    signal navigate(string page)
    clip: true
    contentWidth: availableWidth

    property bool checkingUpdate: false
    property bool applyingUpdate: false
    property bool runningDoctor: false
    property string currentVersion: "1.0.0"
    property string latestVersion: "1.0.0"
    property bool hasUpdate: false
    property string releaseTitle: ""
    property string releaseNotes: ""
    property string publishedAt: ""
    property string updateStatusText: ""
    property string doctorOutput: ""

    function launchTerminal(args: var): void {
        const term = (Session.settings && Session.settings.apps && Session.settings.apps.terminal) ? Session.settings.apps.terminal : ["kitty"];
        Quickshell.execDetached(term.concat(["-e"]).concat(args));
    }

    function checkUpdates(): void {
        if (updateChecker.running) return;
        root.checkingUpdate = true;
        root.updateStatusText = I18n.tr("settings.update_checking");
        updateChecker.command = [Session.controller, "update", "check", "--json"];
        updateChecker.running = true;
    }

    function applyUpdateInline(): void {
        if (updateApplier.running) return;
        root.applyingUpdate = true;
        root.updateStatusText = I18n.tr("settings.update_applying");
        updateApplier.command = [Session.controller, "update", "apply"];
        updateApplier.running = true;
    }

    function runDoctor(bundle: bool): void {
        if (doctorRunner.running) return;
        root.runningDoctor = true;
        doctorRunner.command = bundle ? [Session.controller, "doctor", "--bundle"] : [Session.controller, "doctor"];
        doctorRunner.running = true;
    }

    Component.onCompleted: root.checkUpdates()

    Process {
        id: updateChecker
        stdout: StdioCollector {
            onStreamFinished: {
                root.checkingUpdate = false;
                try {
                    const info = JSON.parse(text.trim());
                    root.currentVersion = info.current_version || "1.0.0";
                    root.latestVersion = info.latest_version || root.currentVersion;
                    root.hasUpdate = !!info.has_update;
                    root.releaseTitle = info.release_title || "";
                    root.releaseNotes = info.release_notes || "";
                    root.publishedAt = info.published_at ? String(info.published_at).slice(0, 10) : "";
                    root.updateStatusText = root.hasUpdate ? I18n.tr("settings.update_available") : I18n.tr("settings.update_up_to_date");
                } catch (_) {
                    root.updateStatusText = I18n.tr("settings.update_up_to_date");
                }
            }
        }
        onExited: root.checkingUpdate = false
    }

    Process {
        id: updateApplier
        stdout: StdioCollector {
            onStreamFinished: {
                root.applyingUpdate = false;
                if (text.trim()) {
                    root.updateStatusText = text.trim().split("\n").slice(-1)[0];
                }
                root.checkUpdates();
            }
        }
        stderr: StdioCollector {
            onStreamFinished: {
                if (text.trim()) {
                    root.updateStatusText = text.trim();
                }
            }
        }
        onExited: root.applyingUpdate = false
    }

    Process {
        id: doctorRunner
        stdout: StdioCollector {
            onStreamFinished: {
                root.runningDoctor = false;
                root.doctorOutput = text.trim();
            }
        }
        onExited: root.runningDoctor = false
    }

    ColumnLayout {
        width: root.availableWidth
        spacing: 14

        // 1. Hero System Update Card (OTA + TUI Updater)
        SettingsCard {
            Layout.fillWidth: true
            RowLayout {
                Layout.fillWidth: true
                spacing: 14
                SettingsBadge {
                    symbol: "refresh"
                    tint: root.hasUpdate ? PolyTheme.Theme.color("#edb493") : PolyTheme.Theme.color("#a8d5bc")
                }
                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: 4
                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 10
                        Text {
                            text: I18n.tr("settings.update_title")
                            color: PolyTheme.Theme.color("#eff1f4")
                            font.family: Session.fontFamily
                            font.pixelSize: 19
                            font.weight: Font.DemiBold
                        }
                        Rectangle {
                            radius: 8
                            implicitHeight: 22
                            implicitWidth: badgeText.implicitWidth + 16
                            color: root.hasUpdate ? Glass.tint(PolyTheme.Theme.color("#edb493"), 0.22) : Glass.tint(PolyTheme.Theme.color("#a8d5bc"), 0.2)
                            border.width: 1
                            border.color: root.hasUpdate ? PolyTheme.Theme.color("#edb493") : PolyTheme.Theme.color("#a8d5bc")
                            Text {
                                id: badgeText
                                anchors.centerIn: parent
                                text: "v" + root.currentVersion + (root.hasUpdate ? " → " + root.latestVersion : " · OK")
                                color: root.hasUpdate ? PolyTheme.Theme.color("#edb493") : PolyTheme.Theme.color("#a8d5bc")
                                font.family: Session.monoFontFamily || Session.fontFamily
                                font.pixelSize: 11
                                font.weight: Font.DemiBold
                            }
                        }
                    }
                    Text {
                        Layout.fillWidth: true
                        text: root.updateStatusText || I18n.tr("settings.update_desc")
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 13
                        wrapMode: Text.Wrap
                    }
                }
            }

            Rectangle {
                Layout.fillWidth: true
                implicitHeight: 1
                color: Glass.tint(Session.muted, 0.18)
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 6
                columnSpacing: 16
                Text { text: I18n.tr("settings.current_version"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: "ALPORA OS v" + root.currentVersion; color: Session.foreground; font.family: Session.monoFontFamily || Session.fontFamily; font.pixelSize: 12; font.weight: Font.DemiBold }
                Text { text: I18n.tr("settings.latest_version"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: root.latestVersion + (root.publishedAt ? " (" + root.publishedAt + ")" : ""); color: Session.accent; font.family: Session.monoFontFamily || Session.fontFamily; font.pixelSize: 12; font.weight: Font.DemiBold }
            }

            Rectangle {
                visible: !!root.releaseNotes
                Layout.fillWidth: true
                implicitHeight: notesCol.implicitHeight + 20
                radius: 10
                color: Glass.tint(Session.surface, 0.45)
                border.width: 1
                border.color: Glass.tint(Session.accent, 0.2)
                ColumnLayout {
                    id: notesCol
                    anchors.fill: parent
                    anchors.margins: 10
                    spacing: 4
                    Text {
                        text: root.releaseTitle || "Changelog"
                        color: Session.accent
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        font.weight: Font.DemiBold
                    }
                    Text {
                        Layout.fillWidth: true
                        text: root.releaseNotes
                        color: Session.foreground
                        font.family: Session.monoFontFamily || Session.fontFamily
                        font.pixelSize: 11
                        wrapMode: Text.Wrap
                    }
                }
            }

            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.update_open_tui")
                    symbol: "terminal"
                    primary: true
                    onClicked: root.launchTerminal([Session.controller, "update", "tui"])
                }
                AppearanceButton {
                    text: root.checkingUpdate ? I18n.tr("settings.update_checking") : I18n.tr("settings.update_check_btn")
                    symbol: "refresh"
                    enabled: !root.checkingUpdate && !root.applyingUpdate
                    onClicked: root.checkUpdates()
                }
                AppearanceButton {
                    text: root.applyingUpdate ? I18n.tr("settings.update_applying") : I18n.tr("settings.update_apply_btn")
                    symbol: "check"
                    enabled: !root.applyingUpdate && !root.checkingUpdate
                    onClicked: root.applyUpdateInline()
                }
            }
        }

        // 2. System Specs & Architecture Overview
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
                        text: I18n.tr("settings.about")
                        color: PolyTheme.Theme.color("#eff1f4")
                        font.family: Session.fontFamily
                        font.pixelSize: 17
                        font.weight: Font.DemiBold
                    }
                    Text {
                        text: "ALPORA Desktop Shell · Quickshell & Wayland Compositor HAL"
                        color: PolyTheme.Theme.color("#bec7ce")
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                    }
                }
            }

            GridLayout {
                Layout.fillWidth: true
                columns: 2
                rowSpacing: 8
                columnSpacing: 18

                Text { text: I18n.tr("settings.current_mode"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: Session.mode === "vibe" ? "Vibe Mode" : "Work Mode"; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12; font.weight: Font.Medium }

                Text { text: I18n.tr("settings.current_theme"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: PolyTheme.Theme.label; color: Session.accent; font.family: Session.fontFamily; font.pixelSize: 12; font.weight: Font.Medium }

                Text { text: I18n.tr("settings.font_family"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: Session.fontFamily; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12 }

                Text { text: I18n.tr("settings.power"); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 12 }
                Text { text: Session.batteryDescription; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12 }
            }

            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.open_system_card")
                    symbol: "monitor"
                    onClicked: root.launchTerminal(["alpora-fetch"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.open_welcome_wizard")
                    symbol: "home"
                    onClicked: Quickshell.execDetached([Session.controller, "welcome"])
                }
                AppearanceButton {
                    text: I18n.tr("settings.open_task_manager")
                    symbol: "performance"
                    onClicked: Quickshell.execDetached([Session.controller, "task-manager"])
                }
            }
        }

        // 3. System Health Doctor & Diagnostic Bundle
        SettingsCard {
            Layout.fillWidth: true
            Text {
                text: I18n.tr("settings.diagnostics_title")
                color: PolyTheme.Theme.color("#eff1f4")
                font.family: Session.fontFamily
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.diagnostics_desc")
                color: PolyTheme.Theme.color("#bec7ce")
                font.family: Session.fontFamily
                font.pixelSize: 12
                wrapMode: Text.Wrap
            }
            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: I18n.tr("settings.run_doctor")
                    symbol: "check"
                    enabled: !root.runningDoctor
                    onClicked: root.runDoctor(false)
                }
                AppearanceButton {
                    text: I18n.tr("settings.export_diagnostics")
                    symbol: "copy"
                    enabled: !root.runningDoctor
                    onClicked: root.runDoctor(true)
                }
            }
            Rectangle {
                visible: !!root.doctorOutput
                Layout.fillWidth: true
                implicitHeight: docText.implicitHeight + 20
                radius: 10
                color: Glass.tint(Session.background, 0.65)
                border.width: 1
                border.color: Glass.tint(Session.muted, 0.25)
                Text {
                    id: docText
                    anchors.fill: parent
                    anchors.margins: 10
                    text: root.doctorOutput
                    color: Session.foreground
                    font.family: Session.monoFontFamily || Session.fontFamily
                    font.pixelSize: 11
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
