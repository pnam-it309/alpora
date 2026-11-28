pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import "../logic/ArcadePhysics.js" as ArcadePhysics
import QtQuick.Shapes
import Quickshell.Hyprland

Item {
    id: catchGame
    anchors.fill: parent

    required property var screenModel
    readonly property real screenWidth: screenModel ? screenModel.width : 1920
    readonly property real screenHeight: screenModel ? screenModel.height : 1080
    readonly property var monitor: screenModel ? Hyprland.monitorFor(screenModel) : null
    readonly property int activeWorkspace: monitor && monitor.activeWorkspace ? monitor.activeWorkspace.id : 1

    onVisibleChanged: {
        if (!visible) {
            playArea.isAiming = false;
            ball.vx = 4.5;
            ball.vy = -2.0;
            ball.x = catchGame.screenWidth / 2;
            ball.y = catchGame.screenHeight / 3;
        }
    }

    Connections {
        target: ArcadeState
        function onBlitzEnded(): void {
            playArea.isAiming = false;
            physicsTimer.stop();
        }
    }

    // Background click & drag catcher
    MouseArea {
        id: playArea
        anchors.fill: parent
        hoverEnabled: true

        property real dragStartX: 0
        property real dragStartY: 0
        property bool isAiming: false

        onPressed: function(mouse) {
            const d = Math.hypot(mouse.x - ball.x, mouse.y - ball.y);
            if (d < 48) {
                isAiming = true;
                dragStartX = ball.x;
                dragStartY = ball.y;
                physicsTimer.stop();
            } else {
                const dx = mouse.x - ball.x;
                const dy = mouse.y - ball.y;
                const pVel = ArcadePhysics.calculatePointVelocity(dx, dy, 18);
                ball.vx = pVel.vx;
                ball.vy = pVel.vy;
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
                const tVel = ArcadePhysics.calculateThrowVelocity(pullX, pullY);
                ball.vx = tVel.vx;
                ball.vy = tVel.vy;
                physicsTimer.restart();
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

    // Particle Burst System for Catches and Collisions
    Item {
        id: burstContainer
        anchors.fill: parent

        function triggerBurst(cx: real, cy: real): void {
            burstAnim.stop();
            burstOrigin.x = cx;
            burstOrigin.y = cy;
            burstProgress.val = 0.0;
            burstAnim.restart();
        }

        QtObject {
            id: burstOrigin
            property real x: 0
            property real y: 0
        }

        QtObject {
            id: burstProgress
            property real val: 0.0
        }

        NumberAnimation {
            id: burstAnim
            target: burstProgress
            property: "val"
            from: 0.0
            to: 1.0
            duration: 650
            easing.type: Easing.OutCubic
        }

        Repeater {
            model: 12
            delegate: Rectangle {
                id: particle
                required property int index
                readonly property real angle: (index * 30) * Math.PI / 180
                readonly property real maxDistance: 45 + (index % 3) * 20
                readonly property real currentDist: burstProgress.val * maxDistance

                x: burstOrigin.x + Math.cos(angle) * currentDist - width / 2
                y: burstOrigin.y + Math.sin(angle) * currentDist - height / 2
                width: Math.max(0, (1.0 - burstProgress.val) * (index % 2 === 0 ? 10 : 7))
                height: width
                radius: index % 2 === 0 ? 2 : width / 2
                rotation: burstProgress.val * 240 + (index * 25)
                color: index % 2 === 0 ? Session.accent : PolyTheme.Theme.secondary
                opacity: (1.0 - burstProgress.val) * 0.95
                visible: burstAnim.running
            }
        }
    }

    // The Bouncing Ball with Squash & Stretch
    Item {
        id: ball
        x: catchGame.screenWidth / 2
        y: catchGame.screenHeight / 3
        property real vx: 4.5
        property real vy: -2.0
        readonly property real radius: 18

        property real squashX: 1.0
        property real squashY: 1.0

        // Synchronize position to ArcadeState
        onXChanged: ArcadeState.ballX = ball.x
        onYChanged: ArcadeState.ballY = ball.y

        transform: Scale {
            origin.x: ball.radius
            origin.y: ball.radius
            xScale: ball.squashX
            yScale: ball.squashY
        }

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
                color: PolyTheme.Theme.withAlpha(Session.foreground, 0.85)
                opacity: 0.8
            }
        }

        // Soft ambient glow behind ball
        Rectangle {
            anchors.centerIn: parent
            width: ball.radius * 2 + 10
            height: ball.radius * 2 + 10
            radius: width / 2
            color: Glass.tint(Session.accent, 0.25)
            z: -1
        }

        // Squash & stretch recovery animations
        NumberAnimation {
            id: recoveryX
            target: ball
            property: "squashX"
            to: 1.0
            duration: 240
            easing.type: Easing.OutBack
        }

        NumberAnimation {
            id: recoveryY
            target: ball
            property: "squashY"
            to: 1.0
            duration: 240
            easing.type: Easing.OutBack
        }

        function triggerVerticalSquash(): void {
            squashX = 1.45;
            squashY = 0.55;
            recoveryX.restart();
            recoveryY.restart();
        }

        function triggerHorizontalSquash(): void {
            squashX = 0.55;
            squashY = 1.45;
            recoveryX.restart();
            recoveryY.restart();
        }

        function triggerCatchSquash(): void {
            squashX = 1.4;
            squashY = 1.4;
            recoveryX.restart();
            recoveryY.restart();
        }
    }

    // Main 60 FPS Physics Simulation Loop
    Timer {
        id: physicsTimer
        interval: 16
        running: catchGame.visible && !playArea.isAiming
        repeat: true
        onTriggered: catchGame.stepPhysics()
    }

    function stepPhysics(): void {
        const r = ball.radius;
        const g = ArcadePhysics.GRAVITY;
        const friction = ArcadePhysics.FRICTION;
        const restitution = ArcadePhysics.RESTITUTION;

        ball.vy += g;
        ball.vx *= friction;

        let nextX = ball.x + ball.vx;
        let nextY = ball.y + ball.vy;

        // Screen boundaries
        if (nextX - r < 0) {
            nextX = r;
            ball.vx = -ball.vx * restitution;
            ball.triggerHorizontalSquash();
        } else if (nextX + r > screenWidth) {
            nextX = screenWidth - r;
            ball.vx = -ball.vx * restitution;
            ball.triggerHorizontalSquash();
        }

        if (nextY - r < Session.visual.barTop + Session.visual.barHeight) {
            nextY = Session.visual.barTop + Session.visual.barHeight + r;
            ball.vy = -ball.vy * restitution;
            ball.triggerVerticalSquash();
        } else if (nextY + r > screenHeight - 8) {
            nextY = screenHeight - 8 - r;
            ball.vy = -ball.vy * restitution;
            ball.triggerVerticalSquash();
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
            if (!w || !w.workspace || w.workspace.id !== activeWorkspace || w.hidden || !w.at || !w.size) continue;
            const wx = w.at[0] - (screenModel ? screenModel.x : 0);
            const wy = w.at[1] - (screenModel ? screenModel.y : 0);
            const ww = w.size[0];
            const wh = w.size[1];

            // Window top bounce check
            if (nextX >= wx && nextX <= wx + ww && nextY + r >= wy && nextY - r <= wy + 20 && ball.vy > 0) {
                nextY = wy - r;
                ball.vy = -Math.abs(ball.vy) * restitution;
                ball.triggerVerticalSquash();
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
                ball.triggerCatchSquash();
                burstContainer.triggerBurst(cx, cy);

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
