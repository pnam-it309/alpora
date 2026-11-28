pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as PolyTheme

ScrollView {
    id: root
    property string activeCategory: ""
    property bool allApps: false
    signal categorySelected(string categoryId)
    signal allAppsSelected()

    ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff
    clip: true
    contentHeight: availableHeight

    RowLayout {
        spacing: 6
        height: root.availableHeight

        Button {
            id: allBtn
            Layout.preferredHeight: 26
            padding: 8
            hoverEnabled: true
            background: Rectangle {
                radius: 13
                color: (root.allApps && !root.activeCategory) ? Session.accent : (allBtn.hovered ? PolyTheme.Theme.color("#3b4640") : PolyTheme.Theme.color("#252e2a"))
                border.width: (root.allApps && !root.activeCategory) ? 0 : 0.8
                border.color: PolyTheme.Theme.color("#3c4941")
            }
            contentItem: Text {
                text: I18n.tr("common.all")
                color: (root.allApps && !root.activeCategory) ? PolyTheme.Theme.color("#1a221d") : Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 11
                font.weight: (root.allApps && !root.activeCategory) ? Font.DemiBold : Font.Normal
            }
            onClicked: root.allAppsSelected()
        }

        Repeater {
            model: AppCatalog.categories
            Button {
                id: pill
                required property var modelData
                readonly property bool active: root.activeCategory === modelData.id
                Layout.preferredHeight: 26
                padding: 8
                hoverEnabled: true
                background: Rectangle {
                    radius: 13
                    color: pill.active ? Session.accent : (pill.hovered ? PolyTheme.Theme.color("#3b4640") : PolyTheme.Theme.color("#252e2a"))
                    border.width: pill.active ? 0 : 0.8
                    border.color: PolyTheme.Theme.color("#3c4941")
                }
                contentItem: RowLayout {
                    spacing: 4
                    Icon {
                        Layout.preferredWidth: 12
                        Layout.preferredHeight: 12
                        name: pill.modelData.icon
                    }
                    Text {
                        text: pill.modelData.name
                        color: pill.active ? PolyTheme.Theme.color("#1a221d") : Session.foreground
                        font.family: Session.fontFamily
                        font.pixelSize: 11
                        font.weight: pill.active ? Font.DemiBold : Font.Normal
                    }
                }
                onClicked: root.categorySelected(pill.modelData.id)
            }
        }
    }
}
