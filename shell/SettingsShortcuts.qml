pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ColumnLayout {
    id: root
    spacing: 12
    property var editing: null
    property string formError: ""
    onEditingChanged: ShortcutsState.editingForm=!!editing
    Component.onDestruction: ShortcutsState.editingForm=false
    readonly property string action: ShortcutsState.actions[actionSelect.currentIndex]?.id || "command"
    readonly property var shown: ShortcutsState.draft.filter(r=>(showDisabled.checked || r.enabled)
        && (!search.text.trim() || [r.title,r.key,r.argument].join(" ").toLowerCase().includes(search.text.trim().toLowerCase())))
    Component.onCompleted: ShortcutsState.refresh()
    function open(item: var): void {
        editing=ShortcutsState.copy(item);formError="";
        titleField.text=item.title;keyField.text=item.key;argumentField.text=item.argument;
        actionSelect.currentIndex=Math.max(0,ShortcutsState.actions.findIndex(a=>a.id===item.action));
        globalSelect.currentIndex=Math.max(0,ShortcutsState.globals.findIndex(a=>a.id===item.argument));
        activeCheck.checked=item.enabled;repeatCheck.checked=item.repeat;lockedCheck.checked=item.locked;
    }
    function saveForm(): void {
        const argument=action==="global"?(ShortcutsState.globals[globalSelect.currentIndex]?.id || ""):argumentField.text;
        if(!titleField.text.trim() || !keyField.text.trim() || (["command","workspace","move-workspace"].includes(action) && !argument.trim())) {
            formError="Заполни название, сочетание и действие";return;
        }
        const duplicate=ShortcutsState.draft.some(r=>r.id!==editing.id && r.enabled && activeCheck.checked
            && r.key.replace(/\s/g,"").toUpperCase()===keyField.text.replace(/\s/g,"").toUpperCase());
        if(duplicate){formError="Это сочетание уже занято. Сначала измени или отключи другую запись.";return;}
        ShortcutsState.edit(Object.assign({},editing,{title:titleField.text.trim(),key:keyField.text.trim(),action:action,
            argument:argument,enabled:activeCheck.checked,repeat:repeatCheck.checked,locked:lockedCheck.checked}));
        editing=null;
    }
    Text {Layout.fillWidth:true;text:"Горячие клавиши";color:Session.foreground;font.family:Session.fontFamily;font.pixelSize:18;font.weight:Font.Medium}
    Text {Layout.fillWidth:true;text:"Добавляй свои сочетания и меняй существующие. Изменения вступят в силу после «Применить» и сохранятся после входа в систему.";color:Session.muted;font.family:Session.fontFamily;font.pixelSize:12;wrapMode:Text.Wrap}
    RowLayout {
        Layout.fillWidth:true;spacing:8
        TextField {id:search;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;placeholderText:"Поиск по названию, клавише или команде";color:Session.foreground;Accessible.name:"Поиск горячих клавиш"}
        AppearanceButton {text:"Добавить";symbol:"plus";enabled:ShortcutsState.loaded && !ShortcutsState.busy && !root.editing;onClicked:root.open({id:"custom-"+Date.now()+"-"+Math.floor(Math.random()*100000),source:"",key:"",title:"",action:"command",argument:"",enabled:true,locked:false,repeat:false})}
        AppearanceButton {text:"Обновить";symbol:"refresh";enabled:!ShortcutsState.busy && !ShortcutsState.dirty && !root.editing;onClicked:ShortcutsState.refresh()}
    }
    SettingsCard {
        Layout.fillWidth:true;visible:!!root.editing
        GridLayout {
            Layout.fillWidth:true;columns:2;columnSpacing:12;rowSpacing:8
            TextField {id:titleField;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;placeholderText:"Название действия";maximumLength:160;color:Session.foreground;Accessible.name:"Название горячей клавиши"}
            TextField {id:keyField;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;placeholderText:"SUPER + SHIFT + E";maximumLength:100;color:Session.foreground;Accessible.name:"Сочетание клавиш"}
            ComboBox {id:actionSelect;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;model:ShortcutsState.actions;textRole:"title";Accessible.name:"Действие горячей клавиши"}
            TextField {id:argumentField;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;visible:root.action!=="global";enabled:["command","workspace","move-workspace"].includes(root.action);placeholderText:root.action==="command"?"Команда, например nautilus --new-window":"Номер рабочего стола";maximumLength:4096;color:Session.foreground;Accessible.name:"Команда или номер рабочего стола"}
            ComboBox {id:globalSelect;palette.base:Session.surface;palette.button:Session.surface;palette.text:Session.foreground;palette.buttonText:Session.foreground;palette.highlight:Session.accent;palette.highlightedText:Session.background;Layout.fillWidth:true;visible:root.action==="global";model:ShortcutsState.globals;textRole:"title";Accessible.name:"Раздел оболочки"}
        }
        Text {Layout.fillWidth:true;text:"SUPER — клавиша Windows. Введи сочетание текстом: SUPER + E, CTRL + ALT + F1, Print. Клавиши указываются латиницей.";color:Session.muted;font.family:Session.fontFamily;font.pixelSize:11;wrapMode:Text.Wrap}
        RowLayout {
            Layout.fillWidth:true
            CheckBox {id:activeCheck;text:"Включено";palette.windowText:Session.foreground}
            CheckBox {id:repeatCheck;text:"Повтор при удержании";palette.windowText:Session.foreground}
            CheckBox {id:lockedCheck;text:"На экране блокировки";palette.windowText:Session.foreground}
        }
        Text {Layout.fillWidth:true;visible:!!root.formError;text:root.formError;color:Session.foreground;font.family:Session.fontFamily;font.pixelSize:12;wrapMode:Text.Wrap}
        RowLayout {
            Layout.fillWidth:true
            Item {Layout.fillWidth:true}
            AppearanceButton {text:"Отменить редактирование";symbol:"close";onClicked:root.editing=null}
            AppearanceButton {text:"Готово";symbol:"check";primary:true;enabled:!ShortcutsState.busy;onClicked:root.saveForm()}
        }
    }
    CheckBox {id:showDisabled;visible:!root.editing;text:"Показывать отключённые сочетания";palette.windowText:Session.foreground}
    ListView {
        id:list
        visible:!root.editing
        Layout.fillWidth:true;Layout.fillHeight:true;Layout.minimumHeight:100
        clip:true;spacing:6;model:root.shown
        ScrollBar.vertical:ScrollBar {}
        delegate:Rectangle {
            id:shortcutRow
            required property var modelData
            width:list.width;height:70;radius:10;color:Session.surface
            opacity:modelData.enabled?1:.6
            RowLayout {
                anchors.fill:parent;anchors.margins:10;spacing:12
                ColumnLayout {
                    Layout.fillWidth:true;spacing:3
                    Text {Layout.fillWidth:true;text:shortcutRow.modelData.title;elide:Text.ElideRight;color:Session.foreground;font.family:Session.fontFamily;font.pixelSize:13}
                    Text {Layout.fillWidth:true;text:shortcutRow.modelData.key+" · "+(shortcutRow.modelData.action==="command"?shortcutRow.modelData.argument:(ShortcutsState.actions.find(a=>a.id===shortcutRow.modelData.action)?.title || ""));elide:Text.ElideRight;color:Session.muted;font.family:Session.fontFamily;font.pixelSize:11}
                }
                AppearanceButton {text:"Изменить";symbol:"settings";enabled:!ShortcutsState.busy && !root.editing;onClicked:root.open(shortcutRow.modelData)}
                AppearanceButton {text:shortcutRow.modelData.enabled?"Удалить":"Вернуть";symbol:shortcutRow.modelData.enabled?"close":"plus";enabled:!ShortcutsState.busy && !root.editing;onClicked:shortcutRow.modelData.enabled?ShortcutsState.remove(shortcutRow.modelData.id):ShortcutsState.edit(Object.assign({},shortcutRow.modelData,{enabled:true}))}
            }
        }
        Text {anchors.centerIn:parent;visible:!list.count;text:ShortcutsState.loaded?"Нет сочетаний по этому запросу":"Загрузка…";color:Session.muted;font.family:Session.fontFamily;font.pixelSize:13}
    }
    Text {Layout.fillWidth:true;visible:ShortcutsState.external.length>0 && !root.editing;text:"Внешние сочетания и жесты мыши: "+ShortcutsState.external.length+". Они сохраняются в конфигурации Hyprland; редактор не перезаписывает неизвестные действия и подрежимы.";color:Session.muted;font.family:Session.fontFamily;font.pixelSize:11;wrapMode:Text.Wrap}
    RowLayout {
        id:footer
        Layout.fillWidth:true
        Text {Layout.fillWidth:true;text:root.editing?"Заверши редактирование записи":ShortcutsState.error || ShortcutsState.message || (ShortcutsState.dirty?"Есть несохранённые изменения":"Всё сохранено");color:Session.foreground;font.family:Session.fontFamily;font.pixelSize:12;wrapMode:Text.Wrap}
        AppearanceButton {text:"Отменить";symbol:"close";enabled:ShortcutsState.dirty && !ShortcutsState.busy && !root.editing;onClicked:ShortcutsState.cancel()}
        AppearanceButton {text:ShortcutsState.busy?"Проверка…":"Применить";symbol:"check";primary:true;enabled:ShortcutsState.dirty && !ShortcutsState.busy && !root.editing;onClicked:ShortcutsState.apply()}
    }
}
