pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme

Item {
    id: fishingGame
    anchors.fill: parent

    required property var screenModel
    readonly property real screenWidth: screenModel ? screenModel.width : 1920
    readonly property real screenHeight: screenModel ? screenModel.height : 1080

    // Game state: "idle" | "casting" | "waiting" | "nibbling" | "biting" | "reeling" | "caught"
    property string gameState: "idle"

    readonly property real pondTop: screenHeight * 0.52
    readonly property real pondHeight: screenHeight - pondTop

    // Rod & line coordinates
    readonly property real rodTipX: 160
    property real rodTipY: pondTop - 80

    // Bobber position
    property real bobberX: rodTipX
    property real bobberY: rodTipY + 40
    property real bobberTargetX: 400
    property real bobberTargetY: pondTop + 120

    // Cast aiming coordinates
    property bool isAiming: false
    property real aimX: 400
    property real aimY: pondTop + 120

    // Reeling mechanics
    property real tension: 50.0
    property real reelProgress: 0.0
    readonly property real sweetSpotMin: 35.0
    readonly property real sweetSpotMax: 68.0
    property bool isReelingInput: false
    property real fishStruggleAngle: 0

    // Caught fish details
    property var currentFish: null

    onVisibleChanged: {
        if (!visible) {
            fishingGame.isAiming = false;
            fishingGame.resetToIdle();
        }
    }

    Connections {
        target: ArcadeState
        function onBlitzEnded(): void {
            fishingGame.isAiming = false;
            fishingGame.resetToIdle();
        }
    }

    // Pond Scene Presentation
    FishingPondView {
        id: pondView
        screenWidth: fishingGame.screenWidth
        screenHeight: fishingGame.screenHeight
        pondTop: fishingGame.pondTop
        pondHeight: fishingGame.pondHeight
        gameState: fishingGame.gameState
        rodTipX: fishingGame.rodTipX
        rodTipY: fishingGame.rodTipY
        bobberX: fishingGame.bobberX
        bobberY: fishingGame.bobberY
        isAiming: fishingGame.isAiming
        aimX: fishingGame.aimX
        aimY: fishingGame.aimY
        onStalkerArrived: fishingGame.startNibbling()
    }

    // Background input catcher
    MouseArea {
        id: pondInput
        anchors.fill: parent
        hoverEnabled: true

        onPressed: function(mouse) {
            if (fishingGame.gameState === "idle") {
                fishingGame.isAiming = true;
                fishingGame.aimX = Math.max(220, Math.min(fishingGame.screenWidth - 100, mouse.x));
                fishingGame.aimY = Math.max(fishingGame.pondTop + 40, Math.min(fishingGame.screenHeight - 60, mouse.y));
            } else if (fishingGame.gameState === "biting") {
                fishingGame.startReeling();
            } else if (fishingGame.gameState === "reeling") {
                fishingGame.isReelingInput = true;
            } else if (fishingGame.gameState === "caught") {
                fishingGame.resetToIdle();
            }
        }

        onPositionChanged: function(mouse) {
            if (fishingGame.gameState === "idle" && fishingGame.isAiming) {
                fishingGame.aimX = Math.max(220, Math.min(fishingGame.screenWidth - 100, mouse.x));
                fishingGame.aimY = Math.max(fishingGame.pondTop + 40, Math.min(fishingGame.screenHeight - 60, mouse.y));
            }
        }

        onReleased: function(mouse) {
            if (fishingGame.gameState === "idle" && fishingGame.isAiming) {
                fishingGame.isAiming = false;
                const clampedX = Math.max(220, Math.min(fishingGame.screenWidth - 100, mouse.x));
                const clampedY = Math.max(fishingGame.pondTop + 40, Math.min(fishingGame.screenHeight - 60, mouse.y));
                fishingGame.castLine(clampedX, clampedY);
            } else if (fishingGame.gameState === "reeling") {
                fishingGame.isReelingInput = false;
            }
        }
    }

    // Reeling Tension Gauge Card
    Rectangle {
        id: reelHUD
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.top: parent.top
        anchors.topMargin: Session.visual.barTop + Session.visual.barHeight + 68
        width: 320
        height: 120
        radius: 18
        visible: fishingGame.gameState === "reeling"
        color: PolyTheme.Theme.withAlpha(Session.surface, 0.92)
        border.width: 1.5
        border.color: Glass.tint(Session.accent, 0.45)

        Column {
            anchors.centerIn: parent
            spacing: 8
            width: parent.width - 32

            Text {
                text: I18n.tr("arcade.fishing_reel_hint")
                font.family: Session.fontFamily
                font.pixelSize: 11
                font.weight: Font.DemiBold
                color: Session.foreground
                anchors.horizontalCenter: parent.horizontalCenter
            }

            Item {
                width: parent.width
                height: 22

                Rectangle {
                    anchors.fill: parent; radius: 11
                    color: Glass.tint(Session.surface, 0.6); border.width: 1; border.color: Glass.tint(Session.foreground, 0.15)
                }

                Rectangle {
                    x: (parent.width * fishingGame.sweetSpotMin / 100)
                    width: (parent.width * (fishingGame.sweetSpotMax - fishingGame.sweetSpotMin) / 100)
                    height: parent.height; radius: 11
                    color: Glass.tint(Session.accent, 0.40); border.width: 1; border.color: Session.accent
                }

                Rectangle {
                    x: Math.max(0, Math.min(parent.width - width, (parent.width * fishingGame.tension / 100) - width / 2))
                    anchors.verticalCenter: parent.verticalCenter
                    width: 14; height: 26; radius: 7
                    color: (fishingGame.tension >= fishingGame.sweetSpotMin && fishingGame.tension <= fishingGame.sweetSpotMax) ? PolyTheme.Theme.secondary : Session.foreground
                    border.width: 1.5; border.color: Session.background
                }
            }

            Row {
                spacing: 8; anchors.horizontalCenter: parent.horizontalCenter; width: parent.width
                Icon { name: "trophy"; width: 14; height: 14; anchors.verticalCenter: parent.verticalCenter }
                Rectangle {
                    width: parent.width - 24; height: 8; radius: 4
                    color: Glass.tint(Session.surface, 0.6); anchors.verticalCenter: parent.verticalCenter
                    Rectangle { height: parent.height; width: parent.width * (fishingGame.reelProgress / 100); radius: 4; color: Session.accent }
                }
            }
        }
    }

    Timer { id: reelTimer; interval: 32; running: fishingGame.gameState === "reeling"; repeat: true; onTriggered: fishingGame.stepReelPhysics() }
    Timer {
        id: biteWindowTimer; interval: 2800; running: false; repeat: false
        onTriggered: if (fishingGame.gameState === "biting") { pondView.triggerSplash(fishingGame.bobberX, fishingGame.bobberY); fishingGame.resetToIdle(); }
    }
    Timer { id: waitTimer; interval: 2400; running: false; repeat: false; onTriggered: if (fishingGame.gameState === "waiting") fishingGame.startNibbling(); }
    Timer { id: nibbleTimer; interval: 1400; running: false; repeat: false; onTriggered: if (fishingGame.gameState === "nibbling") fishingGame.startBiting(); }

    // Catch Celebration Dialog / Banner
    Rectangle {
        id: catchBanner
        anchors.centerIn: parent
        width: 380
        height: 210
        radius: 20
        visible: fishingGame.gameState === "caught" && fishingGame.currentFish !== null
        color: PolyTheme.Theme.withAlpha(Session.surface, 0.94)
        border.width: 2
        border.color: Session.accent

        Column {
            anchors.centerIn: parent
            spacing: 10
            width: parent.width - 40

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: "★ " + (fishingGame.currentFish ? I18n.tr(fishingGame.currentFish.nameKey) : "") + " ★"
                font.family: Session.fontFamily
                font.pixelSize: 18
                font.weight: Font.Bold
                color: Session.accent
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: fishingGame.currentFish ? I18n.trWith("arcade.fish_specs", {
                    weight: fishingGame.currentFish.weight,
                    length: fishingGame.currentFish.length
                }) : ""
                font.family: Session.fontFamily
                font.pixelSize: 14
                font.weight: Font.Medium
                color: Session.foreground
            }

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                width: scorePillText.implicitWidth + 24
                height: 28
                radius: 14
                color: Glass.tint(Session.accent, 0.3)
                border.width: 1
                border.color: Session.accent

                Text {
                    id: scorePillText
                    anchors.centerIn: parent
                    text: "+" + (fishingGame.currentFish ? (fishingGame.currentFish.awardedPoints || fishingGame.currentFish.points) : 0) + " PTS"
                        + ((fishingGame.currentFish && fishingGame.currentFish.multiplier > 1) ? (" (x" + fishingGame.currentFish.multiplier + ")") : "")
                    font.family: Session.fontFamily
                    font.pixelSize: 13
                    font.weight: Font.Bold
                    color: Session.foreground
                }
            }

            Text {
                anchors.horizontalCenter: parent.horizontalCenter
                text: I18n.tr("arcade.fish_again")
                font.family: Session.fontFamily
                font.pixelSize: 11
                color: Glass.tint(Session.foreground, 0.65)
            }
        }
    }

    // Star Burst particle system on successful catch
    Item {
        id: fishingBurst
        anchors.fill: parent

        function triggerBurst(cx: real, cy: real): void {
            fishBurstProgress.val = 0.0;
            fishBurstOrigin.x = cx;
            fishBurstOrigin.y = cy;
            fishBurstAnim.restart();
        }

        QtObject { id: fishBurstOrigin; property real x: 0; property real y: 0 }
        QtObject { id: fishBurstProgress; property real val: 0.0 }

        NumberAnimation {
            id: fishBurstAnim
            target: fishBurstProgress
            property: "val"
            from: 0.0; to: 1.0; duration: 700
            easing.type: Easing.OutCubic
        }

        Repeater {
            model: 14
            delegate: Rectangle {
                id: fParticle
                required property int index
                readonly property real angle: (index * (360 / 14)) * Math.PI / 180
                readonly property real dist: fishBurstProgress.val * (55 + (index % 3) * 25)
                x: fishBurstOrigin.x + Math.cos(angle) * dist - width / 2
                y: fishBurstOrigin.y + Math.sin(angle) * dist - height / 2
                width: Math.max(0, (1.0 - fishBurstProgress.val) * (index % 2 === 0 ? 12 : 8))
                height: width
                radius: index % 2 === 0 ? 2 : width / 2
                rotation: fishBurstProgress.val * 270
                color: index % 2 === 0 ? Session.accent : PolyTheme.Theme.secondary
                opacity: 1.0 - fishBurstProgress.val
                visible: fishBurstAnim.running
            }
        }
    }

    // Bottom hint card
    Rectangle {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 24
        width: bottomHintText.implicitWidth + 28
        height: 30
        radius: 15
        color: PolyTheme.Theme.withAlpha(Session.surface, 0.82)

        Text {
            id: bottomHintText
            anchors.centerIn: parent
            text: {
                if (fishingGame.gameState === "idle") return I18n.tr("arcade.fishing_cast_hint");
                if (fishingGame.gameState === "waiting") return I18n.tr("arcade.fishing_wait_hint");
                if (fishingGame.gameState === "biting") return I18n.tr("arcade.fishing_bite_hint");
                if (fishingGame.gameState === "reeling") return I18n.tr("arcade.fishing_reel_hint");
                if (fishingGame.gameState === "caught") return I18n.tr("arcade.fish_again");
                return "";
            }
            font.family: Session.fontFamily
            font.pixelSize: 11
            color: Glass.tint(Session.foreground, 0.8)
        }
    }

    function castLine(tx: real, ty: real): void {
        gameState = "casting";
        bobberTargetX = tx;
        bobberTargetY = ty;

        castXAnim.from = rodTipX;
        castXAnim.to = tx;
        castYAnim.from = rodTipY;
        castYAnim.to = ty;
        castXAnim.restart();
        castYAnim.restart();
    }

    NumberAnimation on bobberX {
        id: castXAnim
        duration: 750
        easing.type: Easing.OutQuad
    }

    NumberAnimation on bobberY {
        id: castYAnim
        duration: 750
        easing.type: Easing.OutBounce
        onFinished: {
            if (fishingGame.gameState === "casting") {
                pondView.triggerSplash(fishingGame.bobberX, fishingGame.bobberY);
                if (ArcadeState.soundFx) AudioFeedback.playTock();
                fishingGame.gameState = "waiting";
                waitTimer.restart();
            }
        }
    }

    function startNibbling(): void {
        if (gameState !== "waiting") return;
        waitTimer.stop();
        gameState = "nibbling";
        if (ArcadeState.soundFx) AudioFeedback.playTock();
        nibbleTimer.restart();
    }

    function startBiting(): void {
        if (gameState !== "nibbling") return;
        gameState = "biting";
        pondView.triggerSplash(bobberX, bobberY);
        if (ArcadeState.soundFx) AudioFeedback.playTock();
        biteWindowTimer.restart();
    }

    function startReeling(): void {
        biteWindowTimer.stop();
        gameState = "reeling";
        tension = 50.0;
        reelProgress = 30.0;
        isReelingInput = true;
    }

    function fishEscaped(): void {
        reelTimer.stop();
        pondView.triggerSplash(bobberX, bobberY);
        resetToIdle();
    }

    function stepReelPhysics(): void {
        tension = isReelingInput ? Math.min(100.0, tension + 2.8) : Math.max(0.0, tension - 1.4);
        fishStruggleAngle += 0.18;
        tension = Math.max(0.0, Math.min(100.0, tension + Math.sin(fishStruggleAngle) * 1.2));

        if (tension >= sweetSpotMin && tension <= sweetSpotMax) {
            reelProgress += 1.3;
            if (reelProgress >= 100.0) {
                reelProgress = 100.0;
                successfulCatch();
            }
        } else {
            reelProgress -= 0.5;
            if (tension > 95.0 || tension < 10.0) reelProgress -= 0.7;
            if (reelProgress <= 0.0) fishEscaped();
        }
    }

    function successfulCatch(): void {
        reelTimer.stop();
        gameState = "caught";

        const r = Math.random();
        const speciesList = [
            { maxR: 0.40, nameKey: "arcade.fish_ro", wMin: 0.18, wSpan: 0.30, lMin: 14, lSpan: 11, pMin: 70, pSpan: 40 },
            { maxR: 0.75, nameKey: "arcade.fish_chep", wMin: 1.5, wSpan: 3.2, lMin: 32, lSpan: 26, pMin: 200, pSpan: 120 },
            { maxR: 0.93, nameKey: "arcade.fish_hoi", wMin: 4.0, wSpan: 4.2, lMin: 56, lSpan: 24, pMin: 480, pSpan: 240 },
            { maxR: 1.00, nameKey: "arcade.fish_than_thoai", wMin: 14.0, wSpan: 10.0, lMin: 98, lSpan: 38, pMin: 1600, pSpan: 800 }
        ];
        const s = speciesList.find(x => r < x.maxR) || speciesList[0];
        const curCombo = ArcadeState.combo;
        const multiplier = Math.min(5, Math.max(1, Math.floor((curCombo + 1) / 2) + 1));
        const pts = Math.floor(s.pMin + Math.random() * s.pSpan);
        const species = {
            nameKey: s.nameKey,
            weight: Number(s.wMin + Math.random() * s.wSpan).toFixed(2),
            length: Math.floor(s.lMin + Math.random() * s.lSpan),
            points: pts,
            awardedPoints: pts * multiplier,
            multiplier: multiplier
        };

        currentFish = species;
        fishingBurst.triggerBurst(fishingGame.screenWidth / 2, fishingGame.screenHeight / 2);
        ArcadeState.addFishCatch(I18n.tr(species.nameKey), parseFloat(species.weight), species.length, species.points);
    }

    function resetToIdle(): void {
        isAiming = false;
        waitTimer.stop();
        nibbleTimer.stop();
        biteWindowTimer.stop();
        reelTimer.stop();
        gameState = "idle";
        bobberX = rodTipX;
        bobberY = rodTipY + 40;
        currentFish = null;
        tension = 50.0;
        reelProgress = 0.0;
        isReelingInput = false;
    }
}
