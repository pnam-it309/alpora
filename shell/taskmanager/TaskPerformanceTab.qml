pragma ComponentBehavior: Bound
import QtQuick
import ".."
import QtQuick.Layouts

Item {
    id: root
    property var performanceData: ({})
    property var cpuHistory: []
    RowLayout {
        anchors.fill: parent; anchors.margins: 16; spacing: 16
        // Left list cards
        ColumnLayout {
            Layout.preferredWidth: 260; Layout.fillHeight: true; spacing: 10
            // CPU Card
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 90; radius: 8
                color: Glass.tint(Session.surface, 0.7); border.width: 1; border.color: Glass.tint(Session.accent, 0.3)
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 12
                    RowLayout {
                        Text { text: "CPU"; color: Session.accent; font.pixelSize: 13; font.weight: Font.Bold }
                        Item { Layout.fillWidth: true }
                        Text { text: ((root.performanceData.cpu || {}).percent || 0) + "%"; color: Session.foreground; font.pixelSize: 15; font.weight: Font.Bold }
                    }
                    Text { text: (root.performanceData.cpu || {}).model || "Processor"; color: Session.muted; font.pixelSize: 10; elide: Text.ElideRight; Layout.fillWidth: true }
                }
            }
            // Memory Card
            Rectangle {
                Layout.fillWidth: true; Layout.preferredHeight: 90; radius: 8
                color: Glass.tint(Session.surface, 0.7); border.width: 1; border.color: Glass.tint(Session.accent, 0.3)
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 12
                    RowLayout {
                        Text { text: I18n.tr("tasks.col_memory"); color: Session.accent; font.pixelSize: 13; font.weight: Font.Bold }
                        Item { Layout.fillWidth: true }
                        Text { text: ((root.performanceData.memory || {}).percent || 0) + "%"; color: Session.foreground; font.pixelSize: 15; font.weight: Font.Bold }
                    }
                    Text { text: ((root.performanceData.memory || {}).used_mb || 0) + " / " + ((root.performanceData.memory || {}).total_mb || 0) + " MB"; color: Session.muted; font.pixelSize: 11 }
                }
            }
            Item { Layout.fillHeight: true }
        }

        // Right live graph
        Rectangle {
            Layout.fillWidth: true; Layout.fillHeight: true; radius: 8
            color: Glass.tint(Session.surface, 0.4); border.width: 1; border.color: Glass.tint(Session.accent, 0.2)
            ColumnLayout {
                anchors.fill: parent; anchors.margins: 16; spacing: 10
                Text { text: I18n.tr("tasks.cpu_graph_title"); color: Session.foreground; font.pixelSize: 14; font.weight: Font.DemiBold }
                Canvas {
                    id: perfCanvas
                    Layout.fillWidth: true; Layout.fillHeight: true
                    onPaint: {
                        const ctx = getContext("2d");
                        ctx.reset();
                        ctx.strokeStyle = Session.accent;
                        ctx.lineWidth = 2.5;
                        const data = root.cpuHistory;
                        if (data.length < 2) return;
                        const stepX = width / Math.max(1, data.length - 1);
                        ctx.beginPath();
                        for (let i = 0; i < data.length; i++) {
                            const x = i * stepX;
                            const y = height - (data[i] / 100.0) * height;
                            if (i === 0) ctx.moveTo(x, y);
                            else ctx.lineTo(x, y);
                        }
                        ctx.stroke();
                    }
                    Connections {
                        target: root
                        function onCpuHistoryChanged(): void { perfCanvas.requestPaint(); }
                    }
                }
            }
        }
    }
}
