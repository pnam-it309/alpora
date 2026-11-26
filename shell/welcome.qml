//@ pragma AppId poly-shell-welcome
//@ pragma Env QSG_RENDER_LOOP=threaded
//@ pragma Env QSG_USE_SIMPLE_ANIMATION_DRIVER=1
//@ pragma UseQApplication
pragma ComponentBehavior: Bound
import QtQuick
import "theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland

ShellRoot {
    id: root

    property string currentTab: "shortcuts"
    property bool dontShowAgain: false

    function close(): void {
        if (dontShowAgain) {
            dismissWriter.running = true;
        }
        welcomeWindow.visible = false;
        welcomeWindow.close();
        Qt.quit();
    }

    function show(): void {
        welcomeWindow.visible = true;
        welcomeWindow.minimized = false;
        Hyprland.dispatch(Hyprland.usingLua ? 'hl.dsp.focus({ window = "class:^poly-shell-welcome$" })' : 'focuswindow class:^poly-shell-welcome$');
    }

    IpcHandler {
        target: "welcome-app"
        function raiseWindow(): void {
            root.show();
        }
        function close(): void {
            root.close();
        }
    }

    Process {
        id: dismissWriter
        command: ["bash", "-c", "mkdir -p ~/.local/state/poly-shell && touch ~/.local/state/poly-shell/welcome-dismissed"]
    }

    Process {
        id: fcitxRestart
        command: ["fcitx5", "-d", "--replace"]
    }

    FloatingWindow {
        id: welcomeWindow
        title: I18n.tr("welcome.window_title")
        implicitWidth: 840
        implicitHeight: 560
        minimumSize: Qt.size(800, 520)
        color: "transparent"
        visible: true

        Shortcut {
            sequence: "Escape"
            onActivated: root.close()
        }

        Rectangle {
            id: container
            anchors.fill: parent
            radius: Math.min(20, Session.visual.panelRadius)
            color: Glass.tint(Session.surface, 0.94)
            border.width: Session.visual.panelBorder
            border.color: Glass.tint(Session.accent, 0.35)

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 24
                spacing: 16

                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    FacetedMark {
                        width: 40
                        height: 40
                        Layout.alignment: Qt.AlignVCenter
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: 2

                        Text {
                            text: I18n.tr("welcome.welcome_heading")
                            color: Session.foreground
                            font.family: Session.fontFamily
                            font.pixelSize: 20
                            font.weight: Font.Bold
                        }

                        Text {
                            text: I18n.tr("welcome.welcome_subheading")
                            color: Session.muted
                            font.family: Session.fontFamily
                            font.pixelSize: 12
                        }
                    }

                    Button {
                        Layout.preferredWidth: 32
                        Layout.preferredHeight: 32
                        onClicked: root.close()
                        background: Rectangle {
                            radius: 16
                            color: parent.hovered ? Glass.tint(Session.accent, 0.25) : Glass.tint(Session.foreground, 0.08)
                        }
                        contentItem: Icon {
                            name: "close"
                            anchors.centerIn: parent
                            width: 14; height: 14
                            color: Session.foreground
                        }
                    }
                }

                // Tab Switcher
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 8

                    Repeater {
                        model: [
                            {
                                id: "shortcuts",
                                label: I18n.tr("welcome.tab_shortcuts")
                            },
                            {
                                id: "ime",
                                label: I18n.tr("welcome.tab_ime")
                            },
                            {
                                id: "themes",
                                label: I18n.tr("welcome.tab_themes")
                            },
                            {
                                id: "doctor",
                                label: I18n.tr("welcome.tab_doctor")
                            }
                        ]

                        Button {
                            required property var modelData
                            Layout.fillWidth: true
                            Layout.preferredHeight: 36
                            checkable: true
                            checked: root.currentTab === modelData.id
                            onClicked: root.currentTab = modelData.id

                            background: Rectangle {
                                radius: 8
                                color: checked ? Session.accent : (parent.hovered ? Glass.tint(Session.foreground, 0.1) : Glass.tint(Session.foreground, 0.04))
                                border.width: checked ? 0 : 1
                                border.color: Glass.tint(Session.foreground, 0.1)
                            }

                            contentItem: Text {
                                text: modelData.label
                                color: checked ? Session.surface : Session.foreground
                                font.family: Session.fontFamily
                                font.pixelSize: 12
                                font.weight: checked ? Font.DemiBold : Font.Normal
                                horizontalAlignment: Text.AlignHCenter
                                verticalAlignment: Text.AlignVCenter
                            }
                        }
                    }
                }

                // Content Area
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    radius: 12
                    color: Glass.tint(Session.surface, 0.5)
                    border.width: 1
                    border.color: Glass.tint(Session.foreground, 0.08)
                    clip: true

                    WelcomeShortcutsTab {
                        visible: root.currentTab === "shortcuts"
                    }
                    WelcomeImeTab {
                        visible: root.currentTab === "ime"
                        restarting: fcitxRestart.running
                        onRestartRequested: fcitxRestart.running = true
                    }
                    WelcomeThemesTab {
                        visible: root.currentTab === "themes"
                    }
                    WelcomeDoctorTab {
                        visible: root.currentTab === "doctor"
                        onCloseRequested: root.close()
                    }
                }

                // Footer
                RowLayout {
                    Layout.fillWidth: true
                    spacing: 16

                    CheckBox {
                        id: checkDontShow
                        text: I18n.tr("welcome.dont_show_again")
                        checked: root.dontShowAgain
                        onCheckedChanged: root.dontShowAgain = checked
                    }

                    Item {
                        Layout.fillWidth: true
                    }

                    Button {
                        text: I18n.tr("welcome.get_started")
                        Layout.preferredHeight: 38
                        Layout.preferredWidth: 160
                        onClicked: root.close()
                        background: Rectangle {
                            radius: 8
                            color: Session.accent
                        }
                        contentItem: Text {
                            text: I18n.tr("welcome.get_started")
                            color: Session.surface
                            font.family: Session.fontFamily
                            font.pixelSize: 12
                            font.weight: Font.Bold
                            horizontalAlignment: Text.AlignHCenter
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
            }
        }
    }
}
