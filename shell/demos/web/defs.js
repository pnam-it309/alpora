/**
 * ALPORA Unified Interactive Shell & Motion Sandbox
 * Definition Constants: Study animations, i18n dictionaries, and theme palettes.
 */

'use strict';

const STUDY_DEFS = [
  { id: 'slide', title: { vi: "Trượt mềm (Soft Slide)", en: "Soft Slide", ru: "Мягкий выезд" }, desc: { vi: "Panel trượt xuống êm ái từ mép dưới của TopBar rồi dừng nhẹ nhàng. Khi đóng trượt ngược lên.", en: "Panel slides down smoothly from beneath the bar and eases to a stop. Closing slides it back.", ru: "Панель спускается из-под бара и плавно останавливается. Закрытие уводит её обратно." }, hint: { vi: "Dịch chuyển trục Y + mờ dần (opacity). Chuẩn mặc định cho desktop.", en: "Vertical translation + opacity fade. Clean and distraction-free.", ru: "Движение вниз + прозрачность." } },
  { id: 'curtain', title: { vi: "Kéo rèm (Curtain Drop)", en: "Curtain Drop", ru: "Шторка" }, desc: { vi: "Mép trên cố định dưới TopBar. Panel mở dần xuống dưới như tấm rèm buông nhẹ.", en: "Top edge anchored under the bar. The panel unfolds downward, revealing contents progressively.", ru: "Верхний край закреплён под баром. Панель раскрывается вниз, постепенно открывая содержимое." }, hint: { vi: "Mở rộng chiều cao với clip-path bo tròn 14px; văn bản không bị kéo giãn.", en: "Height expansion with 14px rounded clip-path; text is not stretched.", ru: "Раскрытие по высоте · текст не растягивается." } },
  { id: 'origin', title: { vi: "Phóng từ icon (Origin Pop)", en: "Origin Pop", ru: "Из кнопки в панель" }, desc: { vi: "Từ vị trí icon được nhấn trên TopBar, một khối nhỏ bung nở thành cửa sổ hoàn chỉnh.", en: "A compact shape directly beneath the clicked button morphs outward into the full window.", ru: "Маленькая форма возле иконки разворачивается в окно. Содержимое появляется после раскрытия." }, hint: { vi: "Tâm biến đổi (transform-origin) gắn chặt với tọa độ icon bấm.", en: "Transform origin anchored directly to the clicked icon coordinates.", ru: "Превращение формы от нажатой кнопки." } },
  { id: 'pop', title: { vi: "Nảy nhẹ (Subtle Pop-in)", en: "Subtle Pop-in", ru: "Мягкий pop-in" }, desc: { vi: "Panel xuất hiện với độ phóng to 94% -> 100% kèm tăng dần độ trong suốt, không rung lắc.", en: "The panel expands gently from 94% to full scale with zero bounce or overshoot.", ru: "Панель чуть увеличивается до полного размера. Спокойное движение без отскока." }, hint: { vi: "Tăng nhẹ kích thước + mượt mà. Rất phù hợp với chế độ Work tối giản.", en: "Subtle scale-up + smooth opacity curve. Ideal for Work mode.", ru: "Лёгкое увеличение + прозрачность." } },
  { id: 'spring', title: { vi: "Độ nảy lò xo (Spring Bounce)", en: "Spring Bounce", ru: "Лёгкая пружина" }, desc: { vi: "Panel trượt xuống, vượt nhẹ qua điểm dừng một chút rồi bật khẽ trở lại vị trí cân bằng.", en: "The panel slides down, slightly overshoots its resting mark, then springs gently back into place.", ru: "Панель выезжает, слегка проходит точку остановки и мягко возвращается на место." }, hint: { vi: "Hiệu ứng lò xo tinh tế tạo cảm giác phản hồi vật lý sống động.", en: "Organic bounce simulation with subtle physical elasticity.", ru: "Один небольшой отскок с физической отдачей." } },
  { id: 'morph', title: { vi: "Biến đổi tab (Morph Switch)", en: "Morph Switch", ru: "Плавное превращение" }, desc: { vi: "Panel tự động co giãn kích thước, di chuyển vị trí và đổi nội dung mượt mà khi bấm tab khác.", en: "The open window simultaneously animates position, dimensions, and contents when switching tabs.", ru: "Открытое окно одновременно меняет положение, размер и содержимое при выборе другой кнопки." }, hint: { vi: "Thử chuyển qua lại giữa Đồng hồ, Lịch, Thông báo và Cài đặt!", en: "Switch between Clock, Timeline, Notifications, and Settings!", ru: "Переключай часы, календарь, уведомления и настройки." }, pages: true },
  { id: 'fade', title: { vi: "Mờ ảo tối giản (Pure Fade)", en: "Pure Fade", ru: "Только прозрачность" }, desc: { vi: "Panel giữ nguyên tọa độ, xuất hiện tức thì chỉ qua tăng giảm độ mờ 0% -> 100%.", en: "Zero motion, pure opacity fade. Ultra-clean for low-resource environments or minimalists.", ru: "Никакого движения. Только плавное появление и исчезновение через прозрачность." }, hint: { vi: "Chế độ không chuyển động (Reduced Motion), tốc độ tức thì 140ms.", en: "Respects Reduced Motion accessibility preference. 140ms duration.", ru: "Уважает настройки доступности без движения." } },
  { id: 'unfold', title: { vi: "Mở cánh 2 bên (Dual Unfold)", en: "Dual Unfold", ru: "Раскрытие крыльев" }, desc: { vi: "Cột giữa xuất hiện trước, hai bên cánh mở rộng sang trái và phải như cánh chim.", en: "Center core drops in first, then flanking cards unfold symmetrically to the left and right.", ru: "Центр появляется первым, затем боковые части симметрично раскрываются влево и вправо." }, hint: { vi: "Hiệu ứng phân lớp so le (staggered delay 40ms) tạo chiều sâu không gian.", en: "Staggered 40ms delay between core and wings creates natural spatial depth.", ru: "Каскадная задержка 40 мс между частями." } },
  { id: 'glass', title: { vi: "Kính khuếch tán (Frosted Bloom)", en: "Frosted Bloom", ru: "Размытие стекла" }, desc: { vi: "Mặt kính mờ ảo với bộ lọc blur tăng dần từ 0px -> 28px kết hợp viền sáng gradient.", en: "Backdrop blur animates smoothly from 0px to 28px while luminous edge gradient sweeps across.", ru: "Размытие фона плавно нарастает от 0 до 28px, подчеркивая стеклянную поверхность." }, hint: { vi: "Mô phỏng hiệu ứng Shader GLSL thời gian thực của Quickshell.", en: "Emulates the real-time GLSL fragment shader used in Poly Shell runtime.", ru: "Имитирует GLSL-шейдер размытия из настоящего шелла." } },
  { id: 'magnetic', title: { vi: "Lực hút nam châm (Magnetic Dock)", en: "Magnetic Dock", ru: "Магнитная панель" }, desc: { vi: "Khi kéo hoặc mở gần TopBar, panel tự động bắt dính vào mép với gia tốc hút vật lý.", en: "When released near the top bar, the panel accelerates and snaps cleanly to the boundary.", ru: "Панель плавно притягивается к краю бара, словно на магнитах." }, hint: { vi: "Mô phỏng vật lý kéo thả (drag & snap) cho các widget tùy biến.", en: "Physics-based magnetic snapping curve for floating modular widgets.", ru: "Магнитное прилипание к границе." } },
  { id: 'cascade', title: { vi: "Thác đổ tầng (Layer Cascade)", en: "Layer Cascade", ru: "Каскад слоёв" }, desc: { vi: "Khung nền xuất hiện trước, sau đó các thẻ bên trong lần lượt trượt vào theo bậc thang.", en: "Container appears first, then internal cards drop in sequentially like falling dominos.", ru: "Сначала появляется каркас, затем внутренние карточки падают друг за другом." }, hint: { vi: "Mỗi phần tử con có độ trễ 25ms, tạo nhịp điệu sinh động tự nhiên.", en: "Micro-stagger (25ms per item) brings complex data layouts to life.", ru: "Микрозадержка 25 мс для каждого элемента." } },
  { id: 'elastic', title: { vi: "Co giãn đàn hồi (Elastic Stretch)", en: "Elastic Stretch", ru: "Эластичное сжатие" }, desc: { vi: "Panel hơi dẹp lại theo chiều ngang và kéo dài theo chiều dọc khi di chuyển nhanh.", en: "Panel squashes slightly horizontally and stretches vertically while dropping into place.", ru: "Панель сжимается по горизонтали и вытягивается при быстром движении." }, hint: { vi: "Nguyên lý hoạt họa truyền thống (Squash & Stretch) ứng dụng vào UI hiện đại.", en: "Classic animation principle (Squash & Stretch) applied to system surfaces.", ru: "Принцип классической анимации: сжатие и растяжение." } },
  { id: 'flip', title: { vi: "Lật không gian 3D (Perspective Tilt)", en: "Perspective Tilt", ru: "3D-наклон" }, desc: { vi: "Panel lật nhẹ quanh trục X từ góc -8 độ về phẳng 0 độ trong không gian 3 chiều.", en: "Panel tilts around its X axis from -8deg down to 0deg with realistic 3D perspective.", ru: "Панель наклоняется по оси X от -8 градусов до нуля в трёхмерном пространстве." }, hint: { vi: "Hiệu ứng con quay hồi chuyển tạo chiều sâu góc nhìn công nghệ cao.", en: "Perspective projection (800px) creates clean architectural depth.", ru: "Перспектива 800px создает глубину." } },
  { id: 'ripple', title: { vi: "Gợn sóng tỏa (Circular Ripple)", en: "Circular Ripple", ru: "Круговая волна" }, desc: { vi: "Một vòng sóng tròn tỏa ra từ điểm click chuột, hé lộ giao diện từ trong ra ngoài.", en: "A circular wavefront expands outward from the cursor tap point, revealing the layout.", ru: "Круговая волна расходится от точки клика, раскрывая интерфейс изнутри наружу." }, hint: { vi: "Sử dụng kỹ thuật SVG clipPath hình tròn với bán kính tăng dần.", en: "SVG dynamic circular clip-path expanding at organic ease-out speed.", ru: "Круговая маска, расширяющаяся из точки нажатия." } },
  { id: 'orbit', title: { vi: "Quỹ đạo xoay (Orbit Reveal)", en: "Orbit Reveal", ru: "Орбитальное появление" }, desc: { vi: "Panel lướt vào theo một cung tròn mềm mại quanh tâm TopBar trước khi khóa vị trí.", en: "Panel sweeps in along a subtle radial arc path before settling into locked alignment.", ru: "Панель скользит по мягкой дуге вокруг центра верхнего бара." }, hint: { vi: "Quỹ đạo chuyển động theo đường cong Bezier kép độc quyền ALPORA.", en: "Dual-axis bezier curve simulates celestial orbital mechanics.", ru: "Движение по кривой орбите." } },
  { id: 'capsule', title: { vi: "Viên nhộng du hành (Capsule Transit)", en: "Capsule Transit", ru: "Транзит капсулы" }, desc: { vi: "Panel thu gọn thành hình con nhộng, chạy ngang sang icon mới rồi bung mở trở lại.", en: "Panel collapses into a capsule, glides horizontally to the new button, and re-expands.", ru: "Панель сворачивается в компактную капсулу, переезжает к другой кнопке и раскрывается заново." }, hint: { vi: "Thu nhỏ capsule -> dịch chuyển ngang -> mở rộng kích thước mới.", en: "Click different bar buttons: capsule travels between them.", ru: "Нажимай разные кнопки — капсула перемещается между ними." }, pages: true },
];

const I18N = {
  vi: {
    navShell: "Desktop Shell",
    navMotion: "Phòng thí nghiệm Motion (16 Studies)",
    navTypo: "Bộ Typography",
    brandTitle: "ALPORA · INTERACTIVE LAB",
    liveBackend: "● KẾT NỐI LIVE BACKEND",
    standalone: "● MÔ PHỎNG ĐỘC LẬP",
    lblTheme: "Chủ đề:",
    lblMode: "Chế độ:",
    workMode: "Làm việc",
    vibeMode: "Thư giãn",
    lblPower: "Hiệu năng",
    lblTypoTitle: "Bộ Typography Tiêu Chuẩn ALPORA",
    lblTypoDesc: "Được nạp trực tiếp qua FontLoader vào Quickshell và áp dụng đồng bộ cho toàn bộ hệ thống.",
    playAll: "↻ Chạy tất cả",
    closeAll: "Đóng tất cả",
    speed: "Tốc độ",
    open: "Mở",
    close: "Đóng",
    repeat: "Thử lại",
    opened: "Đang mở",
    closed: "Đã đóng",
    qmlCode: "Mã QML",
    copied: "Đã sao chép!",
    footerHint: "Nhấn chuột vào các nút trên thanh TopBar để thử nghiệm tương tác · Phím Esc để thoát.",
    days: ["Chủ Nhật", "Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy"],
    pages: {
      settings: { title: "Cài đặt nhanh", subtitle: "ALPORA · Không gian làm việc", volume: "Âm lượng", brightness: "Độ sáng", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Đang bật", off: "Đang tắt", mode: "Chế độ làm việc", balance: "Cân bằng" },
      calendar: { title: "Lịch hôm nay", month: "Tháng 10 2026", footer: "Hôm nay là thời điểm tuyệt vời cho các dự định mới", days: ['T2','T3','T4','T5','T6','T7','CN'] },
      notifications: { title: "Thông báo", note1Title: "Chào mừng đến với ALPORA", note1Desc: "Hệ thống · vừa xong", note2Title: "Danh sách nhạc đã sẵn sàng", note2Desc: "Media · 5 phút trước", footer: "Lịch sử thông báo hệ thống" },
      timeline: { title: "Dòng thời gian (Timeline)", subtitle: "Từ bình minh đến đêm muộn" }
    }
  },
  en: {
    navShell: "Desktop Shell",
    navMotion: "Motion Lab (16 Studies)",
    navTypo: "Typography",
    brandTitle: "ALPORA · INTERACTIVE LAB",
    liveBackend: "● LIVE BACKEND CONNECTED",
    standalone: "● STANDALONE SIMULATION",
    lblTheme: "Theme:",
    lblMode: "Mode:",
    workMode: "Work",
    vibeMode: "Vibe",
    lblPower: "Power Profile",
    lblTypoTitle: "ALPORA Typography Specification",
    lblTypoDesc: "Loaded directly via FontLoader into Quickshell and applied uniformly across the entire system.",
    playAll: "↻ Play All",
    closeAll: "Close All",
    speed: "Speed",
    open: "Open",
    close: "Close",
    repeat: "Replay",
    opened: "Open",
    closed: "Closed",
    qmlCode: "QML Source",
    copied: "Copied!",
    footerHint: "Click buttons on the TopBar to trigger panel reveals · Press Esc to dismiss.",
    days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    pages: {
      settings: { title: "Quick Settings", subtitle: "ALPORA · Workspace", volume: "Volume", brightness: "Brightness", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Enabled", off: "Disabled", mode: "Work Mode", balance: "Balanced" },
      calendar: { title: "Today", month: "October 2026", footer: "Great moment for focused creation", days: ['Mo','Tu','We','Th','Fr','Sa','Su'] },
      notifications: { title: "Notifications", note1Title: "Welcome to ALPORA", note1Desc: "System · just now", note2Title: "Playlist Ready", note2Desc: "Media · 5m ago", footer: "System Notification History" },
      timeline: { title: "Timeline", subtitle: "From dawn till midnight" }
    }
  },
  ru: {
    navShell: "Оболочка",
    navMotion: "Лаборатория движения (16 этюдов)",
    navTypo: "Типографика",
    brandTitle: "ALPORA · INTERACTIVE LAB",
    liveBackend: "● БЭКЕНД ПОДКЛЮЧЁН",
    standalone: "● АВТОНОМНЫЙ РЕЖИМ",
    lblTheme: "Тема:",
    lblMode: "Режим:",
    workMode: "Работа",
    vibeMode: "Вайб",
    lblPower: "Профиль питания",
    lblTypoTitle: "Спецификация типографики ALPORA",
    lblTypoDesc: "Загружается напрямую через FontLoader в Quickshell и применяется по всей системе.",
    playAll: "↻ Запустить все",
    closeAll: "Закрыть все",
    speed: "Скорость",
    open: "Открыть",
    close: "Закрыть",
    repeat: "Повторить",
    opened: "Открыто",
    closed: "Закрыто",
    qmlCode: "Код QML",
    copied: "Скопировано!",
    footerHint: "Нажимай кнопки на верхнем баре для проверки панелей · Нажми Esc для закрытия.",
    days: ["Воскресенье", "Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"],
    pages: {
      settings: { title: "Быстрые настройки", subtitle: "ALPORA · Пространство", volume: "Громкость", brightness: "Яркость", wifi: "Wi-Fi", bluetooth: "Bluetooth", on: "Включено", off: "Выключено", mode: "Режим работы", balance: "Баланс" },
      calendar: { title: "Календарь", month: "Октябрь 2026", footer: "Отличное время для сосредоточенной работы", days: ['Пн','Вт','Ср','Чт','Пт','Сб','Вс'] },
      notifications: { title: "Уведомления", note1Title: "Добро пожаловать в ALPORA", note1Desc: "Система · только что", note2Title: "Плейлист готов", note2Desc: "Медиа · 5 мин назад", footer: "История системных уведомлений" },
      timeline: { title: "Хронология (Timeline)", subtitle: "От рассвета до полуночи" }
    }
  }
};

const THEME_PRESETS = {
  alpine: { label: "Alpine", accent: "#9eb393", bg: "#1a211e", fg: "#dbe3d6", surface: "#242d29", cool: "#7a9482", altWallpaper: "url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/alpine-dawn.png')" },
  moon: { label: "Moon Lake", accent: "#8fa3b3", bg: "#1a1f24", fg: "#d6dfe6", surface: "#242b32", cool: "#758c9e", altWallpaper: "url('https://images.unsplash.com/photo-1518495973542-4542c06a5843?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/moon-lake.png')" },
  forest: { label: "Forest Mist", accent: "#8ea889", bg: "#1a2119", fg: "#d7e3d4", surface: "#242d23", cool: "#738f6d", altWallpaper: "url('https://images.unsplash.com/photo-1448375240586-882707db888b?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/forest-mist.png')" },
  desert: { label: "Warm Desert", accent: "#b39c82", bg: "#241f1a", fg: "#e6ded6", surface: "#322b24", cool: "#9e866e", altWallpaper: "url('https://images.unsplash.com/photo-1509316975850-ff9c5deb0cd9?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/warm-desert.png')" },
  glacier: { label: "Northern Lights", accent: "#7ec4bb", bg: "#162325", fg: "#d2e7e7", surface: "#1f3033", cool: "#63a8a0", altWallpaper: "url('https://images.unsplash.com/photo-1531366936337-7c912a4589a7?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/northern-lights.png')" },
  coast: { label: "Rose Sunset", accent: "#b88f9c", bg: "#241a20", fg: "#e6d6dd", surface: "#32242c", cool: "#a17282", altWallpaper: "url('https://images.unsplash.com/photo-1495616811223-4d98c6e9c869?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/rose-sunset.png')" },
  timeline: { label: "Timeline (24h Dynamic)", accent: "#9eb393", bg: "#1a211e", fg: "#dbe3d6", surface: "#242d29", cool: "#7a9482", altWallpaper: "url('https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=1920&q=80')", wallpaper: "url('../../../assets/wallpapers/timeline/day.png')" },
};

const THEMES = {};
for (const [key, t] of Object.entries(THEME_PRESETS)) {
  THEMES[key] = {
    ...t,
    cardBg: `rgba(${parseInt(t.surface.slice(1,3),16)}, ${parseInt(t.surface.slice(3,5),16)}, ${parseInt(t.surface.slice(5,7),16)}, 0.45)`,
    cardBorder: `rgba(${parseInt(t.accent.slice(1,3),16)}, ${parseInt(t.accent.slice(3,5),16)}, ${parseInt(t.accent.slice(5,7),16)}, 0.22)`,
  };
}
