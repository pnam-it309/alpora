# Appearance settings — proposed reference

Generated with built-in image_gen on 2026-10-21 from settings-center-implemented.png and inspected current settings source/configuration. This image is a design proposal; it does not implement additional controls. Existing visual settings cover shared window/bar/menu rounding, bar/menu/launcher opacity, active/inactive application opacity and blur. Per-element widget/notification styling, configurable padding, outlines, shadows and expanded animation controls require implementation. Work/Vibe and visual themes remain independent. Actual current blur behavior must be preserved/reviewed during implementation rather than inferred from this mockup.

Image: appearance-per-element-proposal-v1.png

Exact prompt:

Use case: ui-mockup.
Create a high-fidelity UI design reference for extending an EXISTING Poly Shell Linux settings app. Supplied reference is the actual current app; preserve its strong recognizable identity and layout, not a new visual brand. Output one straight-on app screenshot mockup, approximately 1650x1200 (11:8 aspect), no monitor hardware, no surrounding desktop, no presentation text outside the window. This is a proposed future design, not documentation of shipped controls.

Reference invariants: dark desaturated forest-green/charcoal surfaces, sage/mint accent matching current forest theme, thin subdued pale-green outlines, rounded corners, restrained low-poly mountain decoration only at upper-right header, geometric little POLY logo, clean sans-serif readable Russian typography. Sidebar about 21% width. Compact and practical desktop application, not dramatic glass, not mobile, no giant wasted whitespace. Keep all text sharp, legible and correctly spelled. Scale the reference UI proportionately for this higher-resolution mockup.

Left sidebar: POLY logo and "Настройки", search field "Поиск настроек". Navigation headings and items: "ОСНОВНОЕ", "Обзор", "Wi-Fi", "Bluetooth"; "РАБОЧИЙ СТОЛ", "Мониторы", "Темы и обои", "Внешний вид" SELECTED in a sage-tinted rounded outline, "Виджеты", "Панель и меню"; "СИСТЕМА", "Звук", "Питание", "Уведомления", "Клавиатура и мышь". Small bottom theme card "Лесной туман" / "Текущая тема". Subtle line icons matching source app.

Main header: "Внешний вид", subtitle "Настрой каждый элемент под себя", close x top right, small decorative polygon mountain ridge behind right side of header.
Below header, a horizontal component selector of six compact rounded tabs: "Окна", "Бар", "Меню" SELECTED, "Виджеты", "Лаунчер", "Уведомления". This selects what object is being styled; not a row of duplicate sidebar sections.

Main content below is two columns: controls around 60%, preview 40%.
Left controls column:
Card 1 header "Материал", small subtitle "Фон меню и всплывающих панелей".
Row "Непрозрачность фона" with slider and editable numeric pill "75 %"; helper line "100% — сплошной фон".
Row "Размытие фона" with enabled sage toggle.
Row "Сила размытия" with slider and numeric pill "3".
Card 2 header "Форма и отступы".
Row "Скругление углов" with slider and numeric pill "20 px".
Row "Внутренние отступы" with slider and numeric pill "16 px".
Row "Толщина обводки" with compact stepper numeric "1 px".
Card 3 compact horizontal header "Тень" with enabled toggle, one row slider "Интенсивность" numeric "20 %".
Bottom slim collapsed row "Анимации" with right-side summary "Плавные · 220 мс" and chevron.
Every card uses tidy consistent spacing, alignment, shared slider lengths, right-aligned numeric fields and thin borders. Small reset arrow icons at card headings, unobtrusive.

Right preview column:
Title "ПРЕДПРОСМОТР".
Large roughly square miniature desktop scene with existing-style alpine low-poly lake wallpaper, narrow top bar and a beautiful compact quick-control menu, NOT a generic website. Quick menu visibly rounded corners 20 px, translucent dark green tinted background with soft blurred wallpaper behind it, one small mountain header, Wi-Fi/Bluetooth compact tiles, speaker and brightness sliders with icons. Subtle sage selection outline around the quick menu connects to selected "Меню" tab.
Below scene a compact segmented preview background selector labeled "Светлый" / "Тёмный".
A small explanatory card "Меню оболочки" and text "Быстрые настройки, календарь и всплывающие панели".
Below that an unobtrusive theme compatibility note "Параметры сохраняются при смене темы".
At bottom of preview column a small text button "Сбросить настройки элемента".

Fixed footer spanning main content, separated by thin line: left status dot and "Есть несохранённые изменения", right "Отменить" outlined button and "Применить" sage filled button with check icon. Ensure footer is fully visible inside window, no clipped controls.
Avoid: ornamental fantasy scenes, wallpapers as main subject, neon, glowing blobs, hard bevel corners, excessive gradients, large headings, promotional captions, English labels, tiny illegible text, duplicated controls, complex diagram, multiple windows. The result must feel like a plausible professionally extended version of the supplied settings app, with richer user control and clear selected-element editing.

