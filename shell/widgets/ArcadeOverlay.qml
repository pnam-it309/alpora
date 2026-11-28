pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Shapes
import Quickshell
import Quickshell.Io
import Quickshell.Hyprland
import Quickshell.Wayland

// qmllint disable uncreatable-type
PanelWindow {
    // qmllint enable uncreatable-type
    id: overlay
    required property var modelData
    screen: modelData
    anchors { top: true; bottom: true; left: true; right: true }

    readonly property real screenWidth: modelData ? modelData.width : 1920
    readonly property real screenHeight: modelData ? modelData.height : 1080
    readonly property var monitor: modelData ? Hyprland.monitorFor(modelData) : null
    readonly property int activeWorkspace: monitor && monitor.activeWorkspace ? monitor.activeWorkspace.id : 1

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

        // Background click & drag catcher
        MouseArea {
            id: playArea
            anchors.fill: parent
            hoverEnabled: true

            property real dragStartX: 0
            property real dragStartY: 0
            property bool isAiming: false

            onPressed: function(mouse) {
                // If clicked near ball, start aiming
                const d = Math.hypot(mouse.x - ball.x, mouse.y - ball.y);
                if (d < 45) {
                    isAiming = true;
                    dragStartX = ball.x;
                    dragStartY = ball.y;
                    physicsTimer.stop();
                } else {
                    // Click elsewhere launches ball toward click
                    const dx = mouse.x - ball.x;
                    const dy = mouse.y - ball.y;
                    const len = Math.max(1, Math.hypot(dx, dy));
                    ball.vx = (dx / len) * 18;
                    ball.vy = Math.min(-6, (dy / len) * 18);
                    physicsTimer.restart();
                }
            }

            onPositionChanged: function(mouse) {
                if (isAiming) {
                    aimIndicator.targetX = mouse.x;
                    aimIndicator.targetY = mouse.y;
                }
            }

            onReleased: function(mouse) {
                if (isAiming) {
                    isAiming = false;
                    const pullX = dragStartX - mouse.x;
                    const pullY = dragStartY - mouse.y;
                    ball.vx = Math.max(-28, Math.min(28, pullX * 0.18));
                    ball.vy = Math.max(-28, Math.min(28, pullY * 0.18));
                    physicsTimer.restart();
                }
            }
        }

        // Floating HUD pill at top
        Rectangle {
            id: hudBar
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: parent.top
            anchors.topMargin: Session.visual.barTop + Session.visual.barHeight + 14
            width: hudContent.implicitWidth + 32
            height: 44
            radius: 22
            color: PolyTheme.Theme.withAlpha(Session.surface, 0.88)
            border.width: 1.2
            border.color: Glass.tint(Session.accent, 0.5)

            Row {
                id: hudContent
                anchors.centerIn: parent
                spacing: 14

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

                // Sound toggle button
                IconButton {
                    name: ArcadeState.soundFx ? "volume" : "muted"
                    size: 16
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ArcadeState.toggleSound()
                }

                // Exit button
                IconButton {
                    name: "close"
                    size: 16
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: ArcadeState.close()
                }
            }
        }

        // Aim slingshot indicator line
        Shape {
            id: aimIndicator
            anchors.fill: parent
            visible: playArea.isAiming
            property real targetX: 0
            property real targetY: 0

            ShapePath {
                strokeColor: Session.accent
                strokeWidth: 2.5
                strokeStyle: ShapePath.DashLine
                dashPattern: [4, 4]
                fillColor: "transparent"
                startX: ball.x; startY: ball.y
                PathLine { x: aimIndicator.targetX; y: aimIndicator.targetY }
            }
        }

        // The Bouncing Ball
        Item {
            id: ball
            x: overlay.screenWidth / 2
            y: overlay.screenHeight / 3
            property real vx: 4.5
            property real vy: -2.0
            readonly property real radius: 18

            // Synchronize position to ArcadeState
            onXChanged: ArcadeState.ballX = ball.x
            onYChanged: ArcadeState.ballY = ball.y

            // Visual Ball Circle
            Rectangle {
                anchors.centerIn: parent
                width: ball.radius * 2
                height: ball.radius * 2
                radius: ball.radius
                color: Session.accent
                border.width: 2
                border.color: PolyTheme.Theme.secondary

                // Cute sparkle highlight
                Rectangle {
                    x: 6; y: 6
                    width: 7; height: 7
                    radius: 3.5
                    color: "white"
                    opacity: 0.8
                }
            }

            // Glow / Shadow behind ball
            Rectangle {
                anchors.centerIn: parent
                width: ball.radius * 2 + 10
                height: ball.radius * 2 + 10
                radius: width / 2
                color: Glass.tint(Session.accent, 0.25)
                z: -1
            }
        }

        // Floating score celebration label
        Text {
            id: scorePopup
            property real targetY: 0
            visible: opacity > 0
            opacity: 0
            text: "+100!"
            font.family: Session.fontFamily
            font.pixelSize: 22
            font.weight: Font.Bold
            color: PolyTheme.Theme.secondary

            NumberAnimation on y {
                id: popupYAnim
                duration: 600
                easing.type: Easing.OutCubic
            }
            NumberAnimation on opacity {
                id: popupFadeAnim
                duration: 600
                from: 1.0; to: 0.0
                easing.type: Easing.InQuad
            }
        }

        // Bottom control hint
        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 24
            width: hintText.implicitWidth + 24
            height: 28
            radius: 14
            color: PolyTheme.Theme.withAlpha(Session.surface, 0.75)

            Text {
                id: hintText
                anchors.centerIn: parent
                text: I18n.tr("arcade.throw_ball") + "  ·  " + I18n.tr("arcade.exit_hint")
                font.family: Session.fontFamily
                font.pixelSize: 11
                color: Glass.tint(Session.foreground, 0.7)
            }
        }

        // Main 60 FPS Physics Simulation Loop
        Timer {
            id: physicsTimer
            interval: 16
            running: overlay.visible && !playArea.isAiming
            repeat: true
            onTriggered: overlay.stepPhysics()
        }
    }

    Connections {
        target: ArcadeState
        function onScoreAdded(pts: int, mult: int): void {
            scorePopup.text = mult > 1 ? ("+" + pts + " COMBO x" + mult + "!") : ("+" + pts + "!");
            scorePopup.x = ball.x - scorePopup.implicitWidth / 2;
            scorePopup.y = ball.y - 30;
            popupYAnim.from = ball.y - 30;
            popupYAnim.to = ball.y - 80;
            popupYAnim.start();
            popupFadeAnim.restart();
        }
    }

    function stepPhysics(): void {
        const r = ball.radius;
        const g = 0.44;
        const friction = 0.995;
        const restitution = 0.78;

        ball.vy += g;
        ball.vx *= friction;

        let nextX = ball.x + ball.vx;
        let nextY = ball.y + ball.vy;

        // Screen boundaries
        if (nextX - r < 0) {
            nextX = r;
            ball.vx = -ball.vx * restitution;
        } else if (nextX + r > screenWidth) {
            nextX = screenWidth - r;
            ball.vx = -ball.vx * restitution;
        }

        if (nextY - r < Session.visual.barTop + Session.visual.barHeight) {
            nextY = Session.visual.barTop + Session.visual.barHeight + r;
            ball.vy = -ball.vy * restitution;
        } else if (nextY + r > screenHeight - 8) {
            nextY = screenHeight - 8 - r;
            ball.vy = -ball.vy * restitution;
            // Floor bounce drops combo if moving slowly
            if (Math.abs(ball.vy) < 2.0) {
                ball.vy = 0;
                ArcadeState.dropBall();
            }
        }

        // Window collisions (Hyprland toplevels on this workspace)
        const clients = Hyprland.toplevels.values;
        for (let i = 0; i < clients.length; ++i) {
            const w = clients[i].lastIpcObject;
            if (!w || !w.workspace || w.workspace.id !== activeWorkspace) continue;
            const wx = w.at[0] - (modelData ? modelData.x : 0);
            const wy = w.at[1] - (modelData ? modelData.y : 0);
            const ww = w.size[0];
            const wh = w.size[1];

            // Window top bounce check
            if (nextX >= wx && nextX <= wx + ww && nextY + r >= wy && nextY - r <= wy + 20 && ball.vy > 0) {
                nextY = wy - r;
                ball.vy = -Math.abs(ball.vy) * restitution;
                break;
            }
        }

        // Companion catch collision
        if (ArcadeState.companionPresent) {
            const cx = ArcadeState.companionX + 24;
            const cy = ArcadeState.companionY + 24;
            const dist = Math.hypot(nextX - cx, nextY - cy);
            if (dist < 58 && (Math.abs(ball.vx) > 0.5 || Math.abs(ball.vy) > 0.5)) {
                ArcadeState.petCatch();
                ArcadeState.addScore(100);
                // Launch ball back playfully
                ball.vy = -(12 + Math.random() * 5);
                ball.vx = (Math.random() - 0.5) * 16;
                nextY = cy - 40;
            }
        }

        ball.x = nextX;
        ball.y = nextY;
    }

    Component.onCompleted: {
        ball.x = screenWidth / 2;
        ball.y = screenHeight / 3;
    }
}
