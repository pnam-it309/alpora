.pragma library
// Shared UI metadata; backend validates every saved value.
var defaults = {"windowRadius": 16, "barRadius": 20, "panelRadius": 20, "barOpacity": 75, "panelOpacity": 75, "launcherOpacity": 75, "activeOpacity": 100, "inactiveOpacity": 100, "blurEnabled": true, "blurSize": 3, "blurPasses": 1, "launcherRadius": 20, "widgetRadius": 16, "notificationRadius": 13, "widgetOpacity": 75, "notificationOpacity": 75, "panelPadding": 16, "launcherPadding": 18, "notificationPadding": 12, "barBorder": 1, "panelBorder": 1, "launcherBorder": 1, "widgetBorder": 1, "notificationBorder": 1, "barShadow": 20, "panelShadow": 20, "launcherShadow": 20, "widgetShadow": 0, "notificationShadow": 0, "panelOpenMs": 320, "panelCloseMs": 200, "launcherOpenMs": 320, "launcherCloseMs": 200, "widgetAnimations": true, "widgetFadeMs": 420, "barHeight": 40, "barMargin": 20, "barTop": 12, "barLeft": 20, "barRight": 20, "barBottom": 8, "windowGap": 5, "windowMargin": 12};

var elements = [
 {id:"window",title:"Окна",icon:"window",description:"Отступы управляют раскладкой окон. Непрозрачность затрагивает всё содержимое, включая текст."},
 {id:"bar",title:"Бар",icon:"panel",description:"Верхняя панель: материал, форма и расположение на экране."},
 {id:"panel",title:"Меню",icon:"settings",description:"Быстрые настройки, календарь и всплывающие панели."},
 {id:"widget",title:"Виджеты",icon:"devices",description:"Карточки часов, погоды и музыки на рабочем столе."},
 {id:"launcher",title:"Лаунчер",icon:"search",description:"Поиск и список приложений, включая компактную панель."},
 {id:"notification",title:"Уведомления",icon:"bell",description:"Карточки центра уведомлений и всплывающие сообщения Mako. Тень — только в центре."}
];
function field(key,label,min,max,suffix) { return {key:key,label:label,min:min,max:max,suffix:suffix===undefined?" px":suffix}; }
function groups(element) {
 var material=[],geometry=[],result=[];
 if(element==="window") {
  material=[field("activeOpacity","Активное окно",60,100," %"),field("inactiveOpacity","Неактивные окна",60,100," %")];
  geometry=[field("windowRadius","Скругление углов",0,32),field("windowMargin","От границ рабочей области",0,128),field("windowGap","Между окнами (на сторону)",0,64)];
 } else {
  material=[field(element+"Opacity","Непрозрачность фона",element==="launcher"?75:element==="panel"?50:element==="notification"?20:40,100," %")];
  geometry=[field(element+"Radius","Скругление углов",0,element==="bar"?20:32)];
  if(["panel","launcher","notification"].indexOf(element)>=0) geometry.push(field(element+"Padding","Внутренние отступы",element==="notification"?6:8,24));
  geometry.push(field(element+"Border","Толщина обводки",0,3));
 }
 result.push({title:"Материал",icon:"transparency",fields:material});
 result.push({title:"Форма и отступы",icon:"rounded",fields:geometry});
 if(element==="bar") result.push({title:"Расположение",icon:"monitor",fields:[field("barHeight","Высота панели",32,80),field("barLeft","Отступ слева",0,128),field("barRight","Отступ справа",0,128),field("barTop","Отступ сверху",0,64),field("barBottom","Свободное место под баром",0,128)]});
 if(element!=="window") result.push({title:"Тень",icon:"focus",fields:[field(element+"Shadow","Интенсивность",0,100," %")]});
 if(element==="panel"||element==="launcher") result.push({title:"Анимации",icon:"music",fields:[field(element+"OpenMs","Открытие",0,800," мс"),field(element+"CloseMs","Закрытие",0,800," мс")]});
 if(element==="widget") result.push({title:"Анимации",icon:"music",fields:[field("widgetFadeMs","Появление карточек",0,800," мс")]});
 return result;
}
function keys(element) {
 var result=[];groups(element).forEach(function(g){g.fields.forEach(function(f){result.push(f.key);});});
 if(element==="widget")result.push("widgetAnimations");
 return result;
}
function resolve(value,bar) {
 var out=Object.assign({},defaults,value||{});bar=bar||{};
 [["barHeight","height"],["barMargin","margin"],["barTop","top"]].forEach(function(pair){if(!value||value[pair[0]]===undefined)out[pair[0]]=bar[pair[1]]===undefined?defaults[pair[0]]:bar[pair[1]];});
 ["barLeft","barRight"].forEach(function(key){if(!value||value[key]===undefined)out[key]=out.barMargin;});
 if(value&&value.launcherRadius===undefined&&value.panelRadius!==undefined)out.launcherRadius=value.panelRadius;
 return out;
}
