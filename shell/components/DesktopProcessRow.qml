pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Controls
import QtQuick.Layouts
import "../theme" as PolyTheme

Rectangle {
    id: root
    required property var modelData
    required property var widgetRoot
    required property real listWidth

    x: modelData.appName ? Math.min(Number(modelData.depth || 0) * 10, 28) : 0
    width: listWidth - x
    height: processBody.implicitHeight + 14
    radius: 8
    color: Glass.tint(Session.surface, 0.68)
    border.width: 1
    border.color: Glass.tint(Session.accent, 0.12)

    ColumnLayout {
        id: processBody
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.margins: 7
        spacing: 3

        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            Text {
                Layout.fillWidth: true
                text: (root.modelData.appName ? (Number(root.modelData.depth) > 0 ? "↳ " : "● ") : "• ") + root.modelData.name
                color: Session.foreground
                font.family: Session.fontFamily
                font.pixelSize: 11
                font.weight: Font.DemiBold
                elide: Text.ElideRight
            }
            Text {
                text: root.widgetRoot.tr("pid") + " " + root.modelData.pid
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 9
            }
        }

        Text {
            Layout.fillWidth: true
            text: root.widgetRoot.tr("ppid") + " " + (root.modelData.parentName || "PID") + " (" + root.modelData.ppid + ") · " + root.widgetRoot.processRoleLabel(root.modelData)
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 9
            wrapMode: Text.Wrap
        }

        Text {
            Layout.fillWidth: true
            text: root.modelData.command
            color: Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 9
            elide: Text.ElideMiddle
            maximumLineCount: 1
        }

        Text {
            Layout.fillWidth: true
            text: root.widgetRoot.associationLabel(root.modelData)
            color: root.modelData.appName ? Session.accent : Session.muted
            font.family: Session.fontFamily
            font.pixelSize: 9
            wrapMode: Text.Wrap
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: 5
            Text {
                Layout.fillWidth: true
                visible: !root.modelData.canSignal
                text: root.widgetRoot.tr("protected")
                color: Session.muted
                font.family: Session.fontFamily
                font.pixelSize: 9
                wrapMode: Text.Wrap
            }
            Text {
                Layout.fillWidth: true
                visible: root.modelData.canSignal && root.widgetRoot.forceProcessKey !== root.widgetRoot.processKey(root.modelData)
                text: ""
            }
            Text {
                Layout.fillWidth: true
                visible: root.widgetRoot.forceProcessKey === root.widgetRoot.processKey(root.modelData)
                text: root.widgetRoot.tr("forceWarning")
                color: PolyTheme.Theme.color("#e5b878")
                font.family: Session.fontFamily
                font.pixelSize: 9
                wrapMode: Text.Wrap
            }
            Button {
                visible: root.modelData.canSignal
                enabled: !root.widgetRoot.terminatorRunning && root.widgetRoot.pendingProcessKey !== root.widgetRoot.processKey(root.modelData)
                text: root.widgetRoot.forceProcessKey === root.widgetRoot.processKey(root.modelData)
                    ? root.widgetRoot.tr("forceKill")
                    : (root.widgetRoot.pendingProcessKey === root.widgetRoot.processKey(root.modelData) ? "…" : root.widgetRoot.tr("endProcess"))
                onClicked: root.widgetRoot.requestSignal(root.modelData, root.widgetRoot.forceProcessKey === root.widgetRoot.processKey(root.modelData))
            }
        }
    }
}
