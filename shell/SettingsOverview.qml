pragma ComponentBehavior: Bound
import QtQuick
import "theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    signal navigate(string page)
    property var monitors: []
    property url wallpaper: "file://" + Quickshell.env("POLY_SHELL_ASSETS") + "/wallpapers/alpine-dawn.png"
    readonly property string powerLabel: ({"power-saver": "Энергосбережение", balanced: "Сбалансированный режим", performance: "Производительность"})[Desktop.data.powerProfile] || "Профили недоступны"
    spacing: 12
    RowLayout {
        Layout.fillWidth: true; Layout.preferredHeight: 65; spacing: 12
        SettingsTile { Layout.fillWidth: true; Layout.fillHeight: true; padding: 12; title: Session.mode === "vibe" ? "Vibe" : "Work"; subtitle: "Текущий режим"; symbol: "monitor"; tint: PolyTheme.Theme.color("#edb493"); onClicked: root.navigate("modes") }
        SettingsTile { Layout.fillWidth: true; Layout.fillHeight: true; padding: 12; title: PolyTheme.Theme.label; subtitle: "Тема оформления"; symbol: "gem"; onClicked: root.navigate("appearance") }
    }
    RowLayout {
        Layout.fillWidth: true; Layout.preferredHeight: 99; spacing: 12
        SettingsTile {
            Layout.fillWidth: true; Layout.fillHeight: true
            title: "Wi-Fi"; symbol: "wifi"
            subtitle: Session.wifiNetwork ? Session.wifiNetwork.name : Session.wifiEnabled ? "Нет подключения" : "Выключен"
            detail: Session.wifiNetwork ? "●  Подключено" : ""
            showToggle: true; toggled: Session.wifiEnabled; toggleAvailable: !!Session.wifiDevice
            onClicked: root.navigate("wifi"); onToggleRequested: Session.toggleWifi()
        }
        SettingsTile {
            Layout.fillWidth: true; Layout.fillHeight: true
            title: "Bluetooth"; symbol: "bluetooth"; tint: PolyTheme.Theme.color("#9cc8df")
            subtitle: Session.bluetoothEnabled ? "Включён" : "Выключен"
            detail: Session.bluetoothAdapter ? "Подключено: " + Session.bluetoothAdapter.devices.values.filter(d => d.connected).length : "Адаптер не найден"
            showToggle: true; toggled: Session.bluetoothEnabled; toggleAvailable: !!Session.bluetoothAdapter && !Desktop.changingSettings
            onClicked: root.navigate("bluetooth"); onToggleRequested: Session.toggleBluetooth()
        }
    }
    RowLayout {
        Layout.fillWidth: true; Layout.preferredHeight: 146; spacing: 12
        SettingsCard {
            Layout.fillWidth: true; Layout.fillHeight: true
            TapHandler { onTapped: root.navigate("monitors") }
            HoverHandler { cursorShape: Qt.PointingHandCursor }
            RowLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 15
                SettingsBadge { symbol: "monitor"; Layout.alignment: Qt.AlignTop }
                ColumnLayout {
                    Layout.fillWidth: true; spacing: 5
                    Text { text: "Мониторы"; color: PolyTheme.Theme.color("#eff1f5"); font.family: Session.fontFamily; font.pixelSize: 15; font.weight: Font.DemiBold }
                    Row {
                        spacing: 7
                        Repeater {
                            model: root.monitors
                            Rectangle {
                                required property var modelData
                                width: 88; height: 46; radius: 5; color: PolyTheme.Theme.color("#4e575d"); border.color: PolyTheme.Theme.color("#909b9a"); border.width: 1
                                Image { anchors.fill: parent; anchors.margins: 3; source: root.wallpaper; fillMode: Image.PreserveAspectCrop; sourceSize: Qt.size(176, 92) }
                            }
                        }
                    }
                    Text { Layout.fillWidth: true; text: root.monitors.length ? root.monitors[0].description : "Нет подключённых экранов"; color: PolyTheme.Theme.color("#ccd0d5"); font.family: Session.fontFamily; font.pixelSize: 11; elide: Text.ElideRight }
                    Text { text: root.monitors.length ? root.monitors[0].width + " × " + root.monitors[0].height + " · " + Math.round(root.monitors[0].refreshRate) + " Гц" : ""; color: PolyTheme.Theme.color("#b9c0cb"); font.family: Session.fontFamily; font.pixelSize: 11 }
                }
                Icon { name: "chevron-right"; Layout.preferredWidth: 17; Layout.preferredHeight: 17 }
            }
        }
        SettingsCard {
            Layout.fillWidth: true; Layout.fillHeight: true
            RowLayout {
                Layout.fillWidth: true; Layout.fillHeight: true; spacing: 15
                SettingsBadge { symbol: "volume"; tint: PolyTheme.Theme.color("#edb493"); Layout.alignment: Qt.AlignTop }
                ColumnLayout {
                    Layout.fillWidth: true; Layout.fillHeight: true; spacing: 6
                    RowLayout {
                        Layout.fillWidth: true
                        Text { Layout.fillWidth: true; text: "Звук"; color: PolyTheme.Theme.color("#eff1f5"); font.family: Session.fontFamily; font.pixelSize: 15; font.weight: Font.DemiBold }
                        ToolButton { Accessible.name: "Открыть настройки звука"; implicitWidth: 24; implicitHeight: 24; background: Item {} contentItem: Icon { name: "chevron-right" } onClicked: root.navigate("sound") }
                    }
                    Text { Layout.fillWidth: true; text: Session.sink ? (Session.sink.nickname || Session.sink.description || "Динамики") : "Нет устройства вывода"; color: PolyTheme.Theme.color("#c3c8d0"); font.family: Session.fontFamily; font.pixelSize: 11; elide: Text.ElideRight }
                    Item { Layout.fillHeight: true }
                    RowLayout {
                        Layout.fillWidth: true; spacing: 15
                        ControlSlider { Layout.fillWidth: true; accent: PolyTheme.Theme.color("#bcd5a7"); value: Session.audio ? Session.audio.volume : 0; enabled: !!Session.audio; Accessible.name: "Громкость динамиков"; onMoved: if (Session.audio) Session.audio.volume = value }
                        Text { text: Session.audio ? Math.round(Session.audio.volume * 100) + "%" : "—"; color: PolyTheme.Theme.color("#edf1f4"); font.family: Session.fontFamily; font.pixelSize: 13 }
                    }
                    Item { Layout.fillHeight: true }
                }
            }
        }
    }
    SettingsCard {
        Layout.fillWidth: true; Layout.fillHeight: true; Layout.minimumHeight: 168
        RowLayout {
            Layout.fillWidth: true; spacing: 12
            Icon { name: "wallpaper"; Layout.preferredWidth: 22; Layout.preferredHeight: 22 }
            Text { Layout.fillWidth: true; text: "Рабочий стол"; color: PolyTheme.Theme.color("#eff1f5"); font.family: Session.fontFamily; font.pixelSize: 15; font.weight: Font.DemiBold }
            ToolButton { Accessible.name: "Открыть обои"; implicitWidth: 22; implicitHeight: 22; background: Item {} contentItem: Icon { name: "chevron-right" } onClicked: root.navigate("wallpaper") }
        }
        RowLayout {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 20
            Rectangle {
                Layout.preferredWidth: 290; Layout.fillHeight: true; Layout.minimumHeight: 91
                radius: 11; color: PolyTheme.Theme.color("#3b4145"); clip: true
                SettingsImage { anchors.fill: parent; source: root.wallpaper; sourceSize: Qt.size(580, 240) }
                TapHandler { onTapped: root.navigate("wallpaper") }
                HoverHandler { cursorShape: Qt.PointingHandCursor }
            }
            ColumnLayout {
                Layout.fillWidth: true; spacing: 8
                Text { text: PolyTheme.Theme.label; color: PolyTheme.Theme.color("#eff1f5"); font.family: Session.fontFamily; font.pixelSize: 16; font.weight: Font.DemiBold }
                Text { text: "Обои, цвета и оформление"; color: PolyTheme.Theme.color("#c0c5ce"); font.family: Session.fontFamily; font.pixelSize: 12 }
                Item { Layout.fillHeight: true }
                RowLayout {
                    Layout.fillWidth: true; spacing: 10
                    AppearanceButton { Layout.fillWidth: true; text: "Сменить обои"; symbol: "wallpaper"; onClicked: root.navigate("wallpaper") }
                    AppearanceButton { Layout.fillWidth: true; text: "Внешний вид"; symbol: "palette"; onClicked: root.navigate("appearance") }
                }
            }
        }
    }
    RowLayout {
        Layout.fillWidth: true; Layout.preferredHeight: 78; spacing: 12
        SettingsTile { Layout.fillWidth: true; Layout.fillHeight: true; padding: 12; title: "Питание"; subtitle: root.powerLabel; symbol: "battery"; onClicked: root.navigate("power") }
        SettingsTile { Layout.fillWidth: true; Layout.fillHeight: true; padding: 12; title: "Уведомления"; subtitle: Desktop.data.dnd ? "Не беспокоить" : "Приложения и поведение"; symbol: "bell"; tint: PolyTheme.Theme.color("#edb493"); onClicked: root.navigate("notifications") }
        SettingsTile { Layout.fillWidth: true; Layout.fillHeight: true; padding: 12; title: "Устройства"; subtitle: "Подключения и периферия"; symbol: "devices"; tint: PolyTheme.Theme.color("#9cc8df"); onClicked: root.navigate("devices") }
    }
}
