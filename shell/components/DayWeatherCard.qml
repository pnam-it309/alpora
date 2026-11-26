pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Layouts

// Open-Meteo summary for the calendar: current conditions plus a 7-day outlook
// whose tiles select the matching date in the calendar.
Rectangle {
    id: root
    property date selectedDate: ClockState.date
    signal daySelected(date day)
    readonly property var current: WeatherState.current
    readonly property var outlook: current ? (WeatherState.data.outlook || WeatherState.data.forecast || []) : []
    readonly property string selectedKey: Qt.formatDateTime(selectedDate, "yyyy-MM-dd")
    radius: 13
    color: Glass.tint(PolyTheme.Theme.color("#222a2c"), 0.4)
    border.width: 0.7; border.color: PolyTheme.Theme.color("#36423c")
    implicitHeight: 64
    Component.onCompleted: if (!WeatherState.current && !WeatherState.busy) WeatherState.refresh()

    RowLayout {
        anchors.fill: parent; anchors.margins: 8; spacing: 10
        WeatherGlyph {
            Layout.preferredWidth: 46; Layout.preferredHeight: 46
            code: root.current ? root.current.weather_code : 0
            day: root.current ? !!root.current.is_day : true
        }
        ColumnLayout {
            Layout.preferredWidth: 120; spacing: 0
            Text {
                text: root.current ? Math.round(root.current.temperature_2m) + "°" : "--"
                color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 22
            }
            Text {
                Layout.fillWidth: true; elide: Text.ElideRight
                text: root.current ? WeatherState.label(root.current.weather_code)
                      : WeatherState.busy ? I18n.tr("weather.loading") : (WeatherState.error || I18n.tr("weather.no_data"))
                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11
            }
            Text {
                Layout.fillWidth: true; elide: Text.ElideRight; visible: !!root.current && root.current.relative_humidity_2m !== undefined
                text: root.current && root.current.relative_humidity_2m !== undefined
                      ? I18n.tr("weather.humidity") + " " + Math.round(root.current.relative_humidity_2m) + "%" : ""
                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10
            }
        }
        Row {
            Layout.fillWidth: true; Layout.fillHeight: true; spacing: 5
            Repeater {
                model: root.outlook
                Rectangle {
                    id: tile
                    required property var modelData
                    readonly property bool chosen: modelData.day === root.selectedKey
                    width: Math.max(44, (parent.width - 5 * (root.outlook.length - 1)) / Math.max(1, root.outlook.length))
                    height: parent.height; radius: 10
                    color: chosen ? Qt.rgba(Session.accent.r, Session.accent.g, Session.accent.b, 0.22)
                           : (hit.containsMouse ? PolyTheme.Theme.color("#3b4840") : PolyTheme.Theme.color("#2b3534"))
                    border.width: chosen ? 1 : 0.7; border.color: chosen ? Session.accent : PolyTheme.Theme.color("#3c4941")
                    Behavior on color { ColorAnimation { duration: Session.settings.reducedMotion ? 0 : 140 } }
                    Accessible.role: Accessible.Button
                    Accessible.name: WeatherState.day(modelData.day) + ": " + WeatherState.label(modelData.code) + ", " + Math.round(modelData.high) + " / " + Math.round(modelData.low)
                    Column {
                        anchors.centerIn: parent; spacing: 1
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: WeatherState.day(tile.modelData.day); color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10 }
                        Text { anchors.horizontalCenter: parent.horizontalCenter; text: Math.round(tile.modelData.high) + "° / " + Math.round(tile.modelData.low) + "°"; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 11 }
                        Text {
                            anchors.horizontalCenter: parent.horizontalCenter
                            visible: tile.modelData.rain !== undefined && tile.modelData.rain !== null
                            text: Math.round(tile.modelData.rain || 0) + "%"; color: Session.accent; font.family: Session.fontFamily; font.pixelSize: 9
                        }
                    }
                    MouseArea {
                        id: hit; anchors.fill: parent; hoverEnabled: true; cursorShape: Qt.PointingHandCursor
                        onClicked: root.daySelected(new Date(tile.modelData.day + "T12:00:00"))
                    }
                }
            }
        }
        IconButton {
            symbol: "refresh"; Layout.preferredWidth: 27; Layout.preferredHeight: 27
            hint: WeatherState.error ? WeatherState.error : I18n.tr("weather.refresh_open_meteo")
            enabled: !WeatherState.busy; onClicked: WeatherState.refresh()
        }
    }
}
