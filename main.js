/* ============================================================
   TAVIA — 交互
   1) 首屏丝带随滚动上卷  2) 全站飘雪  3) 结尾像素雪花
   4) 复制联系方式  5) 入场
   ============================================================ */
(() => {
  'use strict';

  const root = document.documentElement;
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const lerp = (a, b, t) => a + (b - a) * t;
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));

  /* ---------------------------------------------------------
     1. 丝带：滚动进度 --p（0→1）
     --------------------------------------------------------- */
  let rawP = 0, smoothP = 0;
  let scrolling = false;

  function readScroll() {
    rawP = clamp(window.scrollY / Math.max(1, window.innerHeight * 0.92), 0, 1);
    scrolling = true;
  }
  addEventListener('scroll', readScroll, { passive: true });
  readScroll();

  function tickRibbon() {
    smoothP = reduce ? rawP : lerp(smoothP, rawP, 0.12);
    if (Math.abs(smoothP - rawP) < 0.001) smoothP = rawP;
    root.style.setProperty('--p', smoothP.toFixed(4));
  }

  /* ---------------------------------------------------------
     2. 全站飘雪
     --------------------------------------------------------- */
  const snow = document.getElementById('snowfall');
  const sctx = snow && snow.getContext('2d', { alpha: true });
  let flakes = [], W = 0, H = 0, dpr = 1;
  let paperMix = 0, paperTarget = 0;      // 0 = 夜（白） 1 = 纸（蓝墨）

  function sizeSnow() {
    if (!sctx) return;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    W = snow.clientWidth; H = snow.clientHeight;
    snow.width = Math.round(W * dpr);
    snow.height = Math.round(H * dpr);
    sctx.setTransform(dpr, 0, 0, dpr, 0, 0);

    const target = W < 640 ? 46 : W < 1100 ? 78 : 104;
    flakes = [];
    for (let i = 0; i < target; i++) {
      flakes.push({
        x: Math.random() * W,
        y: Math.random() * H,
        s: Math.random() < 0.55 ? 2 : Math.random() < 0.85 ? 3 : 4,   // 像素块
        v: 0.16 + Math.random() * 0.5,
        sway: Math.random() * Math.PI * 2,
        swaySpd: 0.006 + Math.random() * 0.014,
        swayAmp: 0.25 + Math.random() * 0.75,
        a: 0.22 + Math.random() * 0.62
      });
    }
  }

  // 当前位置是纸还是夜：给雪换颜色（纸上是蓝墨点，夜是白点）
  function sampleMood() {
    const el = document.elementFromPoint(window.innerWidth * 0.5, window.innerHeight * 0.5);
    paperTarget = el && el.closest && el.closest('.sheet') ? 1 : 0;
  }
  setInterval(sampleMood, 240);
  sampleMood();

  function drawSnow() {
    if (!sctx) return;
    sctx.clearRect(0, 0, W, H);
    paperMix = lerp(paperMix, paperTarget, 0.06);

    const night = [255, 255, 255];
    const paper = [30, 74, 130];
    const r = Math.round(lerp(night[0], paper[0], paperMix));
    const g = Math.round(lerp(night[1], paper[1], paperMix));
    const b = Math.round(lerp(night[2], paper[2], paperMix));

    for (const f of flakes) {
      f.sway += f.swaySpd;
      f.y += f.v;
      f.x += Math.sin(f.sway) * f.swayAmp * 0.35;

      if (f.y > H + 6) { f.y = -6; f.x = Math.random() * W; }
      if (f.x < -8) f.x = W + 8;
      if (f.x > W + 8) f.x = -8;

      sctx.fillStyle = `rgba(${r},${g},${b},${f.a * (0.6 + 0.4 * paperMix)})`;
      sctx.fillRect(Math.round(f.x), Math.round(f.y), f.s, f.s);
    }
  }

  /* ---------------------------------------------------------
     3. 结尾的像素雪花
     --------------------------------------------------------- */
  const flakeCv = document.getElementById('flake');
  const fctx = flakeCv && flakeCv.getContext('2d');
  const N = 73;                     // 73×73 的像素网格（够细，才有雪花的轻）
  const C = (N - 1) / 2;
  const R = 30;                     // 主臂长度（格）
  let cells = [];                   // {x, y, d}
  let flakeProg = 0, flakeVisible = false;

  // 先在 3 倍分辨率的网格上画线，再降采样取整：
  // 这样六条臂既对称又连得住，不会出现断点和中心的黑叉。
  function buildFlake() {
    const S = 3;                    // 超采样倍数
    const g = N * S;
    const cg = (g - 1) / 2;
    const hi = new Uint8Array(g * g);

    const put = (x, y) => {
      x = Math.round(x); y = Math.round(y);
      if (x < 0 || y < 0 || x >= g || y >= g) return;
      hi[y * g + x] = 1;
    };
    // 在超采样网格上画粗线
    const line = (x0, y0, x1, y1, w) => {
      const n = Math.ceil(Math.hypot(x1 - x0, y1 - y0) * 2) + 1;
      for (let i = 0; i <= n; i++) {
        const t = i / n;
        const px = x0 + (x1 - x0) * t, py = y0 + (y1 - y0) * t;
        const r = Math.max(1, Math.round(w));
        for (let dy = -r; dy <= r; dy++) {
          for (let dx = -r; dx <= r; dx++) {
            if (dx * dx + dy * dy <= r * r + 0.8) {
              put(cg + px + dx, cg + py + dy);
            }
          }
        }
      }
    };

    const HR = R * S;
    const segs = [];
    // 六条臂 + 三对枝 + 臂尖
    for (let k = 0; k < 6; k++) {
      const a = Math.PI / 3 * k;
      const ca = Math.cos(a), sa = Math.sin(a);
      const rot = (x, y) => [x * ca - y * sa, x * sa + y * ca];
      // 主臂
      segs.push([0, 0, HR, 0].map((v, i) => i < 2 ? v : v)); // 占位，下面单独处理
      const [ax, ay] = rot(0, HR);
      line(0, 0, ax, ay, 1.0 * S * 0.5);
      // 三对枝，和臂成 60°
      [[0.33, 0.30], [0.54, 0.24], [0.73, 0.17]].forEach(([t, len], idx) => {
        const by = HR * t, bl = HR * len;
        const b60 = Math.PI / 3;
        for (const sgn of [1, -1]) {
          const bx = Math.cos(b60) * bl * sgn;
          const byy = by + Math.sin(b60) * bl;
          const [rx, ry] = rot(bx, byy);
          const [sx, sy] = rot(0, by);
          line(sx, sy, rx, ry, 0.8 * S * 0.5);
          // 枝尖的小点
          for (let q = -1; q <= 1; q++) put(cg + rx + q, cg + ry);
          for (let q = -1; q <= 1; q++) put(cg + ry * 0 + rx, cg + ry + q);
        }
      });
      // 臂尖的小十字
      const [tx, ty] = rot(0, HR);
      const [lx, ly] = rot(-2.2 * S, HR);
      const [rx2, ry2] = rot(2.2 * S, HR);
      line(lx, ly, rx2, ry2, 0.7 * S * 0.5);
    }

    // 中心的小六边形
    for (let k = 0; k < 6; k++) {
      const a1 = Math.PI / 3 * k, a2 = Math.PI / 3 * (k + 1);
      const r = 2.2 * S;
      line(Math.cos(a1) * r, Math.sin(a1) * r, Math.cos(a2) * r, Math.sin(a2) * r, 0.9 * S * 0.5);
      line(0, 0, Math.cos(a1) * r, Math.sin(a1) * r, 0.9 * S * 0.5);
    }

    // 降采样：一个输出格里覆盖到 3 个以上子像素就算实心
    cells = [];
    for (let y = 0; y < N; y++) {
      for (let x = 0; x < N; x++) {
        let n = 0;
        for (let j = 0; j < S; j++) {
          for (let i = 0; i < S; i++) {
            if (hi[(y * S + j) * g + (x * S + i)]) n++;
          }
        }
        if (n >= 3) {
          const dx = x - C, dy = y - C;
          cells.push({ x: dx, y: dy, d: Math.hypot(dx, dy) });
        }
      }
    }
    cells.sort((p, q) => p.d - q.d);
  }
  buildFlake();
  const MAXD = cells.length ? cells[cells.length - 1].d : 1;

  function sizeFlake() {
    if (!fctx) return;
    const d = Math.min(window.devicePixelRatio || 1, 2);
    const w = flakeCv.clientWidth || 320;
    flakeCv.width = Math.round(w * d);
    flakeCv.height = Math.round(w * d);
    fctx.setTransform(d, 0, 0, d, 0, 0);
  }

  function drawFlake(t) {
    if (!fctx) return;
    const w = flakeCv.clientWidth;
    if (!w) return;

    const px = Math.max(2, Math.floor(w * 0.92 / N));
    const span = px * N;
    const ox = (w - span) / 2;
    const oy = (w - span) / 2;
    fctx.clearRect(0, 0, w, w);

    // 背后的冷光
    const halo = fctx.createRadialGradient(w / 2, w / 2, w * 0.04, w / 2, w / 2, w * 0.52);
    halo.addColorStop(0, `rgba(150,200,255,${0.14 * flakeProg})`);
    halo.addColorStop(1, 'rgba(150,200,255,0)');
    fctx.fillStyle = halo;
    fctx.fillRect(0, 0, w, w);

    // 像素雪花：从中心向外生长
    const reveal = flakeProg * MAXD * 1.06;
    for (const c of cells) {
      if (c.d > reveal) continue;
      const edge = c.d > reveal - 1.6 ? 0.55 : 1;
      const core = 1 - Math.min(1, c.d / MAXD) * 0.35;
      const twinkle = 0.92 + 0.08 * Math.sin(t * 0.0014 + c.d * 0.7);
      const alpha = Math.min(1, (0.35 + 0.65 * edge) * flakeProg * 1.6) * core * twinkle;
      fctx.fillStyle = `rgba(236,247,255,${alpha.toFixed(3)})`;
      fctx.fillRect(ox + (c.x + C) * px, oy + (c.y + C) * px, px, px);
    }

    // 萦绕的碎雪：不跟着雪花转，各自绕行
    const w2 = w / 2;
    for (let i = 0; i < 18; i++) {
      const rad = w * (0.26 + 0.24 * (((i * 7) % 11) / 11));
      const spd = 0.00022 + (i % 5) * 0.00008;
      const ang = i * 2.399963 + t * spd * (i % 2 ? 1 : -1);
      const ex = w2 + Math.cos(ang) * rad * 1.04;
      const ey = w2 + Math.sin(ang) * rad * 0.66;
      const s = (i % 3 === 0 ? 3 : 2);
      const fl = 0.3 + 0.55 * Math.abs(Math.sin(ang * 2 + i));
      fctx.fillStyle = `rgba(226,242,255,${(fl * Math.min(1, flakeProg * 3)).toFixed(3)})`;
      fctx.fillRect(Math.round(ex), Math.round(ey), s, s);
    }
  }

  function readFlakeProgress() {
    if (!flakeCv) return;
    const r = flakeCv.getBoundingClientRect();
    const vh = window.innerHeight;
    flakeProg = clamp((vh * 0.92 - r.top) / (vh * 0.62), 0, 1);
    flakeVisible = r.bottom > -80 && r.top < vh + 80;
  }

  /* ---------------------------------------------------------
     4. 动画循环
     --------------------------------------------------------- */
  let t0 = 0, frameCount = 0;
  function loop(t) {
    if (!t0) t0 = t;
    const time = t - t0;

    tickRibbon();

    if (!reduce) drawSnow();

    // 可见性每 6 帧检查一次，够用又不至于每帧读布局
    if (++frameCount % 6 === 0) readFlakeProgress();
    if (flakeVisible) drawFlake(t);
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);

  /* ---------------------------------------------------------
     5. 入场
     --------------------------------------------------------- */
  const io = 'IntersectionObserver' in window
    ? new IntersectionObserver((entries) => {
        for (const e of entries) {
          if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); }
        }
      }, { rootMargin: '0px 0px -8% 0px', threshold: 0.12 })
    : null;

  document.querySelectorAll('[data-reveal]').forEach((el, i) => {
    el.style.transitionDelay = `${Math.min(i * 70, 420)}ms`;
    if (io) io.observe(el); else el.classList.add('in');
  });
  // 首屏立刻入场
  requestAnimationFrame(() => {
    document.querySelectorAll('#hero [data-reveal]').forEach((el, i) => {
      el.style.transitionDelay = `${180 + i * 110}ms`;
      el.classList.add('in');
    });
  });

  /* ---------------------------------------------------------
     6. 复制联系方式
     --------------------------------------------------------- */
  const toast = document.getElementById('toast');
  let toastTimer = 0;
  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('on');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(() => toast.classList.remove('on'), 1800);
  }

  async function copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (e) {
      const ta = document.createElement('textarea');
      ta.value = text;
      ta.setAttribute('readonly', '');
      ta.style.cssText = 'position:fixed;top:-1000px;opacity:0';
      document.body.appendChild(ta);
      ta.select();
      let ok = false;
      try { ok = document.execCommand('copy'); } catch (_) {}
      document.body.removeChild(ta);
      return ok;
    }
  }

  document.querySelectorAll('[data-copy]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      const val = btn.getAttribute('data-copy');
      const ok = await copyText(val);
      showToast(ok ? `已复制  ${val}` : `复制失败，请手动选择：${val}`);
    });
  });

  /* ---------------------------------------------------------
     7. 尺寸变化
     --------------------------------------------------------- */
  let rz = 0;
  addEventListener('resize', () => {
    clearTimeout(rz);
    rz = setTimeout(() => {
      sizeSnow();
      sizeFlake();
      readScroll();
    }, 180);
  });

  sizeSnow();
  sizeFlake();
  readFlakeProgress();
  if (reduce) { drawSnow(); drawFlake(0); }
  addEventListener('load', () => { sizeSnow(); sizeFlake(); });
})();
