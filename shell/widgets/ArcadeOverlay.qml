pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import Quickshell
import Quickshell.Wayland

// qmllint disable uncreatable-type
PanelWindow {
    // qmllint enable uncreatable-type
    id: overlay
    required property var modelData
    screen: modelData
    anchors { top: true; bottom: true; left: true; right: true }

    readonly property bool isCurrentScreen: !ArcadeState.targetScreen || ArcadeState.targetScreen === (modelData ? modelData.name : "")
    visible: ArcadeState.active && isCurrentScreen
    color: "transparent"

    WlrLayershell.namespace: "poly-arcade"
    WlrLayershell.layer: WlrLayer.Overlay
    WlrLayershell.keyboardFocus: WlrKeyboardFocus.OnDemand

    FocusScope {
        id: focusScope
        anchors.fill: parent
        focus: overlay.visible

        Keys.onEscapePressed: ArcadeState.close()

        // Active Game Canvases
        ArcadeCatchGame {
            id: catchGame
            screenModel: overlay.modelData
            visible: ArcadeState.currentGame === "catch"
        }

        ArcadeFishingGame {
            id: fishingGame
            screenModel: overlay.modelData
            visible: ArcadeState.currentGame === "fishing"
        }

        // Floating HUD Pill at top
        Rectangle {
            id: hudBar
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: Session.visual.barTop + Session.visual.barHeight + 14
            width: hudContent.implicitWidth + 32
            height: 44
            radius: 22
            color: PolyTheme.Theme.withAlpha(Session.surface, 0.90)
            border.width: 1.2
            border.color: Glass.tint(Session.accent, 0.5)

            Row {
                id: hudContent
                anchors.centerIn: parent
                spacing: 12

                Icon {
                    name: "gamepad"
                    width: 18
                    height: 18
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: "ALPORA ARCADE"
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    font.weight: Font.Bold
                    font.letterSpacing: 1.2
                    color: Session.accent
                    anchors.verticalCenter: parent.verticalCenter
                }

                Rectangle {
                    width: 1
                    height: 16
                    color: Glass.tint(Session.foreground, 0.2)
                    anchors.verticalCenter: parent.verticalCenter
                }

                // Game Selector: Catch Tab
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: catchTabText.implicitWidth + 16
                    height: 26
                    radius: 13
                    color: ArcadeState.currentGame === "catch"
                        ? Glass.tint(Session.accent, 0.35)
                        : (catchTabMouse.containsMouse ? Glass.tint(Session.surface, 0.8) : "transparent")
                    border.width: 1
                    border.color: ArcadeState.currentGame === "catch" ? Session.accent : "transparent"

                    Text {
                        id: catchTabText
                        anchors.centerIn: parent
                        text: I18n.tr("arcade.game_catch")
                        font.family: Session.fontFamily
                        font.pixelSize: 11
                        font.weight: ArcadeState.currentGame === "catch" ? Font.Bold : Font.Normal
                        color: ArcadeState.currentGame === "catch" ? Session.accent : Session.foreground
                    }

                    MouseArea {
                        id: catchTabMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: ArcadeState.setGame("catch")
                    }
                }

                // Game Selector: Fishing Tab
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: fishingTabText.implicitWidth + 16
                    height: 26
                    radius: 13
                    color: ArcadeState.currentGame === "fishing"
                        ? Glass.tint(Session.accent, 0.35)
                        : (fishingTabMouse.containsMouse ? Glass.tint(Session.surface, 0.8) : "transparent")
                    border.width: 1
                    border.color: ArcadeState.currentGame === "fishing" ? Session.accent : "transparent"

                    Text {
                        id: fishingTabText
                        anchors.centerIn: parent
                        text: I18n.tr("arcade.game_fishing")
                        font.family: Session.fontFamily
                        font.pixelSize: 11
                        font.weight: ArcadeState.currentGame === "fishing" ? Font.Bold : Font.Normal
                        color: ArcadeState.currentGame === "fishing" ? Session.accent : Session.foreground
                    }

                    MouseArea {
                        id: fishingTabMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: ArcadeState.setGame("fishing")
                    }
                }

                Rectangle {
                    width: 1
                    height: 16
                    color: Glass.tint(Session.foreground, 0.2)
                    anchors.verticalCenter: parent.verticalCenter
                }

                Text {
                    text: I18n.tr("arcade.score") + ": " + ArcadeState.score
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    font.weight: Font.DemiBold
                    color: Session.foreground
                    anchors.verticalCenter: parent.verticalCenter
                }

                // Combo badge
                Rectangle {
                    visible: ArcadeState.combo > 1
                    width: comboText.implicitWidth + 12
                    height: 20
                    radius: 10
                    color: Session.accent
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        id: comboText
                        anchors.centerIn: parent
                        text: "x" + ArcadeState.combo
                        font.family: Session.fontFamily
                        font.pixelSize: 11
                        font.weight: Font.Bold
                        color: Session.background
                    }
                }

                Text {
                    text: I18n.tr("arcade.high_score") + ": " + ArcadeState.highScore
                    font.family: Session.fontFamily
                    font.pixelSize: 12
                    color: Glass.tint(Session.foreground, 0.65)
                    anchors.verticalCenter: parent.verticalCenter
                }

                Rectangle {
                    width: 1
                    height: 16
                    color: Glass.tint(Session.foreground, 0.2)
                    anchors.verticalCenter: parent.verticalCenter
                }

                // Blitz Mode Toggle & Timer
                Rectangle {
                    anchors.verticalCenter: parent.verticalCenter
                    width: blitzContent.implicitWidth + 14
                    height: 26
                    radius: 13
                    color: ArcadeState.blitzMode
                        ? Glass.tint(Session.accent, 0.32)
                        : (blitzMouse.containsMouse ? Glass.tint(Session.surface, 0.8) : "transparent")
                    border.width: 1
                    border.color: ArcadeState.blitzMode ? Session.accent : Glass.tint(Session.foreground, 0.2)

                    Row {
                        id: blitzContent
                        anchors.centerIn: parent
                        spacing: 6

                        Icon {
                            name: "focus"
                            width: 13
                            height: 13
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            anchors.verticalCenter: parent.verticalCenter
                            text: ArcadeState.blitzMode
                                ? (I18n.trWith("arcade.blitz_time", { time: ArcadeState.blitzTimeLeft }))
                                : I18n.tr("arcade.blitz_mode")
                            font.family: Session.fontFamily
                            font.pixelSize: 11
                            font.weight: ArcadeState.blitzMode ? Font.Bold : Font.Normal
                            color: ArcadeState.blitzMode ? Session.accent : Glass.tint(Session.foreground, 0.8)
                        }
                    }

                    MouseArea {
                        id: blitzMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        cursorShape: Qt.PointingHandCursor
                        onClicked: ArcadeState.toggleBlitz()
                    }
                }

                // Sound toggle button
                IconButton {
                    symbol: ArcadeState.soundFx ? "volume" : "muted"
                    implicitWidth: 28
                    implicitHeight: 28
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ArcadeState.toggleSound()
                }

                // Exit button
                IconButton {
                    symbol: "close"
                    implicitWidth: 28
                    implicitHeight: 28
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ArcadeState.close()
                }
            }
        }

        // Blitz 1-second Countdown Loop
        Timer {
            interval: 1000
            running: overlay.visible && ArcadeState.blitzMode && ArcadeState.blitzActive
            repeat: true
            onTriggered: ArcadeState.tickBlitz()
        }

        // Blitz Game Over Banner
        Rectangle {
            anchors.centerIn: parent
            width: 320
            height: 170
            radius: 20
            visible: ArcadeState.blitzMode && ArcadeState.blitzTimeLeft === 0
            color: PolyTheme.Theme.withAlpha(Session.surface, 0.95)
            border.width: 2
            border.color: PolyTheme.Theme.secondary
            z: 99

            Column {
                anchors.centerIn: parent
                spacing: 12
                width: parent.width - 40

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: I18n.tr("arcade.blitz_over")
                    font.family: Session.fontFamily
                    font.pixelSize: 22
                    font.weight: Font.Bold
                    color: PolyTheme.Theme.secondary
                }

                Text {
                    anchors.horizontalCenter: parent.horizontalCenter
                    text: I18n.tr("arcade.score") + ": " + ArcadeState.score + "  ·  " + I18n.tr("arcade.high_score") + ": " + ArcadeState.highScore
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    color: Session.foreground
                }

                Rectangle {
                    anchors.horizontalCenter: parent.horizontalCenter
                    width: replayText.implicitWidth + 24
                    height: 32
                    radius: 16
                    color: Session.accent

                    Text {
                        id: replayText
                        anchors.centerIn: parent
                        text: "Play Again"
                        font.family: Session.fontFamily
                        font.pixelSize: 12
                        font.weight: Font.Bold
                        color: Session.background
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor
                        onClicked: ArcadeState.open(ArcadeState.currentGame, ArcadeState.targetScreen)
                    }
                }
            }
        }

        // Floating score celebration label
        Text {
            id: scorePopup
            visible: opacity > 0
            opacity: 0
            text: "+100!"
            font.family: Session.fontFamily
            font.pixelSize: 22
            font.weight: Font.Bold
            color: PolyTheme.Theme.secondary

            NumberAnimation {
                id: popupYAnim
                target: scorePopup
                property: "y"
                duration: 600
                easing.type: Easing.OutCubic
            }
            NumberAnimation {
                id: popupFadeAnim
                target: scorePopup
                property: "opacity"
                duration: 600
                from: 1.0; to: 0.0
                easing.type: Easing.InQuad
            }
        }
    }

    Connections {
        target: ArcadeState
        function onScoreAdded(pts: int, mult: int): void {
            scorePopup.text = mult > 1 ? ("+" + pts + " COMBO x" + mult + "!") : ("+" + pts + "!");
            scorePopup.x = (overlay.width / 2) - scorePopup.implicitWidth / 2;
            scorePopup.y = overlay.height / 2 - 40;
            popupYAnim.from = overlay.height / 2 - 40;
            popupYAnim.to = overlay.height / 2 - 90;
            popupYAnim.start();
            popupFadeAnim.restart();
        }
    }
}
