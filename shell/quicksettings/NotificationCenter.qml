pragma ComponentBehavior: Bound
import QtQuick
import ".."
import "../theme" as PolyTheme
import QtQuick.Controls
import QtQuick.Layouts
import Quickshell

ColumnLayout {
    id: root
    implicitWidth: 420
    implicitHeight: 560
    spacing: 10

    property bool groupByApp: true
    property string activeAppFilter: ""
    property string searchQuery: ""
    property var historyItems: []
    property var groupedItems: ({})
    property var appList: []
    property var displayGroups: []
    property var summary: ({ total: 0, unread: 0, critical: 0, apps: [] })
    readonly property int totalCount: historyItems ? historyItems.length : 0

    function formatTimeAgo(timestamp: real): string {
        if (!timestamp || timestamp <= 0) return I18n.tr("notification.ago_now");
        const diff = Math.max(0, Math.floor(Date.now() / 1000 - timestamp));
        if (diff < 60) return I18n.tr("notification.ago_now");
        if (diff < 3600) return I18n.trWith("notification.ago_min", { n: Math.floor(diff / 60) });
        if (diff < 86400) return I18n.trWith("notification.ago_hour", { n: Math.floor(diff / 3600) });
        return I18n.trWith("notification.ago_day", { n: Math.floor(diff / 86400) });
    }

    function refresh(): void {
        if (IpcClient.socketConnected) {
            IpcClient.request("notifications.list", { query: root.searchQuery }, (res, err) => {
                if (!err && res && res.notifications) {
                    root.historyItems = res.notifications;
                    if (res.summary) {
                        root.summary = res.summary;
                        root.appList = res.summary.apps || [];
                    }
                }
            });
            IpcClient.request("notifications.grouped", {}, (res, err) => {
                if (!err && res && res.groups) {
                    root.groupedItems = res.groups;
                    root.updateDisplayGroups();
                }
            });
        } else {
            const raw = BarState.visibleHistory || [];
            root.historyItems = raw;
            root.groupFallbackItems(raw);
        }
    }

    function groupFallbackItems(rawList: var): void {
        const groups = {};
        const apps = [];
        for (let i = 0; i < rawList.length; ++i) {
            const item = rawList[i];
            const app = item.app_name || item.appName || "System";
            if (!groups[app]) {
                groups[app] = [];
                apps.push(app);
            }
            groups[app].push(item);
        }
        root.groupedItems = groups;
        root.appList = apps;
        root.updateDisplayGroups();
    }

    function updateDisplayGroups(): void {
        const result = [];
        const keys = Object.keys(root.groupedItems || {});
        for (let i = 0; i < keys.length; ++i) {
            const appName = keys[i];
            if (root.activeAppFilter.length > 0 && root.activeAppFilter !== appName) continue;
            let items = root.groupedItems[appName] || [];
            if (root.searchQuery.length > 0) {
                const q = root.searchQuery.toLowerCase();
                items = items.filter(it => {
                    const sum = (it.summary || "").toLowerCase();
                    const b = (it.body || "").toLowerCase();
                    return sum.includes(q) || b.includes(q);
                });
            }
            if (items.length > 0) {
                result.push({ appName: appName, items: items });
            }
        }
        root.displayGroups = result;
    }

    function clearAll(): void {
        if (IpcClient.socketConnected) {
            IpcClient.request("notifications.clear", {}, (_res, _err) => { root.refresh(); });
        } else {
            BarState.hideHistory();
            root.refresh();
        }
    }

    function clearApp(targetApp: string): void {
        if (IpcClient.socketConnected) {
            IpcClient.request("notifications.clear", { app: targetApp }, (_res, _err) => { root.refresh(); });
        } else {
            root.refresh();
        }
    }

    function dismissNotification(notifId: var): void {
        if (IpcClient.socketConnected) {
            IpcClient.request("notifications.dismiss", { id: notifId }, (_res, _err) => { root.refresh(); });
        } else {
            BarState.dismissNotification(Number(notifId) || 0);
            root.refresh();
        }
    }

    Connections {
        target: IpcClient
        function onEventReceived(eventName: string, _eventData: var): void {
            if (eventName === "notifications.updated" || eventName === "notifications") root.refresh();
        }
        function onSocketConnectedChanged(): void {
            if (IpcClient.socketConnected) root.refresh();
        }
    }

    Connections {
        target: BarState
        function onVisibleHistoryChanged(): void {
            if (!IpcClient.socketConnected) root.refresh();
        }
    }

    // Top Navigation & Action Header
    RowLayout {
        Layout.fillWidth: true
        Layout.preferredHeight: 38
        spacing: 8

        Icon {
            name: "bell"
            Layout.preferredWidth: 18; Layout.preferredHeight: 18
            Layout.alignment: Qt.AlignVCenter
        }

        Text {
            text: I18n.tr("notification.history_title")
            color: Session.foreground; font.family: Session.fontFamily
            font.pixelSize: 14; font.weight: Font.DemiBold
            Layout.alignment: Qt.AlignVCenter
        }

        Rectangle {
            visible: root.totalCount > 0
            radius: 9; Layout.preferredHeight: 18
            Layout.preferredWidth: Math.max(22, countText.implicitWidth + 10)
            color: Glass.tint(Session.accent, 0.22)
            border.width: 1; border.color: Glass.tint(Session.accent, 0.45)
            Layout.alignment: Qt.AlignVCenter

            Text {
                id: countText
                anchors.centerIn: parent
                text: String(root.totalCount); color: Session.accent
                font.family: Session.fontFamily; font.pixelSize: 10; font.weight: Font.Bold
            }
        }

        Item { Layout.fillWidth: true }

        // Mode switch: Grouped vs Chronological
        Button {
            id: modeBtn
            implicitHeight: 28; padding: 6; hoverEnabled: true
            Accessible.name: root.groupByApp ? I18n.tr("common.grouped") : I18n.tr("common.all")
            background: Rectangle {
                radius: 8
                color: modeBtn.hovered ? Glass.tint(Session.accent, 0.18) : Glass.tint(Session.surface, 0.35)
                border.width: 1
                border.color: modeBtn.hovered ? Glass.tint(Session.accent, 0.5) : Glass.tint(Session.accent, 0.2)
            }
            contentItem: RowLayout {
                spacing: 4
                Icon { name: root.groupByApp ? "layers" : "list"; Layout.preferredWidth: 14; Layout.preferredHeight: 14 }
                Text {
                    text: root.groupByApp ? I18n.tr("common.grouped") : I18n.tr("common.all")
                    color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 10
                }
            }
            onClicked: { root.groupByApp = !root.groupByApp; root.updateDisplayGroups(); }
        }

        DayAction {
            text: I18n.tr("notification.clear_history")
            visible: root.totalCount > 0; implicitHeight: 28
            onClicked: root.clearAll()
        }
    }

    // App Filter Tags (visible when >1 app exists)
    ScrollView {
        Layout.fillWidth: true; Layout.preferredHeight: 30
        visible: root.appList.length > 1; contentHeight: availableHeight
        ScrollBar.horizontal.policy: ScrollBar.AlwaysOff; ScrollBar.vertical.policy: ScrollBar.AlwaysOff

        Row {
            spacing: 6
            Button {
                id: allFilterBtn
                implicitHeight: 26; padding: 6; hoverEnabled: true
                background: Rectangle {
                    radius: 7
                    color: root.activeAppFilter === "" ? Glass.tint(Session.accent, 0.28) : (allFilterBtn.hovered ? Glass.tint(Session.accent, 0.16) : Glass.tint(Session.surface, 0.3))
                    border.width: 1; border.color: root.activeAppFilter === "" ? Session.accent : Glass.tint(Session.accent, 0.2)
                }
                contentItem: Text {
                    text: I18n.tr("common.all")
                    color: root.activeAppFilter === "" ? Session.accent : Session.muted
                    font.family: Session.fontFamily; font.pixelSize: 10
                    font.weight: root.activeAppFilter === "" ? Font.Bold : Font.Normal
                }
                onClicked: { root.activeAppFilter = ""; root.updateDisplayGroups(); }
            }

            Repeater {
                model: root.appList
                Button {
                    id: appPill
                    required property string modelData
                    implicitHeight: 26; padding: 6; hoverEnabled: true
                    background: Rectangle {
                        radius: 7
                        color: root.activeAppFilter === appPill.modelData ? Glass.tint(Session.accent, 0.28) : (appPill.hovered ? Glass.tint(Session.accent, 0.16) : Glass.tint(Session.surface, 0.3))
                        border.width: 1; border.color: root.activeAppFilter === appPill.modelData ? Session.accent : Glass.tint(Session.accent, 0.2)
                    }
                    contentItem: Text {
                        text: appPill.modelData
                        color: root.activeAppFilter === appPill.modelData ? Session.accent : Session.muted
                        font.family: Session.fontFamily; font.pixelSize: 10
                        font.weight: root.activeAppFilter === appPill.modelData ? Font.Bold : Font.Normal
                    }
                    onClicked: {
                        root.activeAppFilter = (root.activeAppFilter === appPill.modelData) ? "" : appPill.modelData;
                        root.updateDisplayGroups();
                    }
                }
            }
        }
    }

    // Main Notifications Viewport
    ScrollView {
        id: notifScroll
        Layout.fillWidth: true; Layout.fillHeight: true
        contentWidth: availableWidth; clip: true

        // Empty state
        Column {
            visible: root.totalCount === 0; width: notifScroll.availableWidth; topPadding: 60; spacing: 12
            Icon { anchors.horizontalCenter: parent.horizontalCenter; name: "bell"; width: 32; height: 32 }
            Text {
                width: parent.width; text: I18n.tr("notification.all_quiet")
                color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 14
                font.weight: Font.DemiBold; horizontalAlignment: Text.AlignHCenter
            }
            Text {
                width: parent.width; text: I18n.tr("notification.history_empty")
                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 11
                horizontalAlignment: Text.AlignHCenter
            }
        }

        // Grouped By App Mode
        Column {
            visible: root.totalCount > 0 && root.groupByApp
            width: notifScroll.availableWidth; spacing: 12

            Repeater {
                model: root.displayGroups
                Column {
                    id: appSection
                    required property var modelData
                    width: parent.width; spacing: 6

                    RowLayout {
                        width: parent.width; height: 24; spacing: 6
                        Text {
                            text: appSection.modelData.appName; color: Session.accent
                            font.family: Session.fontFamily; font.pixelSize: 11; font.weight: Font.Bold
                        }
                        Rectangle {
                            radius: 6; Layout.preferredHeight: 16
                            Layout.preferredWidth: Math.max(18, sectionCountText.implicitWidth + 8)
                            color: Glass.tint(Session.accent, 0.16); border.width: 1; border.color: Glass.tint(Session.accent, 0.3)
                            Text {
                                id: sectionCountText
                                anchors.centerIn: parent; text: String(appSection.modelData.items.length)
                                color: Session.accent; font.family: Session.fontFamily; font.pixelSize: 9
                            }
                        }
                        Item { Layout.fillWidth: true }
                        Button {
                            id: clearSecBtn
                            implicitHeight: 20; padding: 4; hoverEnabled: true
                            background: Item {}
                            contentItem: Text {
                                text: I18n.tr("notification.clear_history")
                                color: clearSecBtn.hovered ? Session.foreground : Session.muted
                                font.family: Session.fontFamily; font.pixelSize: 9
                            }
                            onClicked: root.clearApp(appSection.modelData.appName)
                        }
                    }

                    Repeater {
                        model: appSection.modelData.items
                        Rectangle {
                            id: groupedCard
                            required property var modelData
                            width: parent.width; implicitHeight: cardLayout.implicitHeight + 16
                            radius: Session.visual.notificationRadius
                            color: Glass.tint(Session.surface, Session.visual.notificationOpacity / 100)
                            border.width: Session.visual.notificationBorder
                            border.color: groupedCard.modelData.urgency === "critical" ? PolyTheme.Theme.color("#d18e82") : Glass.tint(Session.accent, 0.2)

                            ColumnLayout {
                                id: cardLayout
                                anchors.fill: parent; anchors.margins: 8; spacing: 4
                                RowLayout {
                                    Layout.fillWidth: true; spacing: 6
                                    Image {
                                        visible: !!groupedCard.modelData.app_icon && status === Image.Ready
                                        source: groupedCard.modelData.app_icon ? (groupedCard.modelData.app_icon.startsWith("/") ? "file://" + groupedCard.modelData.app_icon : Quickshell.iconPath(groupedCard.modelData.app_icon, true)) : ""
                                        Layout.preferredWidth: 16; Layout.preferredHeight: 16
                                        sourceSize.width: 32; sourceSize.height: 32; fillMode: Image.PreserveAspectFit
                                    }
                                    Text {
                                        text: root.formatTimeAgo(groupedCard.modelData.timestamp)
                                        color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 9
                                    }
                                    Item { Layout.fillWidth: true }
                                    BarButton {
                                        symbol: "close"; hint: I18n.tr("notification.dismiss")
                                        implicitWidth: 20; implicitHeight: 20
                                        onClicked: root.dismissNotification(groupedCard.modelData.id)
                                    }
                                }
                                Text {
                                    visible: !!groupedCard.modelData.summary; Layout.fillWidth: true
                                    text: groupedCard.modelData.summary || ""; textFormat: Text.PlainText
                                    color: Session.foreground; font.family: Session.fontFamily
                                    font.pixelSize: 11; font.weight: Font.DemiBold; wrapMode: Text.Wrap
                                    maximumLineCount: 2; elide: Text.ElideRight
                                }
                                Text {
                                    visible: !!groupedCard.modelData.body; Layout.fillWidth: true
                                    text: (groupedCard.modelData.body || "").replace(/<[^>]*>/g, "")
                                    textFormat: Text.PlainText; color: Session.muted
                                    font.family: Session.fontFamily; font.pixelSize: 10; wrapMode: Text.Wrap
                                    maximumLineCount: 3; elide: Text.ElideRight
                                }
                            }
                        }
                    }
                }
            }
        }

        // Chronological Mode
        Column {
            visible: root.totalCount > 0 && !root.groupByApp
            width: notifScroll.availableWidth; spacing: 6

            Repeater {
                model: root.historyItems
                Rectangle {
                    id: chronoCard
                    required property var modelData
                    width: parent.width; implicitHeight: chronoCardLayout.implicitHeight + 16
                    radius: Session.visual.notificationRadius
                    color: Glass.tint(Session.surface, Session.visual.notificationOpacity / 100)
                    border.width: Session.visual.notificationBorder
                    border.color: chronoCard.modelData.urgency === "critical" ? PolyTheme.Theme.color("#d18e82") : Glass.tint(Session.accent, 0.2)

                    ColumnLayout {
                        id: chronoCardLayout
                        anchors.fill: parent; anchors.margins: 8; spacing: 4
                        RowLayout {
                            Layout.fillWidth: true; spacing: 6
                            Image {
                                visible: !!chronoCard.modelData.app_icon && status === Image.Ready
                                source: chronoCard.modelData.app_icon ? (chronoCard.modelData.app_icon.startsWith("/") ? "file://" + chronoCard.modelData.app_icon : Quickshell.iconPath(chronoCard.modelData.app_icon, true)) : ""
                                Layout.preferredWidth: 16; Layout.preferredHeight: 16
                                sourceSize.width: 32; sourceSize.height: 32; fillMode: Image.PreserveAspectFit
                            }
                            Text {
                                text: chronoCard.modelData.app_name || chronoCard.modelData.appName || "System"
                                color: Session.accent; font.family: Session.fontFamily; font.pixelSize: 10; font.weight: Font.DemiBold
                            }
                            Text { text: "·"; color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 10 }
                            Text {
                                text: root.formatTimeAgo(chronoCard.modelData.timestamp)
                                color: Session.muted; font.family: Session.fontFamily; font.pixelSize: 9
                            }
                            Item { Layout.fillWidth: true }
                            BarButton {
                                symbol: "close"; hint: I18n.tr("notification.dismiss")
                                implicitWidth: 20; implicitHeight: 20
                                onClicked: root.dismissNotification(chronoCard.modelData.id)
                            }
                        }
                        Text {
                            visible: !!chronoCard.modelData.summary; Layout.fillWidth: true
                            text: chronoCard.modelData.summary || ""; textFormat: Text.PlainText
                            color: Session.foreground; font.family: Session.fontFamily
                            font.pixelSize: 11; font.weight: Font.DemiBold; wrapMode: Text.Wrap
                            maximumLineCount: 2; elide: Text.ElideRight
                        }
                        Text {
                            visible: !!chronoCard.modelData.body; Layout.fillWidth: true
                            text: (chronoCard.modelData.body || "").replace(/<[^>]*>/g, "")
                            textFormat: Text.PlainText; color: Session.muted
                            font.family: Session.fontFamily; font.pixelSize: 10; wrapMode: Text.Wrap
                            maximumLineCount: 3; elide: Text.ElideRight
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: root.refresh()
}
