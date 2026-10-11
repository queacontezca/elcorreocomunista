/* ════════════════════════════════════════════════════════════════════
   interactivo.js — capa de interacción de los gráficos (portada y Observatorio)
   Sin dependencias ni llamadas externas. Todo lo que hace es mejora
   progresiva: sin JavaScript los gráficos se ven igual que antes.
   1. Gráficos estáticos (.graf svg): cada marca con <title> gana una
      etiqueta flotante; las marcas del mismo período se leen juntas;
      se puede recorrer con teclado; «Ver los datos» abre la tabla.
   2. Gráfico de series (.graf-serie): se dibuja desde el JSON incrustado
      que genera scripts/build_observatorio.py; permite cambiar de serie
      y leer cada período comparado con el mismo del año anterior.
   3. Observatorio: índice fijo de módulos que marca dónde se está.
   ════════════════════════════════════════════════════════════════════ */
(function () {
  'use strict';
  var NS = 'http://www.w3.org/2000/svg';
  var quieto = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var nf = function (v, d) { return Number(v).toLocaleString('es-CL', { minimumFractionDigits: d || 0, maximumFractionDigits: d || 0 }); };

  /* ── etiqueta flotante compartida ── */
  var tip = document.createElement('div');
  tip.className = 'graf-tip'; tip.setAttribute('role', 'status'); tip.hidden = true;
  document.body.appendChild(tip);
  function muestraTip(lineas, x, y) {
    tip.textContent = '';
    lineas.forEach(function (l, i) {
      var p = document.createElement(i === 0 && lineas.length > 1 ? 'strong' : 'span');
      p.textContent = l; tip.appendChild(p);
    });
    tip.hidden = false;
    var r = tip.getBoundingClientRect(), W = document.documentElement.clientWidth;
    var left = Math.min(Math.max(8, x - r.width / 2), W - r.width - 8);
    var top = y - r.height - 14; if (top < 8) top = y + 18;
    tip.style.left = (left + window.scrollX) + 'px'; tip.style.top = (top + window.scrollY) + 'px';
  }
  function ocultaTip() { tip.hidden = true; }

  /* ── 1. gráficos estáticos ── */
  function mejoraEstatico(svg) {
    if (svg.closest('.graf-serie') || svg.classList.contains('mapa')) return;
    var marcas = [].filter.call(svg.querySelectorAll('rect, circle'), function (m) {
      return m.firstElementChild && m.firstElementChild.tagName.toLowerCase() === 'title';
    });
    if (!marcas.length) return;
    svg.classList.add('graf-vivo');
    var grupos = {};
    marcas.forEach(function (m) {
      var t = m.firstElementChild.textContent; m.dataset.t = t;
      m.removeChild(m.firstElementChild);            /* evita la etiqueta nativa duplicada */
      m.setAttribute('aria-label', t);
      var clave = m.tagName === 'circle' ? 'c' + m.getAttribute('cx') : 'r' + m.getAttribute('x') + '|' + m.getAttribute('width');
      m.dataset.g = clave; (grupos[clave] = grupos[clave] || []).push(m);
    });
    var claves = Object.keys(grupos);
    claves.forEach(function (k) { grupos[k][0].setAttribute('tabindex', '0'); });
    function activa(m, ev) {
      var g = grupos[m.dataset.g];
      svg.classList.add('hov');
      marcas.forEach(function (x) { x.classList.toggle('on', g.indexOf(x) > -1); });
      var b = m.getBoundingClientRect();
      var x = ev && ev.clientX ? ev.clientX : b.left + b.width / 2;
      var y = ev && ev.clientY ? ev.clientY : b.top;
      muestraTip(g.map(function (z) { return z.dataset.t; }), x, y);
    }
    function suelta() { svg.classList.remove('hov'); marcas.forEach(function (x) { x.classList.remove('on'); }); ocultaTip(); }
    marcas.forEach(function (m) {
      m.addEventListener('pointerenter', function (e) { activa(m, e); });
      m.addEventListener('pointermove', function (e) { activa(m, e); });
      m.addEventListener('pointerleave', suelta);
      m.addEventListener('focus', function () { activa(m); });
      m.addEventListener('blur', suelta);
      m.addEventListener('keydown', function (e) {
        var i = claves.indexOf(m.dataset.g);
        if (e.key === 'ArrowRight' || e.key === 'ArrowDown') i = Math.min(claves.length - 1, i + 1);
        else if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') i = Math.max(0, i - 1);
        else return;
        e.preventDefault(); grupos[claves[i]][0].focus();
      });
    });
    /* tabla de datos plegable */
    var caja = svg.closest('.graf');
    if (caja && !caja.querySelector('.datos-graf')) {
      var det = document.createElement('details'); det.className = 'datos-graf';
      var sum = document.createElement('summary'); sum.textContent = 'Ver los datos de este gráfico'; det.appendChild(sum);
      var ul = document.createElement('ul');
      marcas.forEach(function (m) { var li = document.createElement('li'); li.textContent = m.dataset.t; ul.appendChild(li); });
      det.appendChild(ul); caja.appendChild(det);
    }
    /* entrada: las barras crecen al entrar en pantalla */
    if (!quieto && 'IntersectionObserver' in window) {
      /* el estado de reposo es el gráfico completo: si el observador no dispara, no se pierde nada */
      new IntersectionObserver(function (en, ob) {
        en.forEach(function (e) { if (e.isIntersecting) { svg.classList.add('entra'); ob.disconnect(); } });
      }, { threshold: 0.25 }).observe(svg);
    }
  }

  /* ── 2. gráfico de series, dibujado desde JSON ── */
  function el(n, at, txt) { var e = document.createElementNS(NS, n); for (var k in at) e.setAttribute(k, at[k]); if (txt != null) e.textContent = txt; return e; }
  function graficoSerie(caja) {
    var src = document.getElementById(caja.dataset.datos); if (!src) return;
    var D; try { D = JSON.parse(src.textContent); } catch (e) { return; }
    var filas = D.filas, series = D.series, actual = series[0].clave, sel = filas.length - 1;
    caja.textContent = '';
    var bot = document.createElement('div'); bot.className = 'serie-botones'; bot.setAttribute('role', 'group'); bot.setAttribute('aria-label', 'Serie que se muestra');
    series.forEach(function (s) {
      var b = document.createElement('button'); b.type = 'button'; b.textContent = s.corto; b.dataset.clave = s.clave;
      b.setAttribute('aria-pressed', s.clave === actual ? 'true' : 'false');
      b.addEventListener('click', function () { actual = s.clave; pinta(); });
      bot.appendChild(b);
    });
    var W = 420, H = 150, BASE = H - 18, ALTO = BASE - 14;
    var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, 'class': 'mini-graf', role: 'group' });
    var lect = document.createElement('p'); lect.className = 'serie-lectura'; lect.setAttribute('aria-live', 'polite');
    var nota = document.createElement('p'); nota.className = 'cifra-nota serie-fuente';
    caja.appendChild(bot); caja.appendChild(svg); caja.appendChild(lect); caja.appendChild(nota);
    var n = filas.length, gap = 5, bw = (W - gap * (n - 1)) / n, barras = [];
    svg.appendChild(el('line', { 'class': 'b-base', x1: 0, y1: BASE, x2: W, y2: BASE }));
    filas.forEach(function (f, i) {
      var x = i * (bw + gap);
      var r = el('rect', { 'class': 'b', x: x.toFixed(1), y: BASE, width: bw.toFixed(1), height: 0, tabindex: i === sel ? 0 : -1 });
      r.addEventListener('pointerenter', function () { elige(i); });
      r.addEventListener('click', function () { elige(i); });
      r.addEventListener('focus', function () { elige(i); });
      r.addEventListener('keydown', function (e) {
        var j = i;
        if (e.key === 'ArrowRight') j = Math.min(n - 1, i + 1); else if (e.key === 'ArrowLeft') j = Math.max(0, i - 1); else return;
        e.preventDefault(); barras[j].focus();
      });
      svg.appendChild(r); barras.push(r);
      if (f.t === 1) svg.appendChild(el('text', { 'class': 'b-eje', x: x.toFixed(1), y: H - 4 }, f.a));
    });
    function serie() { return series.filter(function (s) { return s.clave === actual; })[0]; }
    function elige(i) {
      sel = i; var s = serie(), f = filas[i], v = f[actual];
      barras.forEach(function (b, j) { b.classList.toggle('sel', j === i); b.setAttribute('tabindex', j === i ? 0 : -1); });
      var prev = filas.filter(function (z) { return z.a === f.a - 1 && z.t === f.t; })[0];
      var txt = f.a + ' T' + f.t + ' · US$ ' + nf(v) + ' M';
      var cmp = '';
      if (prev && prev[actual]) { var d = (v / prev[actual] - 1) * 100; cmp = (d >= 0 ? '+' : '−') + nf(Math.abs(d), 1) + ' % sobre ' + prev.a + ' T' + prev.t; }
      lect.textContent = '';
      var st = document.createElement('strong'); st.textContent = txt; lect.appendChild(st);
      if (cmp) { var sp = document.createElement('span'); sp.textContent = cmp; lect.appendChild(sp); }
      barras[i].setAttribute('aria-label', s.nombre + ', ' + txt + (cmp ? ', ' + cmp : ''));
    }
    function pinta() {
      var s = serie(), mx = Math.max.apply(null, filas.map(function (f) { return f[actual]; }));
      [].forEach.call(bot.children, function (b) { b.setAttribute('aria-pressed', b.dataset.clave === actual ? 'true' : 'false'); });
      filas.forEach(function (f, i) {
        var h = Math.max(1, f[actual] / mx * ALTO);
        barras[i].setAttribute('y', (BASE - h).toFixed(1)); barras[i].setAttribute('height', h.toFixed(1));
        barras[i].classList.toggle('b-ult', f[actual] === mx);
      });
      svg.setAttribute('aria-label', s.nombre + ', por trimestre');
      nota.textContent = s.nombre + '. En rojo, el trimestre más alto de lo graficado. ';
      var fu = document.createElement('span'); fu.textContent = D.fuente; nota.appendChild(fu);
      elige(sel);
    }
    pinta();
  }

  /* ── 3. índice del Observatorio ── */
  function indiceObs(nav) {
    var enlaces = [].slice.call(nav.querySelectorAll('a[href^="#"]'));
    var blancos = enlaces.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
    if (!('IntersectionObserver' in window)) return;
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = blancos.indexOf(e.target);
        enlaces.forEach(function (a, j) { if (j === i) a.setAttribute('aria-current', 'true'); else a.removeAttribute('aria-current'); });
      });
    }, { rootMargin: '-25% 0px -65% 0px' });
    blancos.forEach(function (b) { if (b) io.observe(b); });
  }

  function inicia() {
    [].forEach.call(document.querySelectorAll('.graf-serie'), graficoSerie);
    [].forEach.call(document.querySelectorAll('.graf svg'), mejoraEstatico);
    [].forEach.call(document.querySelectorAll('.nav-obs'), indiceObs);
    document.addEventListener('scroll', ocultaTip, { passive: true });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') ocultaTip(); });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', inicia); else inicia();
})();
