"""Capability-oriented runtime inventory; optional tools do not block the shell."""
import importlib.util
import shutil

# Name, Arch package, binaries, purpose, required for the shell foundation.
PROGRAMS = (
    ('Quickshell','quickshell',('quickshell',),'Панель, настройки, виджеты',True),
    ('Hyprland','hyprland',('hyprctl',),'Окна, рабочие столы, горячие клавиши',True),
    ('Python','python',('python3',),'Настройки и системные адаптеры',True),
    ('systemd','systemd',('systemctl','systemd-run'),'Запуск оболочки и настроек',True),
    ('D-Bus tools','glib2',('gdbus',),'События уведомлений и сна',True),
    ('Foot','foot',('foot',),'Терминал по умолчанию, если установлен',False),
    ('Kitty','kitty',('kitty',),'Дополнительный терминал; полная сессия использует Foot',False),
    ('Nautilus','nautilus',('nautilus',),'Файловый менеджер, текущий Super+E',False),
    ('XDG utilities','xdg-utils',('xdg-open','xdg-mime'),'Системный обработчик папок',False),
    ('XDG user directories','xdg-user-dirs',('xdg-user-dir',),'Каталог изображений для снимков экрана',False),
    ('Fuzzel','fuzzel',('fuzzel',),'Внешний запасной запускатель; основной встроен в оболочку',False),
    ('UPower','upower',('upower',),'Состояние батареи и зарядки',False),
    ('WirePlumber','wireplumber',('wpctl',),'Громкость, микрофон и мультимедийные клавиши',False),
    ('NetworkManager','networkmanager',('nmcli','nmtui'),'Wi-Fi и расширенное подключение',False),
    ('Network editor','nm-connection-editor',('nm-connection-editor',),'Текущий Super+N',False),
    ('BlueZ tools','bluez-utils',('bluetoothctl',),'Bluetooth и сопряжение',False),
    ('rfkill','util-linux',('rfkill',),'Авиарежим и блокировка радиоустройств',False),
    ('Brightnessctl','brightnessctl',('brightnessctl',),'Яркость экрана',False),
    ('Hyprsunset','hyprsunset',('hyprsunset',),'Ночной свет',False),
    ('Mako','mako',('mako','makoctl'),'Уведомления, история, режим тишины',False),
    ('Pavucontrol','pavucontrol',('pavucontrol',),'Расширенные настройки звука',False),
    ('Power profiles','power-profiles-daemon',('powerprofilesctl',),'Профили энергопотребления',False),
    ('Swaybg','swaybg',('swaybg',),'Статические обои',False),
    ('Hyprlock','hyprlock',('hyprlock',),'Экран блокировки',False),
    ('Hypridle','hypridle',('hypridle',),'Бездействие, гашение экрана и блокировка',False),
    ('Hyprshutdown','hyprshutdown',('hyprshutdown',),'Текущий Super+Shift+E',False),
    ('wl-clipboard','wl-clipboard',('wl-copy','wl-paste'),'Буфер обмена и его история',False),
    ('Playerctl','playerctl',('playerctl',),'Мультимедийные клавиши; виджеты используют MPRIS напрямую',False),
    ('Grim','grim',('grim',),'Снимок экрана',False),
    ('Slurp','slurp',('slurp',),'Выбор области снимка',False),
    ('Libnotify','libnotify',('notify-send',),'Уведомление о сохранённом снимке',False),
    ('GSettings','glib2',('gsettings',),'Согласование темы GTK и значков',False),
)


def inventory():
    result=[]
    for name,package,commands,purpose,required in PROGRAMS:
        tools={command:shutil.which(command) for command in commands}
        result.append(dict(name=name,package=package,tools=tools,purpose=purpose,required=required,
                           available=all(tools.values())))
    pillow=importlib.util.find_spec('PIL') is not None
    result.append(dict(name='Pillow',package='python-pillow',tools={'PIL':pillow},
                       purpose='Импорт обоев, извлечение палитры и подготовка Timeline',required=False,available=pillow))
    return result
