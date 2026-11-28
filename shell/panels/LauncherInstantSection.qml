pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

ColumnLayout {
    id: root
    spacing: 6
    Layout.fillWidth: true

    property string mathResult: ""
    property bool isCommand: false
    property string commandText: ""
    property var webMatch: null
    property string webEngine: ""
    property string webTerm: ""
    property bool isPath: false
    property string resolvedPath: ""
    property string trimmedQuery: ""

    signal activated

    // Quick Calculator Instant Card
    LauncherInstantCard {
        visible: root.mathResult.length > 0
        icon: "calculator"
        title: "= " + root.mathResult
        subtitle: I18n.tr("launcher.copy_clipboard")
        emphasis: true
        onActivated: root.activated()
    }

    // Quick Command Runner Instant Card
    LauncherInstantCard {
        visible: root.isCommand && root.commandText.length > 0
        icon: "terminal"
        title: root.commandText
        subtitle: I18n.trWith("launcher.run_command", {cmd: root.commandText})
        onActivated: root.activated()
    }

    // Quick Web Search Instant Card
    LauncherInstantCard {
        visible: !!root.webMatch
        icon: "globe"
        title: root.webTerm
        subtitle: I18n.trWith("launcher.search_web", {
            engine: ({g: "Google", gh: "GitHub", yt: "YouTube", w: "Wikipedia"})[root.webEngine] || "Web",
            term: root.webTerm
        })
        onActivated: root.activated()
    }

    // Quick Folder Location Instant Card
    LauncherInstantCard {
        visible: root.isPath && root.resolvedPath.length > 0
        icon: "folder"
        title: root.trimmedQuery
        subtitle: I18n.tr("launcher.open_location")
        emphasis: true
        onActivated: root.activated()
    }
}
