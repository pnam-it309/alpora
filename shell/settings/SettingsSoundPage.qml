pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

SettingsCard {
    Layout.fillWidth: true
    Text {
        text: I18n.tr("settings.sound_output")
        color: PolyTheme.Theme.color("#eff1f4")
        font.family: Session.fontFamily
        font.pixelSize: 17
    }
    RowLayout {
        Layout.fillWidth: true
        IconButton {
            symbol: Session.audio && Session.audio.muted ? "muted" : "volume"
            hint: I18n.tr("settings.toggle_sound")
            enabled: !!Session.audio
            onClicked: Session.audio.muted = !Session.audio.muted
        }
        ControlSlider {
            Layout.fillWidth: true
            wheelEnabled: false
            enabled: !!Session.audio
            value: Session.audio ? Session.audio.volume : 0
            Accessible.name: I18n.tr("osd.volume")
            onMoved: if (Session.audio)
                Session.audio.volume = value
        }
    }
    Repeater {
        model: Session.outputs
        SettingsRow {
            required property var modelData
            Layout.fillWidth: true
            text: modelData.nickname || modelData.description || modelData.name
            symbol: "volume"
            selected: modelData === Session.sink
            enabled: modelData.ready
            onClicked: Session.selectOutput(modelData)
        }
    }
    Text {
        text: I18n.tr("settings.microphone")
        color: PolyTheme.Theme.color("#eff1f4")
        font.family: Session.fontFamily
        font.pixelSize: 17
    }
    RowLayout {
        Layout.fillWidth: true
        IconButton {
            symbol: Session.microphone && Session.microphone.muted ? "microphone-muted" : "microphone"
            hint: I18n.tr("settings.toggle_mic")
            enabled: !!Session.microphone
            onClicked: Session.microphone.muted = !Session.microphone.muted
        }
        ControlSlider {
            Layout.fillWidth: true
            wheelEnabled: false
            enabled: !!Session.microphone
            value: Session.microphone ? Session.microphone.volume : 0
            Accessible.name: I18n.tr("settings.mic_volume")
            onMoved: if (Session.microphone)
                Session.microphone.volume = value
        }
    }
    Repeater {
        model: Session.inputs
        SettingsRow {
            required property var modelData
            Layout.fillWidth: true
            text: modelData.nickname || modelData.description || modelData.name
            symbol: "microphone"
            selected: modelData === Session.source
            enabled: modelData.ready
            onClicked: Session.selectInput(modelData)
        }
    }
}
