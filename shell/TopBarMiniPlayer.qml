pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import Quickshell
import Quickshell.Io
import "theme" as PolyTheme

Item {
    id: root
    readonly property var player: MusicState.player
    readonly property bool hasMedia: !!player && (player.isPlaying || (player.trackTitle && player.trackTitle.length > 0))
    readonly property bool isPlaying: !!player && player.isPlaying
    readonly property string trackTitle: player && player.trackTitle ? player.trackTitle : ""
    readonly property string trackArtist: player && player.trackArtist ? player.trackArtist : ""
    readonly property string displayTitle: trackTitle.length > 0
        ? (trackTitle + (trackArtist.length > 0 ? " · " + trackArtist : ""))
        : I18n.tr("music.untitled")

    visible: hasMedia
    implicitHeight: 28
    implicitWidth: hasMedia ? Math.min(230, Math.max(88, contentLayout.implicitWidth + 20)) : 0

    Behavior on implicitWidth {
        NumberAnimation {
            duration: Motion.reduced ? 0 : 260
            easing.type: Easing.OutCubic
        }
    }

    Behavior on opacity {
        NumberAnimation {
            duration: Motion.reduced ? 0 : 200
        }
    }
    opacity: hasMedia ? 1 : 0

    property real playbackPulse: 0
    Timer {
        interval: 50
        repeat: true
        running: root.hasMedia && root.isPlaying && !ClockState.sleeping
        onTriggered: root.playbackPulse += 0.08
    }

    Rectangle {
        id: pill
        anchors.fill: parent
        radius: Math.min(14, Session.visual.barRadius)
        color: Glass.tint(Session.surface, mouseArea.containsMouse ? 0.70 : 0.45)
        border.width: Session.visual.barBorder
        border.color: mouseArea.containsMouse ? Glass.tint(Session.accent, 0.42) : Glass.tint(Session.foreground, 0.08)

        Behavior on color { ColorAnimation { duration: Motion.responseMs } }
        Behavior on border.color { ColorAnimation { duration: Motion.responseMs } }

        Row {
            id: contentLayout
            anchors.centerIn: parent
            spacing: 8
            height: parent.height

            // 1. Audio Visualizer Wave (dải sóng âm thanh nhỏ)
            Item {
                id: waveBox
                width: 34
                height: 16
                anchors.verticalCenter: parent.verticalCenter

                MusicWaveform {
                    anchors.fill: parent
                    phase: root.playbackPulse
                    progress: root.isPlaying ? 1.0 : 0.0
                    hasTrack: root.hasMedia
                    playing: root.isPlaying
                    animated: !Motion.reduced
                    playedColor: Session.accent
                    remainingColor: Session.muted
                }
            }

            // 2. Marquee / Scrolling Track Title (tên bài hát chạy chữ)
            Item {
                id: marqueeBox
                width: Math.min(125, Math.max(48, titleText.implicitWidth))
                height: parent.height
                clip: true
                anchors.verticalCenter: parent.verticalCenter

                Text {
                    id: titleText
                    text: root.displayTitle
                    color: Session.foreground
                    font.family: Session.fontFamily
                    font.pixelSize: 11
                    font.weight: Font.Medium
                    anchors.verticalCenter: parent.verticalCenter

                    readonly property real overflow: Math.max(0, implicitWidth - marqueeBox.width)
                    property real scrollOffset: 0
                    x: scrollOffset

                    SequentialAnimation on scrollOffset {
                        id: marqueeAnim
                        running: root.hasMedia && root.isPlaying && titleText.overflow > 0 && !Motion.reduced
                        loops: Animation.Infinite

                        PauseAnimation { duration: 1800 }
                        NumberAnimation {
                            to: -(titleText.overflow + 6)
                            duration: Math.max(1600, titleText.overflow * 38)
                            easing.type: Easing.Linear
                        }
                        PauseAnimation { duration: 1800 }
                        NumberAnimation {
                            to: 0
                            duration: Math.max(1600, titleText.overflow * 38)
                            easing.type: Easing.Linear
                        }
                    }

                    onOverflowChanged: {
                        if (overflow <= 0) scrollOffset = 0;
                    }
                }
            }

            // 3. Mini Play/Pause Indicator
            Item {
                id: playIconBox
                width: 14
                height: 14
                anchors.verticalCenter: parent.verticalCenter
                opacity: mouseArea.containsMouse ? 1 : 0.8
                Behavior on opacity { NumberAnimation { duration: 120 } }

                Icon {
                    anchors.centerIn: parent
                    width: 13
                    height: 13
                    name: root.isPlaying ? "pause-dark" : "play-dark"
                }
            }
        }

        MouseArea {
            id: mouseArea
            anchors.fill: parent
            hoverEnabled: true
            acceptedButtons: Qt.LeftButton | Qt.RightButton | Qt.MiddleButton
            cursorShape: Qt.PointingHandCursor

            Accessible.name: I18n.tr("music.mini_player") + " · " + root.displayTitle

            onClicked: (mouse) => {
                if (mouse.button === Qt.RightButton) {
                    if (root.player && root.player.canGoNext) root.player.next();
                } else if (mouse.button === Qt.MiddleButton) {
                    if (root.player && root.player.canGoPrevious) root.player.previous();
                } else {
                    if (root.player && root.player.canTogglePlaying) root.player.togglePlaying();
                }
            }

            onWheel: (wheel) => {
                if (Session.sink && Session.sink.audio) {
                    const step = wheel.angleDelta.y > 0 ? 0.05 : -0.05;
                    Session.sink.audio.volume = Math.max(0, Math.min(1.5, Session.sink.audio.volume + step));
                }
            }
        }
    }
}
