pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

RowLayout {
    id: root
    signal activated
    spacing: 8

    MacroActionTile {
        Layout.fillWidth: true
        title: "Terminal"
        subtitle: "Super+Enter"
        symbol: "terminal"
        execCommand: "foot || alacritty || kitty"
        onActivated: root.activated()
    }

    MacroActionTile {
        Layout.fillWidth: true
        title: "Task Mgr"
        subtitle: "Ctrl+Esc"
        symbol: "developer"
        execCommand: "poly-shell task-manager || btop"
        onActivated: root.activated()
    }

    MacroActionTile {
        Layout.fillWidth: true
        title: "Lock"
        subtitle: "Super+L"
        symbol: "lock"
        execCommand: "loginctl lock-session"
        onActivated: root.activated()
    }
}
