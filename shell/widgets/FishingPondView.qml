pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Shapes

Item {
    id: pondView
    anchors.fill: parent

    required property real screenWidth
    required property real screenHeight
    required property real pondTop
    required property real pondHeight
    required property string gameState

    property real rodBaseX: 40
    property real rodBaseY: pondTop - 20
    property real rodTipX: 160
    property real rodTipY: pondTop - 80

    property real bobberX: rodTipX
    property real bobberY: rodTipY + 40
    property real bobberWaveOffset: 0

    property bool isAiming: false
    property real aimX: 0
    property real aimY: 0

    signal stalkerArrived()

    // Water Surface / Pond area
    Rectangle {
        id: pondSurface
        x: 0
        y: pondView.pondTop
        width: pondView.screenWidth
        height: pondView.pondHeight
        color: PolyTheme.Theme.withAlpha(Glass.tint(Session.surface, 0.40), 0.82)
        border.width: 1.5
        border.color: Glass.tint(Session.accent, 0.35)

        // Highlight line at surface
        Rectangle {
            anchors.top: parent.top
            anchors.left: parent.left
            anchors.right: parent.right
            height: 3
            color: Glass.tint(Session.accent, 0.65)
        }

        // Ambient waves
        Repeater {
            model: 5
            delegate: Rectangle {
                id: waveLine
                required property int index
                x: ((index * 380) + waveTimer.phase * 50) % pondView.screenWidth
                y: 35 + index * 55
                width: 90 + (index % 3) * 40
                height: 2
                radius: 1
                color: Glass.tint(Session.accent, 0.22)
            }
        }
    }

    Timer {
        id: waveTimer
        interval: 40
        running: pondView.visible
        repeat: true
        property real phase: 0
        onTriggered: {
            phase = (phase + 0.05) % 1000;
            pondView.bobberWaveOffset = Math.sin(phase * 2.5) * 4.5;
        }
    }

    // Swimming fish shadows in pond
    Repeater {
        id: fishShadows
        model: 4
        delegate: Item {
            id: fishItem
            required property int index
            property real fx: 250 + index * 260
            property real fy: pondView.pondTop + 60 + (index % 3) * 65
            property real targetFx: fx
            property real targetFy: fy
            property real heading: 0

            x: fx
            y: fy
            width: 38
            height: 18

            Rectangle {
                anchors.centerIn: parent
                width: 32; height: 12
                radius: 6
                color: PolyTheme.Theme.withAlpha(Session.foreground, 0.22)
                rotation: fishItem.heading

                // Tail fin
                Rectangle {
                    x: -6; y: 2
                    width: 8; height: 8
                    radius: 2
                    color: PolyTheme.Theme.withAlpha(Session.foreground, 0.20)
                    rotation: 45
                }
            }

            Timer {
                interval: 2500 + fishItem.index * 700
                running: pondView.visible && pondView.gameState !== "reeling"
                repeat: true
                onTriggered: {
                    if (pondView.gameState === "waiting" && fishItem.index === 0) {
                        fishItem.targetFx = pondView.bobberX;
                        fishItem.targetFy = pondView.bobberY;
                    } else {
                        fishItem.targetFx = 200 + Math.random() * (pondView.screenWidth - 350);
                        fishItem.targetFy = pondView.pondTop + 40 + Math.random() * (pondView.pondHeight - 80);
                    }
                    fishAnimX.to = fishItem.targetFx;
                    fishAnimY.to = fishItem.targetFy;
                    fishItem.heading = Math.atan2(fishItem.targetFy - fishItem.fy, fishItem.targetFx - fishItem.fx) * 180 / Math.PI;
                    fishAnimX.restart();
                    fishAnimY.restart();
                }
            }

            NumberAnimation on fx {
                id: fishAnimX
                duration: 2200
                easing.type: Easing.InOutQuad
                onFinished: {
                    if (pondView.gameState === "waiting" && fishItem.index === 0) {
                        pondView.stalkerArrived();
                    }
                }
            }
            NumberAnimation on fy {
                id: fishAnimY
                duration: 2200
                easing.type: Easing.InOutQuad
            }
        }
    }

    // Pier Dock on the left
    Rectangle {
        x: 0
        y: pondView.pondTop - 35
        width: 140
        height: 60
        radius: 6
        color: PolyTheme.Theme.withAlpha(Session.surface, 0.92)
        border.width: 1
        border.color: Glass.tint(Session.foreground, 0.20)

        Rectangle { x: 30; y: 0; width: 1; height: 60; color: Glass.tint(Session.foreground, 0.12) }
        Rectangle { x: 70; y: 0; width: 1; height: 60; color: Glass.tint(Session.foreground, 0.12) }
        Rectangle { x: 105; y: 0; width: 1; height: 60; color: Glass.tint(Session.foreground, 0.12) }
    }

    // Fishing Rod
    Shape {
        anchors.fill: parent
        ShapePath {
            strokeColor: PolyTheme.Theme.secondary
            strokeWidth: 3.5
            capStyle: ShapePath.RoundCap
            startX: pondView.rodBaseX
            startY: pondView.rodBaseY
            PathQuad {
                controlX: (pondView.rodBaseX + pondView.rodTipX) / 2
                controlY: pondView.rodTipY - (pondView.gameState === "reeling" ? 25 : 8)
                x: pondView.rodTipX
                y: pondView.rodTipY
            }
        }
    }

    // Cast Trajectory Indicator when dragging/aiming
    Shape {
        anchors.fill: parent
        visible: pondView.isAiming
        ShapePath {
            strokeColor: Session.accent
            strokeWidth: 2
            strokeStyle: ShapePath.DashLine
            dashPattern: [5, 4]
            fillColor: "transparent"
            startX: pondView.rodTipX
            startY: pondView.rodTipY
            PathQuad {
                controlX: (pondView.rodTipX + pondView.aimX) / 2
                controlY: Math.min(pondView.rodTipY, pondView.aimY) - 50
                x: pondView.aimX
                y: pondView.aimY
            }
        }
    }

    // Landing Target Marker
    Rectangle {
        visible: pondView.isAiming
        x: pondView.aimX - width / 2
        y: pondView.aimY - height / 2
        width: 34
        height: 18
        radius: 9
        color: "transparent"
        border.width: 1.5
        border.color: Session.accent
        opacity: 0.85
    }

    // Fishing Line
    Shape {
        anchors.fill: parent
        visible: pondView.gameState !== "idle"
        ShapePath {
            strokeColor: Glass.tint(Session.foreground, 0.65)
            strokeWidth: 1.2
            startX: pondView.rodTipX
            startY: pondView.rodTipY
            PathLine {
                x: pondView.bobberX
                y: pondView.bobberY + (pondView.gameState === "waiting" || pondView.gameState === "nibbling" ? pondView.bobberWaveOffset : 0)
            }
        }
    }

    // Water Splash Ripple Circle
    Rectangle {
        id: splashRipple
        property real rippleX: 0
        property real rippleY: 0
        x: rippleX - width / 2
        y: rippleY - height / 2
        width: 10
        height: 10
        radius: width / 2
        color: "transparent"
        border.width: 2
        border.color: Session.accent
        opacity: 0

        ParallelAnimation {
            id: rippleAnim
            NumberAnimation { target: splashRipple; property: "width"; from: 10; to: 75; duration: 600; easing.type: Easing.OutQuad }
            NumberAnimation { target: splashRipple; property: "height"; from: 10; to: 75; duration: 600; easing.type: Easing.OutQuad }
            NumberAnimation { target: splashRipple; property: "opacity"; from: 0.9; to: 0.0; duration: 600 }
        }

        function trigger(sx: real, sy: real): void {
            rippleX = sx;
            rippleY = sy;
            rippleAnim.restart();
        }
    }

    function triggerSplash(sx: real, sy: real): void {
        splashRipple.trigger(sx, sy);
    }

    // The Fishing Bobber (Phao câu)
    Item {
        id: bobberItem
        x: pondView.bobberX
        y: pondView.bobberY + (pondView.gameState === "waiting" || pondView.gameState === "nibbling" ? pondView.bobberWaveOffset : 0)
        visible: pondView.gameState !== "idle"

        Rectangle {
            anchors.centerIn: parent
            width: 16
            height: 16
            radius: 8
            color: Session.accent
            border.width: 1.5
            border.color: PolyTheme.Theme.secondary

            Rectangle {
                anchors.bottom: parent.top
                anchors.horizontalCenter: parent.horizontalCenter
                width: 2.5
                height: 8
                color: PolyTheme.Theme.secondary
            }
        }
    }

    // Bite Alert Badge ("!")
    Rectangle {
        id: biteAlert
        x: pondView.bobberX - width / 2
        y: pondView.bobberY - 60
        visible: pondView.gameState === "biting"
        width: 38
        height: 38
        radius: 19
        color: PolyTheme.Theme.secondary
        border.width: 2
        border.color: Session.foreground

        Text {
            anchors.centerIn: parent
            text: "!"
            font.family: Session.fontFamily
            font.pixelSize: 24
            font.weight: Font.Black
            color: Session.background
        }

        SequentialAnimation on scale {
            running: biteAlert.visible
            loops: Animation.Infinite
            NumberAnimation { from: 1.0; to: 1.35; duration: 180; easing.type: Easing.OutQuad }
            NumberAnimation { from: 1.35; to: 1.0; duration: 180; easing.type: Easing.InQuad }
        }
    }
}
