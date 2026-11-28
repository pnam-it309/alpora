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
  const overrides = {};
  if (id === 'iris') {
    overrides.clipPath = 'circle(145% at calc(100% - 17px) 0%)';
  } else if (id === 'slit') {
    overrides.clipPath = 'polygon(0% 0%,100% 0%,100% 100%,0% 100%)';
  }
  return Object.assign({}, final, overrides);
}

const ease = 'cubic-bezier(.2,.8,.2,1)';

class DemoCard {
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

    const toggleBtn = this.el.querySelector('.toggle');
    if (toggleBtn) {
      toggleBtn.onclick = () => {
        this.autoPlayed = true;
        this.setOpen(!this.open);
      };
    }

    const repeatBtn = this.el.querySelector('.repeat');
    if (repeatBtn) {
      repeatBtn.onclick = () => this.replay();
    }

    this.el.querySelectorAll('[data-page]').forEach(b => {
      b.onclick = () => {
        this.autoPlayed = true;
        const targetPage = b.dataset.page;
        if (this.config.pages && this.open && targetPage !== this.page) {
          this.changePage(targetPage);
        } else {
          if (this.config.pages) this.changePage(targetPage, false);
          this.setOpen(!this.open);
        }
      };
    });

    this.canvas.addEventListener('click', e => {
      if (e.target.closest('[data-close]')) {
        this.setOpen(false);
      } else if (!e.target.closest('.panel,.mini-bar')) {
        this.setOpen(false);
      }
      const toggleTile = e.target.closest('[data-toggle]');
      if (toggleTile) {
        const enabled = toggleTile.getAttribute('aria-pressed') !== 'true';
        toggleTile.setAttribute('aria-pressed', String(enabled));
        toggleTile.classList.toggle('off', !enabled);
        const t = I18N[currentLang].pages.settings;
        const smallLabel = toggleTile.querySelector('small');
        if (smallLabel) smallLabel.textContent = enabled ? t.on : t.off;
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
      try { a.commitStyles(); } catch (_) {}
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
      const source = this.el.querySelector('[data-page="' + this.page + '"]');
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
    const toggleBtn = this.el.querySelector('.toggle');
    if (toggleBtn) toggleBtn.textContent = this.open ? t.close : t.open;
    const status = this.el.querySelector('.state');
    if (status) {
      status.textContent = this.open ? t.opened : t.closed;
      status.classList.toggle('open', this.open);
    }
    this.panel.setAttribute('aria-hidden', String(!this.open));
    this.panel.inert = !this.open;
    this.el.querySelectorAll('[data-page]').forEach(b => {
      const selected = this.open && (!this.config.pages || b.dataset.page === this.page);
      b.classList.toggle('selected', selected);
      b.setAttribute('aria-expanded', String(selected));
    });
  }

  play(target, frames, options) {
    const a = target.animate(frames, Object.assign({ fill: 'forwards' }, options));
    a.finished.catch(() => {});
    return a;
  }

  setOpen(value, opts) {
    const instant = opts && opts.instant;
    this.stop();
    this.open = value;
    this.update();
    const opened = endStyle(this.config.id);
    const end = value ? opened : Object.assign({}, opened, closed[this.config.id]);
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

    if (value) {
      if (id === 'spring') {
        frames = [
          Object.assign({}, closed.spring, { offset: 0 }),
          { transform: 'translateY(7px)', opacity: 1, offset: 0.57 },
          { transform: 'translateY(-2px)', opacity: 1, offset: 0.79 },
          Object.assign({}, opened, { offset: 1 })
        ];
      } else if (id === 'center') {
        frames = [
          Object.assign({}, opened, closed.center, { offset: 0 }),
          Object.assign({}, opened, { clipPath: 'inset(49.5% 0% 49.5% 0% round 14px)', offset: 0.38 }),
          Object.assign({}, opened, { offset: 1 })
        ];
      } else if (id === 'slit') {
        frames = [
          Object.assign({}, opened, closed.slit, { offset: 0 }),
          Object.assign({}, opened, { clipPath: 'polygon(0% 0%,100% 0%,100% 1%,0% 1%)', offset: 0.38 }),
          Object.assign({}, opened, { offset: 1 })
        ];
      } else if (id === 'liquid') {
        frames = [
          Object.assign({}, opened, closed.liquid, { offset: 0 }),
          { transform: 'translateY(-12px) scale(.48,.65)', borderRadius: '58% 42% 35% 65% / 65% 40% 60% 35%', opacity: 1, offset: 0.36 },
          { transform: 'translateY(3px) scale(1.025,.97)', borderRadius: '25px 20px 32px 18px', opacity: 1, offset: 0.74 },
          Object.assign({}, opened, { offset: 1 })
        ];
      }
    }
    const duration = (this.config.duration || 540) * (value ? 1 : 0.8) / speed;
    const animation = this.play(this.panel, frames, { duration, easing: ['spring', 'center', 'liquid', 'slit'].includes(id) ? 'linear' : ease });

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

    // Toggle hidden property on pre-rendered panel pages
    this.panel.querySelectorAll('.panel-page').forEach(pageEl => {
      pageEl.hidden = (pageEl.dataset.page !== page);
    });

    this.layout();
    this.update();
    if (animate && this.open) {
      const next = { left: this.panel.style.left, width: this.panel.style.width, height: this.panel.style.height };
      const old = { left: previous.left + 'px', width: previous.width + 'px', height: previous.height + 'px' };
      const duration = 540 / speed;
      this.play(this.panel, [old, next], { duration, easing: ease });
      this.play(this.body, [{ opacity: 0 }, { opacity: 1 }], { duration, easing: 'linear' });
    }
  }
}
