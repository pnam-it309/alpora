pragma Singleton
import QtQuick
import ".."
import Quickshell
import Quickshell.Io

Singleton {
    id: root

    property bool active: false
    property string currentGame: "catch"
    property int score: 0
    property int combo: 0
    property int highScore: 0
    property var highScores: ({ "catch": 0 })
    property bool soundFx: true
    property string targetScreen: ""
    property bool loaded: false
    property string error: ""

    // Companion position tracking for catch interaction
    property real companionX: 0
    property real companionY: 0
    property bool companionPresent: false

    // Ball coordinate synchronization
    property real ballX: 0
    property real ballY: 0
    property bool ballMoving: false

    signal petCatch()
    signal scoreAdded(int points, int comboMultiplier)

    function toggle(screen: string): void {
        if (active) {
            close();
        } else {
            open(currentGame, screen);
        }
    }

    function open(game: string, screen: string): void {
        if (game) currentGame = game;
        if (screen) targetScreen = screen;
        score = 0;
        combo = 0;
        highScore = (highScores && highScores[currentGame] !== undefined) ? highScores[currentGame] : 0;
        active = true;
    }

    function close(): void {
        active = false;
        save();
    }

    function addScore(points: int): void {
        combo += 1;
        const multiplier = Math.min(5, Math.max(1, Math.floor(combo / 2) + 1));
        const awarded = points * multiplier;
        score += awarded;
        if (score > highScore) {
            highScore = score;
            const updated = Object.assign({}, highScores);
            updated[currentGame] = highScore;
            highScores = updated;
        }
        root.scoreAdded(awarded, multiplier);
        if (soundFx) {
            AudioFeedback.playTock();
        }
    }

    function dropBall(): void {
        combo = 0;
    }

    function setGame(game: string): void {
        if (currentGame === game) return;
        currentGame = game;
        score = 0;
        combo = 0;
        highScore = (highScores && highScores[game] !== undefined) ? highScores[game] : 0;
    }

    function toggleSound(): void {
        soundFx = !soundFx;
        save();
    }

    function save(): void {
        const payload = {
            version: 1,
            high_scores: highScores,
            sound_fx: soundFx,
            last_game: currentGame
        };
        preferences.setText(JSON.stringify(payload, null, 2));
    }

    FileView {
        id: preferences
        path: (Quickshell.env("XDG_CONFIG_HOME") || Quickshell.env("HOME") + "/.config") + "/poly-shell/arcade.json"
        printErrors: false
        watchChanges: true
        onFileChanged: reload()
        onLoaded: {
            try {
                const saved = JSON.parse(text());
                if (saved.high_scores && typeof saved.high_scores === "object") {
                    root.highScores = saved.high_scores;
                }
                if (typeof saved.sound_fx === "boolean") {
                    root.soundFx = saved.sound_fx;
                }
                if (saved.last_game && typeof saved.last_game === "string") {
                    root.currentGame = saved.last_game;
                }
                root.highScore = (root.highScores && root.highScores[root.currentGame] !== undefined)
                    ? root.highScores[root.currentGame] : 0;
                root.error = "";
            } catch (_) {
                root.error = "Error parsing arcade preferences";
            }
            root.loaded = true;
        }
        onLoadFailed: root.loaded = true
        onSaveFailed: root.error = "Failed to save arcade preferences"
    }

    IpcHandler {
        target: "arcade"
        function status(): string {
            return JSON.stringify({
                active: root.active,
                game: root.currentGame,
                score: root.score,
                combo: root.combo,
                highScore: root.highScore,
                soundFx: root.soundFx,
                targetScreen: root.targetScreen
            });
        }
        function toggle(): void { root.toggle(""); }
        function open(game: string): void { root.open(game, ""); }
        function close(): void { root.close(); }
        function record(game: string, pts: int): void {
            if (pts > (root.highScores[game] || 0)) {
                const updated = Object.assign({}, root.highScores);
                updated[game] = pts;
                root.highScores = updated;
                root.save();
            }
        }
    }
}
