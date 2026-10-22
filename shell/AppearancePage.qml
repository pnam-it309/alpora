pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "AppearanceCatalog.js" as Catalog

ScrollView {
 id: root
 property string element: AppearanceState.element
 contentWidth: availableWidth; clip: true
 ScrollBar.horizontal.policy: ScrollBar.AlwaysOff
 rightPadding: 6
 onElementChanged: { const view = contentItem as Flickable; if (view) view.contentY = 0; }
 Component.onCompleted: AppearanceState.begin()
 ColumnLayout {
  width: root.availableWidth; spacing: 12
  Repeater {
   model: Catalog.groups(root.element)
   AppearanceSection {
    id: group
    required property var modelData
    Layout.fillWidth: true
    title: modelData.title; symbol: modelData.icon
    description: modelData.title === "Материал" ? "100% — сплошной фон" : modelData.title === "Тень" ? "0% — без тени" : modelData.title === "Анимации" ? "0 мс — мгновенный переход" : root.element === "window" ? "Отступ на каждую сторону: 5 px дают 10 px между окнами. Внешний отступ — от рабочей области под баром. Для окон в раскладке." : root.element === "bar" && modelData.title === "Расположение" ? "Снизу резервируется свободное место для окон. Меню остаются рядом с баром." : ""
    Repeater {
     model: group.modelData.fields
     AppearanceSlider {
      required property var modelData
      Layout.fillWidth: true
      settingKey: modelData.key; label: modelData.label; minimum: modelData.min; maximum: modelData.max; suffix: modelData.suffix
     }
    }
   }
  }
  AppearanceSection {
   Layout.fillWidth: true; visible: root.element === "widget"
   title: "Движение виджетов"; description: "Дополнительно учитывается переключатель в разделе «Виджеты»."; symbol: "music"
   RowLayout {
    Layout.fillWidth: true
    Text { Layout.fillWidth: true; text: "Декоративные анимации"; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12; wrapMode: Text.Wrap }
    SettingsToggle { checked: !!AppearanceState.draft.widgetAnimations; enabled: !AppearanceState.busy; Accessible.name: "Декоративные анимации виджетов"; onToggled: AppearanceState.edit("widgetAnimations", checked) }
   }
  }
  AppearanceSection {
   Layout.fillWidth: true; visible: root.element === "window" || root.element === "panel" || root.element === "bar" || root.element === "launcher"
   title: "Общее размытие"; description: "Размывает окна и содержимое под панелями."; symbol: "blur"
   RowLayout {
    Layout.fillWidth: true
    Text { Layout.fillWidth: true; text: "Размывать фон"; color: Session.foreground; font.family: Session.fontFamily; font.pixelSize: 12 }
    SettingsToggle { checked: !!AppearanceState.draft.blurEnabled; enabled: !AppearanceState.busy; Accessible.name: "Общее размытие фона"; onToggled: AppearanceState.edit("blurEnabled", checked) }
   }
   AppearanceSlider { Layout.fillWidth: true; settingKey: "blurSize"; label: "Сила размытия"; minimum: 1; maximum: 8; suffix: ""; enabled: !!AppearanceState.draft.blurEnabled }
   AppearanceSlider { Layout.fillWidth: true; settingKey: "blurPasses"; label: "Проходы"; minimum: 1; maximum: 2; suffix: ""; enabled: !!AppearanceState.draft.blurEnabled }
  }
 }
}
