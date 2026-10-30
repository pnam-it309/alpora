/**
 * ALPORA Panel Motion Laboratory
 * Interactive animation studies for the Quickshell TopBar and popup panels.
 * Supports multi-language (VI, EN, RU), 7 visual themes, and variable playback speeds.
 */

'use strict';

const I18N = {
  vi: {
    brand: "ALPORA / CHUYỂN ĐỘNG",
    badge: "PHÒNG THÍ NGHIỆM TƯƠNG TÁC",
    title: "16 Phong cách chuyển động của Panel",
    subtitle: "Khám phá các phương án mở, đóng và biến đổi cho Quick Settings, Calendar và Notifications trước khi đưa vào Quickshell.",
    playAll: "↻ Chạy tất cả",
    closeAll: "Đóng tất cả",
    speed: "Tốc độ",
    theme: "Chủ đề",
    mode: "Chế độ",
    workMode: "Làm việc",
    vibeMode: "Thư giãn",
    open: "Mở",
    close: "Đóng",
    repeat: "Thử lại",
    opened: "Đang mở",
    closed: "Đã đóng",
    qmlCode: "Mã QML",
    copyQml: "Sao chép QML",
    copied: "Đã sao chép!",
    backToHub: "← Quay lại ALPORA Demo Hub",
    footerHint: "Nhấp vào bất kỳ nút nào trên mini-bar hoặc thẻ để kiểm tra chuyển động · Nhấn phím Esc để đóng tất cả.",
    hintTitle: "Gợi ý tương tác:",
    studies: [
      { id: 'slide', title: 'Trượt mềm (Soft Slide)', desc: 'Panel trượt xuống êm ái từ mép dưới của TopBar rồi dừng nhẹ nhàng. Khi đóng trượt ngược lên.', hint: 'Dịch chuyển trục Y + mờ dần (opacity). Chuẩn mặc định cho desktop gọn gàng.' },
      { id: 'curtain', title: 'Kéo rèm (Curtain Drop)', desc: 'Mép trên cố định dưới TopBar. Panel mở dần xuống dưới như tấm rèm buông nhẹ.', hint: 'Mở rộng chiều cao với clip-path bo tròn 14px; văn bản không bị co giãn.' },
      { id: 'origin', title: 'Phóng từ icon (Origin Pop)', desc: 'Từ vị trí icon được nhấn trên TopBar, một khối nhỏ bung nở thành cửa sổ hoàn chỉnh.', hint: 'Tâm biến đổi (transform-origin) gắn chặt với tọa độ icon bấm.' },
      { id: 'pop', title: 'Nảy nhẹ (Subtle Pop-in)', desc: 'Panel xuất hiện với độ phóng to 94% -> 100% kèm tăng dần độ trong suốt, không rung lắc.', hint: 'Tăng nhẹ kích thước + mượt mà. Rất phù hợp với chế độ Work tối giản.' },
      { id: 'spring', title: 'Độ nảy lò xo (Spring Bounce)', desc: 'Panel trượt xuống, vượt nhẹ qua điểm dừng một chút rồi bật khẽ trở lại vị trí cân bằng.', hint: 'Hiệu ứng lò xo tinh tế tạo cảm giác phản hồi vật lý sống động.' },
      { id: 'morph', title: 'Biến đổi tab (Morph Switch)', desc: 'Panel tự động co giãn kích thước, di chuyển vị trí và đổi nội dung mượt mà khi bấm tab khác.', hint: 'Thử chuyển qua lại giữa Đồng hồ, Lịch, Thông báo và Cài đặt!', pages: true },
      { id: 'center', title: 'Mở từ tâm (Center Expand)', desc: 'Từ một điểm nhỏ ở giữa bung thành thanh ngang mỏng, sau đó mở rộng theo chiều dọc.', hint: 'Chuyển động 2 pha: Chiều ngang (Width) -> Chiều dọc (Height).' },
      { id: 'iris', title: 'Mở khẩu độ (Circular Iris)', desc: 'Một mặt nạ hình tròn từ icon nút bấm mở rộng dần ra xung quanh làm lộ panel.', hint: 'Clip-path dạng circle(r at x y) mở rộng 0% -> 145%.' },
      { id: 'depth', title: 'Chiều sâu 3D (Depth Perspective)', desc: 'Panel phóng to từ không gian 3D phía sau, xoay nhẹ góc nghiêng và áp sát màn hình.', hint: 'Sử dụng perspective 800px + translateZ(-180px) + rotateX(22deg).' },
      { id: 'hinge', title: 'Bản lề thả (Hinge Drop)', desc: 'Panel xoay quanh bản lề mép trên thả xuống như cánh cửa tủ mở nhẹ.', hint: 'Xoay 3D quanh trục trên rotateX(-88deg -> 0deg).' },
      { id: 'fold', title: 'Gấp nếp giấy (Origami Fold)', desc: 'Nửa trên mở ra trước, sau đó nửa dưới bung tiếp theo như mở một tờ giấy gấp đôi.', hint: 'Hai mảnh độc lập với trục xoay riêng biệt.' },
      { id: 'liquid', title: 'Giọt nước lỏng (Liquid Droplet)', desc: 'Giọt nước từ icon kéo dài xuống, biến dạng hữu cơ rồi nở bung thành hình panel chữ nhật.', hint: 'Biến thiên border-radius bất đối xứng tạo cảm giác hữu cơ mềm mại.' },
      { id: 'outline', title: 'Vẽ viền trước (Outline Trace)', desc: 'Một vệt sáng neon chạy vòng quanh viền bo góc trước, sau đó nền kính và nội dung hiện ra.', hint: 'Vẽ đường nét SVG stroke-dashoffset rồi làm đầy nội dung.' },
      { id: 'cascade', title: 'Thác đổ (Staggered Cascade)', desc: 'Mặt nền kính hiện lên, sau đó tiêu đề, thanh âm lượng và các ô nút lần lượt rơi vào vị trí.', hint: 'Mỗi thành phần con xuất hiện cách nhau 75ms (stagger delay).' },
      { id: 'slit', title: 'Khe sáng hẹp (Glowing Slit)', desc: 'Một khe sáng mảnh xuất hiện dưới thanh bar, rồi nở rộng xuống dưới thành panel.', hint: 'Đa giác polygon thu hẹp thành khe 1px rồi mở rộng toàn phần.' },
      { id: 'travel', title: 'Con nhộng di chuyển (Traveling Capsule)', desc: 'Panel thu gọn thành hình con nhộng, chạy ngang sang icon mới rồi bung mở trở lại.', hint: 'Thu nhỏ capsule -> dịch chuyển ngang -> mở rộng kích thước mới.', pages: true }
    ],
    pages: {
      settings: { title: "Cài đặt nhanh", subtitle: "ALPORA · Không gian làm việc", volume: "Âm lượng", brightness: "Độ sáng", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Đang bật", off: "Đang tắt", mode: "Chế độ làm việc", balance: "Cân bằng" },
      calendar: { title: "Lịch hôm nay", month: "Tháng 10 2026", footer: "Hôm nay là thời điểm tuyệt vời cho các dự định mới", days: ['T2','T3','T4','T5','T6','T7','CN'] },
      notifications: { title: "Thông báo", note1Title: "Chào mừng đến với ALPORA", note1Desc: "Hệ thống · vừa xong", note2Title: "Danh sách nhạc đã sẵn sàng", note2Desc: "Media · 5 phút trước", footer: "Lịch sử thông báo hệ thống" },
      timeline: { title: "Dòng thời gian (Timeline)", subtitle: "Từ bình minh đến đêm muộn" }
    }
  },
  en: {
    brand: "ALPORA / MOTION",
    badge: "INTERACTIVE LAB",
    title: "16 Panel Motion Studies",
    subtitle: "Explore, compare and fine-tune transition styles for Quick Settings, Calendar, and Notifications before porting to Quickshell.",
    playAll: "↻ Play All",
    closeAll: "Close All",
    speed: "Speed",
    theme: "Theme",
    mode: "Mode",
    workMode: "Work",
    vibeMode: "Vibe",
    open: "Open",
    close: "Close",
    repeat: "Replay",
    opened: "Opened",
    closed: "Closed",
    qmlCode: "QML Code",
    copyQml: "Copy QML",
    copied: "Copied!",
    backToHub: "← Back to ALPORA Demo Hub",
    footerHint: "Click any button on the mini-bar or study card to test · Press Escape to close all.",
    hintTitle: "Interaction hint:",
    studies: [
      { id: 'slide', title: 'Soft Slide', desc: 'Panel slides down smoothly from beneath the bar and eases to a stop. Closing slides it back.', hint: 'Vertical translation + opacity fade. Clean and distraction-free.' },
      { id: 'curtain', title: 'Curtain Drop', desc: 'Top edge anchored under the bar. The panel unfolds downward, revealing contents progressively.', hint: 'Height expansion with 14px rounded clip-path; text is not stretched.' },
      { id: 'origin', title: 'Origin Pop', desc: 'A compact shape directly beneath the clicked button morphs outward into the full window.', hint: 'Transform origin anchored directly to the clicked icon coordinates.' },
      { id: 'pop', title: 'Subtle Pop-in', desc: 'The panel expands gently from 94% to full scale with zero bounce or overshoot.', hint: 'Subtle scale-up + smooth opacity curve. Ideal for Work mode.' },
      { id: 'spring', title: 'Spring Bounce', desc: 'The panel slides down, slightly overshoots its resting mark, then springs gently back into place.', hint: 'Organic bounce simulation with subtle physical elasticity.' },
      { id: 'morph', title: 'Morph Switch', desc: 'The open window simultaneously animates position, dimensions, and contents when switching tabs.', hint: 'Switch between Clock, Timeline, Notifications, and Settings!', pages: true },
      { id: 'center', title: 'Center Expand', desc: 'A tiny center point grows into a thin horizontal bar, which then opens vertically.', hint: 'Two-phase transition: Width first -> Height second.' },
      { id: 'iris', title: 'Circular Iris', desc: 'A circular mask centered at the button expands outward, revealing the panel cleanly.', hint: 'Circle clip-path mask from 0% to 145% without text distortion.' },
      { id: 'depth', title: 'Depth Perspective', desc: 'Panel zooms forward from 3D background depth, tilts slightly, and snaps flush to the viewport.', hint: 'Perspective 800px with translateZ(-180px) and rotateX tilt.' },
      { id: 'hinge', title: 'Hinge Drop', desc: 'Panel swings down on a top hinge like an elegant mechanical lid.', hint: 'Rotates around the top edge from -88deg to 0deg.' },
      { id: 'fold', title: 'Origami Fold', desc: 'Upper half unfolds first, followed by the lower half swinging out like folded paper.', hint: 'Two discrete halves with independent hinge perspectives.' },
      { id: 'liquid', title: 'Liquid Droplet', desc: 'A droplet beneath the button stretches, becomes an organic bubble, then settles into a rectangle.', hint: 'Asymmetric border-radius deformation with smooth dampening.' },
      { id: 'outline', title: 'Outline Trace', desc: 'A crisp glowing outline traces the perimeter first, followed by surface fill and contents.', hint: 'SVG stroke-dashoffset perimeter animation then body fade-in.' },
      { id: 'cascade', title: 'Staggered Cascade', desc: 'Surface appears, then header, sliders, and toggle tiles animate into position one by one.', hint: 'Each child component enters with a 75ms sequential delay.' },
      { id: 'slit', title: 'Glowing Slit', desc: 'A luminous horizontal line widens under the bar, then expands downward into the full panel.', hint: 'Polygon slit expands from 1px slice into full bounding box.' },
      { id: 'travel', title: 'Traveling Capsule', desc: 'Panel collapses into a capsule, glides horizontally to the new button, and re-expands.', hint: 'Click different bar buttons: capsule travels between them.', pages: true }
    ],
    pages: {
      settings: { title: "Quick Settings", subtitle: "ALPORA · Your workspace", volume: "Volume", brightness: "Brightness", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Connected", off: "Off", mode: "Work Mode", balance: "Balanced" },
      calendar: { title: "My Day", month: "October 2026", footer: "Today is a great day for deep focus", days: ['MO','TU','WE','TH','FR','SA','SU'] },
      notifications: { title: "Notifications", note1Title: "Welcome to ALPORA", note1Desc: "System · Just now", note2Title: "Your playlist is ready", note2Desc: "Media · 5m ago", footer: "System notification history" },
      timeline: { title: "Timeline", subtitle: "From sunrise to starlight" }
    }
  },
  ru: {
    brand: "POLY / MOTION",
    badge: "ЛОКАЛЬНАЯ ДЕМОНСТРАЦИЯ",
    title: "16 вариантов анимации панелей",
    subtitle: "Открывай, закрывай и сравнивай характер переходов для быстрых настроек, календаря и уведомлений.",
    playAll: "↻ Сравнить все",
    closeAll: "Закрыть все",
    speed: "Скорость",
    theme: "Мир",
    mode: "Режим",
    workMode: "Работа",
    vibeMode: "Вайб",
    open: "Открыть",
    close: "Закрыть",
    repeat: "Повторить",
    opened: "Открыто",
    closed: "Закрыто",
    qmlCode: "Код QML",
    copyQml: "Копировать",
    copied: "Скопировано!",
    backToHub: "← В хаб демонстраций ALPORA",
    footerHint: "Нажми на значок панели в мини-баре · Esc — закрыть все карточки.",
    hintTitle: "Подсказка:",
    studies: [
      { id: 'slide', title: 'Мягкий выезд', desc: 'Панель спускается из-под бара и плавно останавливается. Закрытие уводит её обратно.', hint: 'Движение вниз + прозрачность.' },
      { id: 'curtain', title: 'Шторка', desc: 'Верхний край закреплён под баром. Панель раскрывается вниз, постепенно открывая содержимое.', hint: 'Раскрытие по высоте · текст не растягивается.' },
      { id: 'origin', title: 'Из кнопки в панель', desc: 'Маленькая форма возле иконки разворачивается в окно. Содержимое появляется после раскрытия.', hint: 'Превращение формы от нажатой кнопки.' },
      { id: 'pop', title: 'Мягкий pop-in', desc: 'Панель чуть увеличивается до полного размера. Спокойное движение без отскока.', hint: 'Лёгкое увеличение + прозрачность.' },
      { id: 'spring', title: 'Лёгкая пружина', desc: 'Панель выезжает, слегка проходит точку остановки и мягко возвращается на место.', hint: 'Один небольшой отскок с физической отдачей.' },
      { id: 'morph', title: 'Плавное превращение', desc: 'Открытое окно одновременно меняет положение, размер и содержимое при выборе другой кнопки.', hint: 'Переключай часы, солнце, колокольчик и настройки!', pages: true },
      { id: 'center', title: 'Раскрытие от центра', desc: 'Из маленькой точки вырастает тонкая горизонтальная полоска. Затем панель раскрывается вверх и вниз.', hint: 'Две фазы: ширина → высота.' },
      { id: 'iris', title: 'Диафрагма', desc: 'Из точки под кнопкой расширяется круг. Он постепенно открывает всю панель.', hint: 'Круглая маска от иконки · без искажения текста.' },
      { id: 'depth', title: 'Карточка из глубины', desc: 'Панель приближается из глубины, немного поворачивается и мягко становится плоской.', hint: 'Перспектива + приближение + выравнивание.' },
      { id: 'hinge', title: 'Откидная панель', desc: 'Панель висит на верхнем шарнире и опускается из-под бара, как лёгкая крышка.', hint: 'Поворот вокруг верхнего края на 88°.' },
      { id: 'fold', title: 'Складка', desc: 'Сначала разворачивается верхняя половина, затем из неё выходит нижняя. Как сложенный лист.', hint: 'Две отдельные половины с собственными шарнирами.' },
      { id: 'liquid', title: 'Жидкое превращение', desc: 'Капля под иконкой вытягивается, становится мягким пузырём и принимает форму панели.', hint: 'Асимметричная форма + растяжение + мягкое оседание.' },
      { id: 'outline', title: 'Контур → содержимое', desc: 'Светлая линия обходит рамку. Следом появляется поверхность и наполняется содержимым.', hint: 'Реальная прорисовка контура, затем заполнение.' },
      { id: 'cascade', title: 'Каскад элементов', desc: 'Появляется поверхность, затем заголовок, ползунки и плитки последовательно занимают свои места.', hint: 'У каждого элемента своя небольшая задержка.' },
      { id: 'slit', title: 'Из тонкой щели', desc: 'Под баром растёт узкая светлая линия. Она раскрывается вниз в полноценную панель.', hint: 'Горизонтальная щель → раскрытие вниз.' },
      { id: 'travel', title: 'Движущийся контейнер', desc: 'Панель сворачивается в компактную капсулу, переезжает к другой кнопке и раскрывается заново.', hint: 'Нажимай разные кнопки — капсула перемещается между ними.', pages: true }
    ],
    pages: {
      settings: { title: "Быстрые настройки", subtitle: "Alpine · Твоё пространство", volume: "Громкость", brightness: "Яркость", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Включён", off: "Выключен", mode: "Рабочий режим", balance: "Баланс" },
      calendar: { title: "Мой день", month: "Октябрь 2026", footer: "Сегодня — время для своих планов", days: ['ПН','ВТ','СР','ЧТ','ПТ','СБ','ВС'] },
      notifications: { title: "Уведомления", note1Title: "Добро пожаловать в Alpine", note1Desc: "Система · только что", note2Title: "Твой плейлист готов", note2Desc: "Музыка · 5 минут назад", footer: "Демонстрационные уведомления" },
      timeline: { title: "Timeline", subtitle: "От рассвета до ночной долины" }
    }
  }
};

const THEMES = {
  alpine: {
    name: "Alpine Dawn",
    wallpaper: "../../assets/wallpapers/alpine-dawn.png",
    bg: "#101a1b",
    surface: "#182526",
    line: "#344441",
    ink: "#ecf0e7",
    muted: "#9baea6",
    accent: "#c0d3ae",
    secondary: "#f1b791"
  },
  "moon-lake": {
    name: "Moon Lake",
    wallpaper: "../../assets/wallpapers/moon-lake.png",
    bg: "#101625",
    surface: "#1a253b",
    line: "#374762",
    ink: "#edf0f6",
    muted: "#a8b5c9",
    accent: "#b2a5f2",
    secondary: "#a9caf6"
  },
  "forest-mist": {
    name: "Forest Mist",
    wallpaper: "../../assets/wallpapers/forest-mist.png",
    bg: "#101f20",
    surface: "#1c3230",
    line: "#345550",
    ink: "#ecf3ef",
    muted: "#9bb5ab",
    accent: "#a9c8ba",
    secondary: "#dfd7bb"
  },
  "northern-lights": {
    name: "Northern Lights",
    wallpaper: "../../assets/wallpapers/northern-lights.png",
    bg: "#0d1b22",
    surface: "#172c38",
    line: "#2f5367",
    ink: "#edf3f6",
    muted: "#97b8c7",
    accent: "#7bd3cd",
    secondary: "#bca4f0"
  },
  "warm-desert": {
    name: "Warm Desert",
    wallpaper: "../../assets/wallpapers/warm-desert.png",
    bg: "#221714",
    surface: "#35231c",
    line: "#5c3d31",
    ink: "#faede8",
    muted: "#cbb1a5",
    accent: "#efba87",
    secondary: "#df9274"
  },
  "rose-sunset": {
    name: "Rose Sunset",
    wallpaper: "../../assets/wallpapers/rose-sunset.png",
    bg: "#1e1724",
    surface: "#2f2237",
    line: "#533b5f",
    ink: "#f7edf3",
    muted: "#c5adc0",
    accent: "#e5a9c4",
    secondary: "#efb89e"
  },
  timeline: {
    name: "Timeline Day",
    wallpaper: "../../assets/wallpapers/timeline/day.png",
    bg: "#141c21",
    surface: "#222c32",
    line: "#3c4d57",
    ink: "#edf2f4",
    muted: "#a9bac5",
    accent: "#c7c5a6",
    secondary: "#edb297"
  }
};

let currentLang = localStorage.getItem('alpora_demo_lang') || 'vi';
let currentTheme = localStorage.getItem('alpora_demo_theme') || 'alpine';
let speed = 1;
const controllers = [];

const svg = name => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><use href="#${name}"/></svg>`;
const closeButton = '<button class="close" data-close aria-label="Close">×</button>';

function applyTheme(themeKey) {
  const t = THEMES[themeKey] || THEMES.alpine;
  currentTheme = themeKey;
  localStorage.setItem('alpora_demo_theme', themeKey);
  const root = document.documentElement;
  root.style.setProperty('--bg', t.bg);
  root.style.setProperty('--surface', t.surface);
  root.style.setProperty('--line', t.line);
  root.style.setProperty('--ink', t.ink);
  root.style.setProperty('--muted', t.muted);
  root.style.setProperty('--accent', t.accent);
  root.style.setProperty('--secondary', t.secondary);
  root.style.setProperty('--wallpaper', `url('${t.wallpaper}')`);

  document.querySelectorAll('[data-theme-key]').forEach(b => {
    b.setAttribute('aria-pressed', String(b.dataset.themeKey === themeKey));
  });
}

function renderContent(page, langKey) {
  const p = I18N[langKey].pages[page] || I18N[langKey].pages.settings;
  if (page === 'calendar') {
    return `
      <div class="panel-heading">${svg('mountain')} ${p.title} ${closeButton}</div>
      <div class="calendar-top"><span>‹</span><span>${p.month}</span><span>›</span></div>
      <div class="calendar-grid">
        ${p.days.map(d => `<span class="weekday">${d}</span>`).join('')}
        ${Array.from({ length: 28 }, (_, i) => `<span class="${i === 19 ? 'today' : ''}">${i + 1}</span>`).join('')}
      </div>
      <div class="panel-bottom"><span>${p.footer}</span></div>
    `;
  }
  if (page === 'notifications') {
    return `
      <div class="panel-heading">${svg('bell')} ${p.title} ${closeButton}</div>
      <div class="notice"><strong>${p.note1Title}</strong><small>${p.note1Desc}</small></div>
      <div class="notice"><strong>${p.note2Title}</strong><small>${p.note2Desc}</small></div>
      <div class="panel-bottom"><span>${p.footer}</span></div>
    `;
  }
  if (page === 'timeline') {
    return `
      <div class="panel-heading">${svg('sun')} ${p.title} <span style="margin-left:auto;color:var(--accent)">14:20</span>${closeButton}</div>
      <div class="panel-subtitle">${p.subtitle}</div>
      <div class="timeline-range"></div>
      <div class="timeline-hours"><span>00:00</span><span>06:00</span><span>12:00</span><span>18:00</span><span>24:00</span></div>
    `;
  }
  return `
    <div class="panel-heading">${svg('mountain')} ${p.title} ${closeButton}</div>
    <div class="panel-subtitle">${p.subtitle}</div>
    <div class="audio">
      ${svg('volume')}
      <input type="range" min="0" max="100" value="68" aria-label="${p.volume}">
      <output>68%</output>
    </div>
    <div class="audio">
      ${svg('sun')}
      <input type="range" min="0" max="100" value="85" aria-label="${p.brightness}">
      <output>85%</output>
    </div>
    <div class="tiles">
      <button class="tile" data-toggle aria-pressed="true">
        ${svg('wifi')}
        <span>${p.wifi}<small>${p.on}</small></span>
      </button>
      <button class="tile off" data-toggle aria-pressed="false">
        ${svg('bluetooth')}
        <span>${p.bluetooth}<small>${p.off}</small></span>
      </button>
    </div>
    <div class="panel-bottom">
      <span>${p.mode}</span>
      <span class="mini-tag">${p.balance}</span>
    </div>
  `;
}

function cardHTML(item, index, langKey) {
  const t = I18N[langKey];
  return `
    <article class="study" id="study-${item.id}" data-study="${item.id}">
      <div class="study-head">
        <span class="number">${String(index + 1).padStart(2, '0')}</span>
        <div>
          <h2>${item.title} ${index >= 6 ? '<span class="new-tag">STUDY</span>' : ''}</h2>
          <p class="study-desc">${item.desc}</p>
        </div>
      </div>
      <div class="desktop">
        <div class="mini-bar">
          ${svg('mountain')}
          <div class="workspaces">
            <span class="workspace active">1</span>
            <span class="workspace">2</span>
            <span class="workspace">3</span>
            <span class="workspace">4</span>
          </div>
          <div class="mini-time">
            ${item.pages ? '<button data-page="calendar" aria-label="Calendar">14:20</button>' : '14:20'}
          </div>
          <div class="bar-actions">
            ${item.pages ? `
              <button data-page="timeline" aria-label="Timeline">${svg('sun')}</button>
              <button data-page="notifications" aria-label="Notifications">${svg('bell')}</button>
            ` : svg('wifi')}
            <button data-page="settings" aria-label="Open settings" aria-expanded="false">${svg('settings')}</button>
          </div>
        </div>
        <div class="desktop-clock">
          <strong>14:20</strong>
          <span>ALPORA DESKTOP</span>
        </div>
        <span class="demo-label">ALPORA · ${item.id.toUpperCase()}</span>
        <div class="panel" role="region" aria-label="Preview: ${item.title}" aria-hidden="true" inert>
          <div class="panel-content">${renderContent('settings', langKey)}</div>
        </div>
      </div>
      <div class="study-footer">
        <button class="toggle primary">${t.open}</button>
        <span class="state">${t.closed}</span>
        <button class="repeat">${svg('repeat')} ${t.repeat}</button>
        <button class="copy-qml" data-qml-id="${item.id}">${svg('code')} ${t.qmlCode}</button>
      </div>
      <div class="hint-line">${item.hint}</div>
    </article>
  `;
}

const identity = 'translate(0px, 0px) scale(1)';
const closed = {
  slide: { transform: 'translateY(-26px)', opacity: 0 },
  curtain: { clipPath: 'inset(0 0 100% 0 round 14px)', transform: 'translateY(-5px)', opacity: 1 },
  origin: { transform: 'translateY(-26px) scale(0.065, 0.10)', borderRadius: '45px', opacity: 0 },
  pop: { transform: 'translateY(-5px) scale(.94)', opacity: 0 },
  spring: { transform: 'translateY(-32px)', opacity: 0 },
  morph: { transform: 'translateY(-12px) scale(.98)', opacity: 0 },
  center: { clipPath: 'inset(49.5% 49.5% 49.5% 49.5% round 14px)', opacity: 1 },
  iris: { clipPath: 'circle(0% at calc(100% - 17px) 0%)', opacity: 1 },
  depth: { transform: 'perspective(800px) translateZ(-180px) translateY(-25px) rotateX(22deg)', opacity: 0 },
  hinge: { transform: 'perspective(750px) rotateX(-88deg)', opacity: 0 },
  fold: { opacity: 0 },
  liquid: { transform: 'translateY(-27px) scale(.09,.14)', borderRadius: '70% 30% 65% 35% / 45% 70% 30% 55%', opacity: 0 },
  outline: { opacity: 0 },
  cascade: { opacity: 0 },
  slit: { clipPath: 'polygon(44% 0%,56% 0%,56% 1%,44% 1%)', opacity: 1 },
  travel: { transform: 'translateY(-12px) scale(.98)', opacity: 0 }
};

const final = { transform: identity, opacity: 1, clipPath: 'inset(0 0 0% 0 round 14px)', borderRadius: '14px' };
function endStyle(id) {
  return {
    ...final,
    ...(id === 'iris' ? { clipPath: 'circle(145% at calc(100% - 17px) 0%)' } : id === 'slit' ? { clipPath: 'polygon(0% 0%,100% 0%,100% 100%,0% 100%)' } : {})
  };
}

const ease = 'cubic-bezier(.2,.8,.2,1)';

class Demo {
  constructor(element, config) {
    this.el = element;
    this.config = config;
    this.canvas = element.querySelector('.desktop');
    this.panel = element.querySelector('.panel');
    this.body = element.querySelector('.panel-content');
    this.open = false;
    this.page = 'settings';
    this.pending = [];
    this.token = 0;
    this.layout();
    if (['center', 'depth', 'hinge', 'fold', 'cascade', 'slit'].includes(config.id)) {
      this.panel.style.transformOrigin = '50% 0%';
    }
    Object.assign(this.panel.style, endStyle(config.id), closed[config.id]);

    this.el.querySelector('.toggle').onclick = () => {
      this.autoPlayed = true;
      this.setOpen(!this.open);
    };
    this.el.querySelector('.repeat').onclick = () => this.replay();
    this.el.querySelectorAll('[data-page]').forEach(b => b.onclick = () => {
      this.autoPlayed = true;
      const page = b.dataset.page;
      if (this.config.pages && this.open && page !== this.page) {
        this.changePage(page);
      } else {
        if (this.config.pages) this.changePage(page, false);
        this.setOpen(!this.open);
      }
    });
    this.canvas.addEventListener('click', e => {
      if (e.target.closest('[data-close]')) this.setOpen(false);
      else if (!e.target.closest('.panel,.mini-bar')) this.setOpen(false);
      const toggle = e.target.closest('[data-toggle]');
      if (toggle) {
        const enabled = toggle.getAttribute('aria-pressed') !== 'true';
        toggle.setAttribute('aria-pressed', String(enabled));
        toggle.classList.toggle('off', !enabled);
        const t = I18N[currentLang].pages.settings;
        toggle.querySelector('small').textContent = enabled ? t.on : t.off;
      }
    });
    this.body.addEventListener('input', e => {
      if (e.target.matches('input[type=range]')) {
        e.target.nextElementSibling.value = e.target.value + '%';
      }
    });
  }

  cleanup() {
    this.panel.querySelectorAll('.motion-extra').forEach(el => el.remove());
    this.panel.classList.remove('folding', 'outlining', 'animating');
    for (const child of this.body.children) {
      child.style.removeProperty('opacity');
      child.style.removeProperty('transform');
    }
    this.body.style.opacity = '1';
  }

  stop() {
    this.pending.forEach(clearTimeout);
    this.pending = [];
    for (const a of this.panel.getAnimations({ subtree: true })) {
      try { a.commitStyles(); } catch {}
      a.cancel();
    }
    this.cleanup();
    this.token++;
  }

  layout() {
    const dimensions = { settings: [290, 240], calendar: [330, 250], notifications: [290, 240], timeline: [290, 160] };
    const [desiredWidth, height] = this.config.pages ? dimensions[this.page] : dimensions.settings;
    const width = Math.min(desiredWidth, this.canvas.clientWidth - 28);
    let left = this.canvas.clientWidth - width - 15;
    if (this.config.pages) {
      const source = this.el.querySelector(`[data-page="${this.page}"]`);
      if (source) {
        const r = source.getBoundingClientRect(), c = this.canvas.getBoundingClientRect();
        left = Math.max(14, Math.min(this.canvas.clientWidth - width - 14, r.left - c.left + r.width / 2 - width / 2));
      }
    }
    this.panel.style.right = 'auto';
    Object.assign(this.panel.style, { left: left + 'px', width: width + 'px', height: height + 'px' });
  }

  update() {
    const t = I18N[currentLang];
    this.el.querySelector('.toggle').textContent = this.open ? t.close : t.open;
    const status = this.el.querySelector('.state');
    status.textContent = this.open ? t.opened : t.closed;
    status.classList.toggle('open', this.open);
    this.panel.setAttribute('aria-hidden', String(!this.open));
    this.panel.inert = !this.open;
    this.el.querySelectorAll('[data-page]').forEach(b => {
      const selected = this.open && (!this.config.pages || b.dataset.page === this.page);
      b.classList.toggle('selected', selected);
      b.setAttribute('aria-expanded', String(selected));
    });
  }

  play(target, frames, options) {
    const a = target.animate(frames, { fill: 'forwards', ...options });
    a.finished.catch(() => {});
    return a;
  }

  fold(value, duration) {
    this.panel.classList.add('folding');
    for (const [index, name] of ['upper', 'lower'].entries()) {
      const half = document.createElement('div');
      half.className = `fold-piece ${name} motion-extra`;
      half.setAttribute('aria-hidden', 'true');
      half.inert = true;
      const face = document.createElement('div');
      face.className = 'fold-face';
      face.style.height = this.panel.offsetHeight + 'px';
      if (index) face.style.top = -this.panel.offsetHeight / 2 + 'px';
      face.innerHTML = this.body.outerHTML;
      half.append(face);
      this.panel.append(half);
      const rotated = `perspective(750px) rotateX(${index ? 125 : -85}deg)`;
      this.play(half, value
        ? [{ transform: rotated, opacity: .4 }, { transform: 'perspective(750px) rotateX(0deg)', opacity: 1 }]
        : [{ transform: 'perspective(750px) rotateX(0deg)', opacity: 1 }, { transform: rotated, opacity: .2 }],
        { duration: duration * .72, delay: value ? (index ? duration * .27 : 0) : (index ? 0 : duration * .27), easing: ease });
    }
  }

  outline(value, duration) {
    this.panel.classList.add('outlining');
    const fill = document.createElement('div');
    fill.className = 'outline-fill motion-extra';
    this.panel.append(fill);
    this.play(fill, value
      ? [{ opacity: 0, offset: 0 }, { opacity: 0, offset: .45 }, { opacity: 1, offset: .82 }, { opacity: 1 }]
      : [{ opacity: 1 }, { opacity: 0, offset: .4 }, { opacity: 0 }],
      { duration, easing: 'linear' });
    const ns = 'http://www.w3.org/2000/svg';
    const drawing = document.createElementNS(ns, 'svg');
    drawing.classList.add('outline-trace', 'motion-extra');
    drawing.setAttribute('viewBox', `0 0 ${this.panel.offsetWidth} ${this.panel.offsetHeight}`);
    drawing.setAttribute('aria-hidden', 'true');
    const rect = document.createElementNS(ns, 'rect');
    for (const [key, v] of Object.entries({ x: 1, y: 1, width: this.panel.offsetWidth - 2, height: this.panel.offsetHeight - 2, rx: 14, pathLength: 1 })) {
      rect.setAttribute(key, v);
    }
    drawing.append(rect);
    this.panel.append(drawing);
    this.play(rect, value
      ? [{ strokeDashoffset: 1 }, { strokeDashoffset: 0 }]
      : [{ strokeDashoffset: 0 }, { strokeDashoffset: 1 }],
      { duration: duration * .72, delay: value ? 0 : duration * .26, easing: 'ease-in-out' });
    this.play(this.body, value
      ? [{ opacity: 0 }, { opacity: 1 }]
      : [{ opacity: 1 }, { opacity: 0 }],
      { duration: duration * .45, delay: value ? duration * .53 : 0, easing: ease });
  }

  cascade(value, duration) {
    const children = [...this.body.children];
    children.forEach((child, index) => {
      this.play(child, value
        ? [{ opacity: 0, transform: 'translateY(15px)' }, { opacity: 1, transform: 'translateY(0px)' }]
        : [{ opacity: 1, transform: 'translateY(0px)' }, { opacity: 0, transform: 'translateY(-9px)' }],
        { duration: duration * .46, delay: (value ? index : children.length - index - 1) * duration * .075, easing: ease });
    });
  }

  setOpen(value, { instant = false } = {}) {
    const wasMoving = this.panel.getAnimations().some(a => a.playState === 'running');
    this.stop();
    this.open = value;
    this.update();
    const opened = endStyle(this.config.id);
    const end = value ? opened : { ...opened, ...closed[this.config.id] };
    if (instant) {
      Object.assign(this.panel.style, end);
      this.panel.style.visibility = value ? 'visible' : 'hidden';
      return;
    }
    this.panel.style.visibility = 'visible';
    this.panel.classList.add('animating');
    const computed = getComputedStyle(this.panel);
    const start = { transform: computed.transform, opacity: computed.opacity, clipPath: computed.clipPath, borderRadius: computed.borderRadius };
    let frames = [start, end];
    const id = this.config.id;

    if (value && !wasMoving) {
      if (id === 'spring') frames = [{ ...closed.spring, offset: 0 }, { transform: 'translateY(7px)', opacity: 1, offset: .57 }, { transform: 'translateY(-2px)', opacity: 1, offset: .79 }, { ...opened, offset: 1 }];
      if (id === 'center') frames = [{ ...opened, ...closed.center, offset: 0 }, { ...opened, clipPath: 'inset(49.5% 0% 49.5% 0% round 14px)', offset: .38 }, { ...opened, offset: 1 }];
      if (id === 'slit') frames = [{ ...opened, ...closed.slit, offset: 0 }, { ...opened, clipPath: 'polygon(0% 0%,100% 0%,100% 1%,0% 1%)', offset: .38 }, { ...opened, offset: 1 }];
      if (id === 'liquid') frames = [{ ...opened, ...closed.liquid, offset: 0 }, { transform: 'translateY(-12px) scale(.48,.65)', borderRadius: '58% 42% 35% 65% / 65% 40% 60% 35%', opacity: 1, offset: .36 }, { transform: 'translateY(3px) scale(1.025,.97)', borderRadius: '25px 20px 32px 18px', opacity: 1, offset: .74 }, { ...opened, offset: 1 }];
      if (['fold', 'outline'].includes(id)) frames = [{ ...opened, opacity: 0, offset: 0 }, { ...opened, opacity: 1, offset: .08 }, { ...opened, offset: 1 }];
      if (id === 'cascade') frames = [{ ...opened, opacity: 0, offset: 0 }, { ...opened, opacity: 1, offset: .22 }, { ...opened, offset: 1 }];
    }
    const duration = (this.config.duration || 540) * (value ? 1 : .8) / speed;
    const animation = this.play(this.panel, frames, { duration, easing: ['spring', 'center', 'liquid', 'slit'].includes(id) ? 'linear' : ease });

    if (['origin', 'liquid'].includes(id)) {
      this.play(this.body, value
        ? [{ opacity: 0, offset: 0 }, { opacity: 0, offset: .42 }, { opacity: 1, offset: .86 }, { opacity: 1 }]
        : [{ opacity: 1 }, { opacity: 0, offset: .4 }, { opacity: 0 }],
        { duration, easing: 'linear' });
    }
    if (id === 'fold') this.fold(value, duration);
    if (id === 'outline') this.outline(value, duration);
    if (id === 'cascade') this.cascade(value, duration);

    const token = this.token;
    animation.finished.then(() => {
      if (token !== this.token) return;
      for (const a of this.panel.getAnimations({ subtree: true })) a.cancel();
      Object.assign(this.panel.style, end);
      this.cleanup();
      if (!this.open) this.panel.style.visibility = 'hidden';
    }).catch(() => {});
  }

  replay() {
    this.autoPlayed = true;
    this.setOpen(false, { instant: true });
    this.pending.push(setTimeout(() => this.setOpen(true), 90));
  }

  changePage(page, animate = true) {
    if (page === this.page) return;
    this.stop();
    const previous = { left: this.panel.offsetLeft, width: this.panel.offsetWidth, height: this.panel.offsetHeight };
    this.page = page;
    this.body.innerHTML = renderContent(page, currentLang);
    this.layout();
    this.update();
    if (animate && this.open) {
      const next = { left: this.panel.style.left, width: this.panel.style.width, height: this.panel.style.height };
      const old = { left: previous.left + 'px', width: previous.width + 'px', height: previous.height + 'px' };
      let frames = [old, next];
      if (this.config.id === 'travel') {
        const capsuleLeft = Math.max(14, Math.min(this.canvas.clientWidth - 134, previous.left + previous.width / 2 - 60));
        const targetLeft = Math.max(14, Math.min(this.canvas.clientWidth - 134, this.panel.offsetLeft + this.panel.offsetWidth / 2 - 60));
        frames = [
          { ...old, borderRadius: '14px', offset: 0 },
          { left: capsuleLeft + 'px', width: '120px', height: '34px', borderRadius: '18px', offset: .28 },
          { left: targetLeft + 'px', width: '120px', height: '34px', borderRadius: '18px', offset: .64 },
          { ...next, borderRadius: '14px', offset: 1 }
        ];
      }
      const duration = (this.config.id === 'travel' ? 1000 : 580) / speed;
      const animation = this.play(this.panel, frames, { duration, easing: ease });
      this.play(this.body, this.config.id === 'travel'
        ? [{ opacity: 0, offset: 0 }, { opacity: 0, offset: .64 }, { opacity: 1, offset: 1 }]
        : [{ opacity: 0 }, { opacity: 1 }],
        { duration, easing: 'linear' });
      const token = this.token;
      animation.finished.then(() => {
        if (token !== this.token) return;
        for (const a of this.panel.getAnimations({ subtree: true })) a.cancel();
        Object.assign(this.panel.style, next);
        this.cleanup();
      }).catch(() => {});
    }
  }
}

function initPage() {
  const t = I18N[currentLang];
  document.documentElement.lang = currentLang;

  // Header & Brand
  document.querySelector('#brand-title').textContent = t.brand;
  document.querySelector('#brand-badge').textContent = t.badge;
  document.querySelector('#hero-title').textContent = t.title;
  document.querySelector('#hero-subtitle').textContent = t.subtitle;
  document.querySelector('#play-all').textContent = t.playAll;
  document.querySelector('#close-all').textContent = t.closeAll;
  document.querySelector('#speed-label').textContent = t.speed;
  document.querySelector('#theme-label').textContent = t.theme;
  document.querySelector('#footer-hint').textContent = t.footerHint;
  document.querySelector('#back-link').textContent = t.backToHub;

  // Render cards
  const studiesContainer = document.querySelector('#studies');
  const catalogContainer = document.querySelector('#catalog');
  controllers.length = 0;

  studiesContainer.innerHTML = t.studies.map((item, i) => cardHTML(item, i, currentLang)).join('');
  catalogContainer.innerHTML = t.studies.map((item, i) => `
    <a href="#study-${item.id}">
      <span>${String(i + 1).padStart(2, '0')}</span> ${item.title}
    </a>
  `).join('');

  document.querySelectorAll('.study').forEach((el, i) => {
    controllers.push(new Demo(el, t.studies[i]));
  });

  // Wire QML snippets
  document.querySelectorAll('.copy-qml').forEach(btn => {
    btn.onclick = () => {
      const qmlId = btn.dataset.qmlId;
      const snippet = `// Quickshell QML PanelMotion definition for "${qmlId}"
NumberAnimation on progress {
    duration: Session.motionMs > 0 ? ${qmlId === 'spring' ? 720 : 540} : 0
    easing.type: ${qmlId === 'spring' ? 'Easing.OutBack' : 'Easing.OutCubic'}
}`;
      navigator.clipboard.writeText(snippet).then(() => {
        const orig = btn.innerHTML;
        btn.innerHTML = `${svg('code')} ${t.copied}`;
        setTimeout(() => btn.innerHTML = orig, 1800);
      });
    };
  });

  applyTheme(currentTheme);
}

// Global Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  initPage();

  // Language buttons
  document.querySelectorAll('[data-lang]').forEach(btn => {
    btn.onclick = () => {
      currentLang = btn.dataset.lang;
      localStorage.setItem('alpora_demo_lang', currentLang);
      document.querySelectorAll('[data-lang]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
      initPage();
    };
  });

  // Speed buttons
  document.querySelectorAll('[data-speed]').forEach(btn => {
    btn.onclick = () => {
      speed = Number(btn.dataset.speed);
      document.querySelectorAll('[data-speed]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    };
  });

  // Theme swatches
  document.querySelectorAll('[data-theme-key]').forEach(btn => {
    btn.onclick = () => applyTheme(btn.dataset.themeKey);
  });

  document.querySelector('#play-all').onclick = () => {
    controllers.forEach(c => c.replay());
  };

  document.querySelector('#close-all').onclick = () => {
    controllers.forEach(c => {
      c.autoPlayed = true;
      c.setOpen(false);
    });
  };

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      controllers.forEach(c => {
        c.autoPlayed = true;
        c.setOpen(false);
      });
      document.querySelector('#play-all').focus();
    }
  });

  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      controllers.forEach(c => {
        c.stop();
        c.layout();
        c.setOpen(c.open, { instant: true });
      });
    }, 120);
  });

  document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
      controllers.forEach(c => c.setOpen(c.open, { instant: true }));
    }
  });

  if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) {
        if (!entry.isIntersecting) continue;
        const c = controllers.find(item => item.el === entry.target);
        if (c) {
          observer.unobserve(entry.target);
          if (!c.autoPlayed) {
            c.autoPlayed = true;
            c.pending.push(setTimeout(() => c.setOpen(true), 250));
          }
        }
      }
    }, { threshold: 0.3 });
    controllers.forEach(c => observer.observe(c.el));
  }
});
