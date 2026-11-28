/**
 * ALPORA Unified Interactive Shell & Motion Sandbox
 * Single-Page Architecture with live Python BE telemetry & i18n support.
 * Pure JavaScript logic: zero embedded HTML strings or innerHTML usage.
 */

'use strict';

let currentLang = localStorage.getItem('alpora_demo_lang') || 'vi';
let currentTheme = localStorage.getItem('alpora_demo_theme') || 'alpine';
let speed = 1;
let isLiveBackend = false;
const controllers = [];

function applyTheme(key, notifyBackend = true) {
  const t = THEMES[key] || THEMES.alpine;
  currentTheme = key;
  localStorage.setItem('alpora_demo_theme', key);
  const root = document.documentElement;
  root.style.setProperty('--bg', t.bg);
  root.style.setProperty('--surface', t.surface);
  root.style.setProperty('--line', t.line);
  root.style.setProperty('--ink', t.ink);
  root.style.setProperty('--muted', t.muted);
  root.style.setProperty('--accent', t.accent);
  root.style.setProperty('--secondary', t.secondary);
  const wp = window.location.protocol === 'file:' ? t.altWallpaper : t.wallpaper;
  root.style.setProperty('--wallpaper', "url('" + wp + "')");

  document.querySelectorAll('.theme-pill-btn').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.theme === key);
  });

  if (notifyBackend) {
    void sendAction('theme', key);
  }
}

async function checkBackend() {
  try {
    const res = await fetch('/api/state');
    if (res.ok) {
      const data = await res.json();
      isLiveBackend = true;
      const badge = document.querySelector('#backend-badge');
      if (badge) {
        badge.textContent = I18N[currentLang].liveBackend;
        badge.style.color = 'var(--accent)';
      }
      if (data.metrics) {
        if (data.metrics.cpuPercent !== undefined) {
          const cpuEl = document.querySelector('#metric-cpu');
          if (cpuEl) cpuEl.textContent = data.metrics.cpuPercent + "% · 48°C";
        }
        if (data.metrics.ramUsedGb !== undefined) {
          const ramEl = document.querySelector('#metric-ram');
          if (ramEl) ramEl.textContent = data.metrics.ramUsedGb + " / " + data.metrics.ramTotalGb + " GB";
        }
        if (data.metrics.batteryPercent !== undefined) {
          const batSpan = document.querySelector('#qs-pill-btn span');
          if (batSpan) batSpan.textContent = data.metrics.batteryPercent + "%";
        }
      }
      if (data.session && data.session.theme && data.session.theme !== currentTheme) {
        applyTheme(data.session.theme, false);
      }
    }
  } catch (_) {
    isLiveBackend = false;
    const badge = document.querySelector('#backend-badge');
    if (badge) {
      badge.textContent = I18N[currentLang].standalone;
      badge.style.color = 'var(--muted)';
    }
  }
}

async function sendAction(action, value) {
  if (!isLiveBackend) return;
  try {
    await fetch('/api/action', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action, value })
    });
  } catch (_) {}
}

function updateLanguage(lang) {
  currentLang = lang;
  localStorage.setItem('alpora_demo_lang', lang);
  const t = I18N[lang];

  document.querySelectorAll('.lang-switch button').forEach(btn => {
    btn.setAttribute('aria-pressed', String(btn.dataset.lang === lang));
  });

  const setText = (selector, text) => {
    const el = document.querySelector(selector);
    if (el) el.textContent = text;
  };

  setText('#tab-nav-shell', t.navShell);
  setText('#tab-nav-motion', t.navMotion);
  setText('#tab-nav-typo', t.navTypo);
  setText('#lbl-theme', t.lblTheme);
  setText('#lbl-mode', t.lblMode);
  setText('#btn-work-mode', t.workMode);
  setText('#btn-vibe-mode', t.vibeMode);
  setText('#txt-power-label', t.lblPower);
  setText('#lbl-typo-title', t.lblTypoTitle);
  setText('#lbl-typo-desc', t.lblTypoDesc);
  setText('#play-all', t.playAll);
  setText('#close-all', t.closeAll);
  setText('#speed-label', t.speed);
  setText('#footer-hint', t.footerHint);

  const badge = document.querySelector('#backend-badge');
  if (badge) {
    badge.textContent = isLiveBackend ? t.liveBackend : t.standalone;
  }

  const setChildText = (parent, selector, text) => {
    if (!parent) return;
    const el = parent.querySelector(selector);
    if (el && text !== undefined) el.textContent = text;
  };

  // Update all 16 study cards in the DOM
  document.querySelectorAll('.study').forEach((card, i) => {
    const s = t.studies[i];
    if (!s) return;

    setChildText(card, '.study-title', s.title);
    setChildText(card, '.study-desc', s.desc);
    setChildText(card, '.hint-line', s.hint);
    setChildText(card, '.repeat-label', t.repeat);
    setChildText(card, '.qml-label', t.qmlCode);

    const isCardOpen = controllers[i] && controllers[i].open;
    setChildText(card, '.toggle', isCardOpen ? t.close : t.open);
    setChildText(card, '.state', isCardOpen ? t.opened : t.closed);

    // Update settings sub-page text
    const setPage = card.querySelector('.panel-page[data-page="settings"]');
    if (setPage) {
      setChildText(setPage, '.heading-title', t.pages.settings.title);
      setChildText(setPage, '.panel-subtitle', t.pages.settings.subtitle);
      setChildText(setPage, '.page-mode', t.pages.settings.mode);
      setChildText(setPage, '.mini-tag', t.pages.settings.balance);
    }

    // Update calendar sub-page text (if present)
    const calPage = card.querySelector('.panel-page[data-page="calendar"]');
    if (calPage) {
      setChildText(calPage, '.heading-title', t.pages.calendar.title);
      setChildText(calPage, '.calendar-month', t.pages.calendar.month);
      setChildText(calPage, '.footer-note', t.pages.calendar.footer);
      const weekdays = calPage.querySelectorAll('.weekday');
      t.pages.calendar.days.forEach((dayStr, dIdx) => {
        if (weekdays[dIdx]) weekdays[dIdx].textContent = dayStr;
      });
    }

    // Update notifications sub-page text (if present)
    const notifPage = card.querySelector('.panel-page[data-page="notifications"]');
    if (notifPage) {
      setChildText(notifPage, '.heading-title', t.pages.notifications.title);
      setChildText(notifPage, '.note-title-1', t.pages.notifications.note1Title);
      setChildText(notifPage, '.note-desc-1', t.pages.notifications.note1Desc);
      setChildText(notifPage, '.note-title-2', t.pages.notifications.note2Title);
      setChildText(notifPage, '.note-desc-2', t.pages.notifications.note2Desc);
      setChildText(notifPage, '.footer-note', t.pages.notifications.footer);
    }

    // Update timeline sub-page text (if present)
    const timePage = card.querySelector('.panel-page[data-page="timeline"]');
    if (timePage) {
      setChildText(timePage, '.heading-title', t.pages.timeline.title);
      setChildText(timePage, '.panel-subtitle', t.pages.timeline.subtitle);
    }
  });

  tick();
}

function tick() {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = now.getSeconds();

  const hourEl = document.querySelector('#hero-hour');
  if (hourEl) hourEl.textContent = hours;
  const minEl = document.querySelector('#hero-min');
  if (minEl) minEl.textContent = minutes;

  const fillEl = document.querySelector('#seconds-fill');
  if (fillEl) fillEl.style.width = ((seconds / 60) * 100) + '%';

  const t = I18N[currentLang];
  const dayName = t.days[now.getDay()];
  const dateEl = document.querySelector('#hero-date-text');
  if (dateEl) {
    dateEl.textContent = dayName + ", " + now.getDate() + " / " + (now.getMonth() + 1);
  }

  const clockBar = document.querySelector('#bar-clock');
  if (clockBar) {
    clockBar.textContent = hours + ":" + minutes + " · " + dayName.slice(0, 3) + " " + now.getDate();
  }

  if (!isLiveBackend) {
    const cpuVal = 28 + (seconds % 9);
    const cpuEl = document.querySelector('#metric-cpu');
    if (cpuEl) cpuEl.textContent = cpuVal + "% · 48°C";
  }


function initMotionStudies() {
  controllers.length = 0;
  const t = I18N[currentLang];
  const desktopTpl = document.querySelector('#study-desktop-template');
  const multiPagesTpl = document.querySelector('#study-multi-pages-template');
  const multiBarTpl = document.querySelector('#study-multi-bar-template');

  document.querySelectorAll('.study').forEach((el, i) => {
    const studyId = el.dataset.study;
    const studyCfg = t.studies[i];

    if (desktopTpl && !el.querySelector('.desktop')) {
      const clone = desktopTpl.content.cloneNode(true);
      const copyBtn = clone.querySelector('.copy-qml');
      if (copyBtn) copyBtn.dataset.qmlId = studyId;
      const demoLabel = clone.querySelector('.demo-label');
      if (demoLabel) demoLabel.textContent = 'ALPORA · ' + studyId.toUpperCase();
      const panel = clone.querySelector('.panel');
      if (panel && studyCfg) panel.setAttribute('aria-label', 'Preview: ' + studyCfg.title);

      if (studyCfg && studyCfg.pages) {
        if (multiBarTpl) {
          const barClone = multiBarTpl.content.cloneNode(true);
          const miniTime = clone.querySelector('.mini-time');
          const barActions = clone.querySelector('.bar-actions');
          const newTime = barClone.querySelector('.mini-time');
          const newActions = barClone.querySelector('.bar-actions');
          if (miniTime && newTime) miniTime.replaceWith(newTime);
          if (barActions && newActions) barActions.replaceWith(newActions);
        }
        if (multiPagesTpl) {
          const panelContent = clone.querySelector('.panel-content');
          if (panelContent) {
            panelContent.appendChild(multiPagesTpl.content.cloneNode(true));
          }
        }
      }

      const hintEl = el.querySelector('.hint-line');
      if (hintEl) el.insertBefore(clone, hintEl);
      else el.appendChild(clone);
    }

    controllers.push(new DemoCard(el, studyCfg));
  });

  document.querySelectorAll('.copy-qml').forEach(btn => {
    btn.onclick = () => {
      const qmlId = btn.dataset.qmlId;
      const snippet = '// Quickshell QML PanelMotion definition for "' + qmlId + '"\n' +
        'NumberAnimation on progress {\n' +
        '    duration: Session.motionMs > 0 ? ' + (qmlId === 'spring' ? 720 : 540) + ' : 0\n' +
        '    easing.type: ' + (qmlId === 'spring' ? 'Easing.OutBack' : 'Easing.OutCubic') + '\n' +
        '}';
      navigator.clipboard.writeText(snippet).then(() => {
        const label = btn.querySelector('.qml-label');
        if (label) {
          const orig = label.textContent;
          label.textContent = t.copied;
          setTimeout(() => { label.textContent = orig; }, 1800);
        }
      }).catch(() => {});
    };
  });
}

// Global initialization
document.addEventListener('DOMContentLoaded', () => {
  initMotionStudies();
  updateLanguage(currentLang);
  applyTheme(currentTheme, false);
  tick();
  setInterval(tick, 1000);
  void checkBackend();
  setInterval(() => { void checkBackend(); }, 4000);

  // Tab Navigation
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.onclick = () => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-view').forEach(v => v.classList.remove('active'));
      btn.classList.add('active');
      const targetView = document.querySelector('#view-' + btn.dataset.tab);
      if (targetView) targetView.classList.add('active');
    };
  });

  // Language buttons
  document.querySelectorAll('.lang-switch button').forEach(btn => {
    btn.onclick = () => updateLanguage(btn.dataset.lang);
  });

  // Theme buttons
  document.querySelectorAll('.theme-pill-btn[data-theme]').forEach(btn => {
    btn.onclick = () => applyTheme(btn.dataset.theme);
  });

  // Mode buttons
  const btnWork = document.querySelector('#btn-work-mode');
  const btnVibe = document.querySelector('#btn-vibe-mode');
  if (btnWork && btnVibe) {
    btnWork.onclick = () => {
      btnWork.classList.add('active');
      btnVibe.classList.remove('active');
      void sendAction('mode', 'work');
    };
    btnVibe.onclick = () => {
      btnVibe.classList.add('active');
      btnWork.classList.remove('active');
      void sendAction('mode', 'vibe');
    };
  }

  // Speed buttons
  document.querySelectorAll('[data-speed]').forEach(btn => {
    btn.onclick = () => {
      speed = Number(btn.dataset.speed);
      document.querySelectorAll('[data-speed]').forEach(b => b.setAttribute('aria-pressed', String(b === btn)));
    };
  });

  // Play All / Close All
  const playAllBtn = document.querySelector('#play-all');
  if (playAllBtn) playAllBtn.onclick = () => controllers.forEach(c => c.replay());

  const closeAllBtn = document.querySelector('#close-all');
  if (closeAllBtn) closeAllBtn.onclick = () => controllers.forEach(c => c.setOpen(false));

  // Workspaces
  document.querySelectorAll('.ws-pill').forEach(pill => {
    pill.onclick = () => {
      document.querySelectorAll('.ws-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
    };
  });

  // Hover-Faceted Quick Menu
  const qsPill = document.querySelector('#qs-pill-btn');
  const hoverMenu = document.querySelector('#hover-menu');
  if (qsPill && hoverMenu) {
    qsPill.onclick = () => {
      hoverMenu.classList.toggle('show');
      qsPill.classList.toggle('active');
    };
    const viewport = document.querySelector('#viewport');
    if (viewport) {
      viewport.onclick = (e) => {
        if (!e.target.closest('#qs-pill-btn') && !e.target.closest('#hover-menu')) {
          hoverMenu.classList.remove('show');
          qsPill.classList.remove('active');
        }
      };
    }
  }
});
