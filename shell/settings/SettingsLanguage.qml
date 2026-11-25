pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts

ScrollView {
    id: root
    contentWidth: availableWidth
    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AsNeeded

    ColumnLayout {
        width: root.availableWidth
        spacing: 16

        SettingsCard {
            Layout.fillWidth: true
            Text {
                text: I18n.tr("settings.language")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 18
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.language_desc")
                wrapMode: Text.Wrap
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 13
            }
            ColumnLayout {
                Layout.fillWidth: true
                spacing: 8
                Repeater {
                    model: [
                        { code: "vi", label: "Tiếng Việt", sub: "Tiếng Việt (Việt Nam) · Giao diện đầy đủ", badge: "VI" },
                        { code: "en", label: "English", sub: "English (United States) · Complete baseline", badge: "EN" },
                        { code: "es", label: "Español", sub: "Español (España) · Interfaz traducida", badge: "ES" },
                        { code: "ru", label: "Русский", sub: "Русский язык · Полный интерфейс", badge: "RU" }
                    ]
                    Rectangle {
                        id: langTile
                        required property var modelData
                        Layout.fillWidth: true
                        implicitHeight: 64
                        radius: 12
                        readonly property bool isSelected: (Session.settings.locale || "en") === modelData.code
                        color: isSelected ? Glass.tint(Session.accent, 0.22) : (langMouse.containsMouse ? Glass.tint(Session.foreground, 0.08) : Glass.tint(Session.surface, 0.35))
                        border.width: isSelected ? 2 : 1
                        border.color: isSelected ? Session.accent : (langMouse.containsMouse ? Glass.tint(Session.accent, 0.5) : Glass.tint(Session.foreground, 0.15))
                        Behavior on color { ColorAnimation { duration: Motion.responseMs } }
                        Behavior on border.color { ColorAnimation { duration: Motion.responseMs } }

                        MouseArea {
                            id: langMouse
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                Desktop.request("locale", langTile.modelData.code);
                            }
                        }

                        RowLayout {
                            anchors.fill: parent
                            anchors.margins: 14
                            spacing: 14
                            Rectangle {
                                width: 38
                                height: 38
                                radius: 10
                                color: langTile.isSelected ? Session.accent : Glass.tint(Session.surface, 0.6)
                                border.width: 1
                                border.color: langTile.isSelected ? Session.accent : Glass.tint(Session.foreground, 0.2)
                                Text {
                                    anchors.centerIn: parent
                                    text: langTile.modelData.badge
                                    color: langTile.isSelected ? Session.background : Session.foreground
                                    font.family: Session.fontFamily
                                    font.pixelSize: 13
                                    font.weight: Font.Bold
                                }
                            }
                            ColumnLayout {
                                Layout.fillWidth: true
                                spacing: 2
                                Text {
                                    text: langTile.modelData.label
                                    color: Session.foreground
                                    font.family: Session.fontFamily
                                    font.pixelSize: 14
                                    font.weight: langTile.isSelected ? Font.Bold : Font.Medium
                                }
                                Text {
                                    text: langTile.modelData.sub
                                    color: Session.muted
                                    font.family: Session.fontFamily
                                    font.pixelSize: 11
                                }
                            }
                            Rectangle {
                                width: 22
                                height: 22
                                radius: 11
                                visible: langTile.isSelected
                                color: Session.accent
                                Icon {
                                    anchors.centerIn: parent
                                    name: "check"
                                    width: 14
                                    height: 14
                                    color: Session.background
                                }
                            }
                        }
                    }
                }
            }
        }

        SettingsCard {
            Layout.fillWidth: true
            Text {
                text: I18n.tr("settings.language")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 17
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.language_desc")
                wrapMode: Text.Wrap
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 12
            }
            Flow {
                Layout.fillWidth: true
                spacing: 10
                AppearanceButton {
                    text: "Tiếng Việt"
                    symbol: "globe"
                    primary: I18n.locale === "vi"
                    selected: I18n.locale === "vi"
                    onClicked: Desktop.request("locale", "vi")
                }
                AppearanceButton {
                    text: "English (US)"
                    symbol: "globe"
                    primary: I18n.locale === "en"
                    selected: I18n.locale === "en"
                    onClicked: Desktop.request("locale", "en")
                }
                AppearanceButton {
                    text: "Español"
                    symbol: "globe"
                    primary: I18n.locale === "es"
                    selected: I18n.locale === "es"
                    onClicked: Desktop.request("locale", "es")
                }
                AppearanceButton {
                    text: "Русский"
                    symbol: "globe"
                    primary: I18n.locale === "ru"
                    selected: I18n.locale === "ru"
                    onClicked: Desktop.request("locale", "ru")
                }
            }
        }

        SettingsCard {
            Layout.fillWidth: true
            Text {
                text: I18n.tr("settings.input_method")
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 15
                font.weight: Font.DemiBold
            }
            Text {
                Layout.fillWidth: true
                text: I18n.tr("settings.input_method_desc")
                wrapMode: Text.Wrap
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 12
            }
            TextField {
                Layout.fillWidth: true
                placeholderText: I18n.tr("settings.input_test_placeholder")
                color: Session.foreground
                placeholderTextColor: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 13
                background: Rectangle {
                    radius: 8
                    color: Glass.tint(Session.surface, 0.40)
                    border.width: 1
                    border.color: parent.activeFocus ? Session.accent : Glass.tint(Session.foreground, 0.20)
                }
            }
        }
    }
}
