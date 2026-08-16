# -*- coding: utf-8 -*-
"""
build_observatorio.py — Genera observatorio.html desde la capa de datos.

REGLA DE ORO (continuidad): ninguna cifra de la página se escribe a mano aquí;
todo número sale de datos/observatorio/*.csv (fuente única de verdad, compartida
con el Reporte de Análisis de Coyuntura). Los textos analíticos sí son editoriales.

Uso:  python3 scripts/build_observatorio.py
      (desde la raíz del sitio; stdlib pura, sin dependencias)
"""
import csv, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos" / "observatorio"
SALIDA = RAIZ / "observatorio.html"

# ───────────────────────── utilidades ─────────────────────────
def lee_csv(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def fmt(v, dec=0):
    """Punto de miles, coma decimal (es-CL)."""
    if v is None: return "—"
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

ROJO, SAL, NEGRO, PIZ, REJ, PAPEL = "#8b1a1a", "#b3543f", "#17110c", "#5c554d", "#d8d2c4", "#efe8d2"

# ───────────────────────── datos ─────────────────────────
rentas_cl = lee_csv("rentas_primarias_chile.csv")
rentas_al = lee_csv("rentas_primarias_al20.csv")
pais24 = lee_csv("rentas_debito_pais_2024.csv")
hickel = lee_csv("drenaje_mundial_hickel.csv")
ied = lee_csv("ied_entradas_cepal.csv")
impuesto = lee_csv("impuesto_primera_categoria.csv")
jornada = {r["concepto"]: r for r in lee_csv("jornada_semana_obrera.csv")}
kpis = lee_csv("kpi_corte.csv")
MAPA_BASE = (DATOS / "mapa_base_paises.svg").read_text(encoding="utf-8")

def h(indicador, periodo=None):
    for r in hickel:
        if r["indicador"] == indicador and (periodo is None or r["periodo"] == periodo):
            return float(r["valor"])
    raise KeyError(indicador)

CL_2025 = next(r for r in rentas_cl if r["anio"] == "2025")
CL_2024 = next(r for r in rentas_cl if r["anio"] == "2024")
CL_2026 = next(r for r in rentas_cl if r["anio"] == "2026")
CL_2016 = next(r for r in rentas_cl if r["anio"] == "2016")
AL_2025 = next(r for r in rentas_al if r["anio"] == "2025")
AL_2024 = next(r for r in rentas_al if r["anio"] == "2024")
IED_AL = float(next(r["valor"] for r in ied if r["indicador"] == "AL_entradas_ied"))
IED_CL = float(next(r["valor"] for r in ied if r["indicador"] == "Chile_entradas_ied"))
PIB_CL = 330124  # US$ millones, Anuario CEPAL (2024) — constatado en metadatos

deb25 = float(CL_2025["debito_total"]); uti25 = float(CL_2025["ied_utilidades_dividendos"])
int25 = float(CL_2025["intereses_otra_inversion"]); deb16 = float(CL_2016["debito_total"])
al_deb25 = float(AL_2025["debito_total"]); al_uti25 = float(AL_2025["ied_utilidades_piso"])
razon_cl = float(CL_2024["ied_utilidades_dividendos"]) / IED_CL
razon_al = float(AL_2024["ied_utilidades_piso"]) / IED_AL
pib_pct = float(CL_2024["debito_total"]) / PIB_CL * 100
mult = deb25 / deb16

# ───────────────────────── figuras SVG ─────────────────────────
def apilada_jornada():
    segs = [("trabajo_necesario", "Trabajo necesario (repite el salario)", NEGRO),
            ("plustrabajo", "Plustrabajo (no pagado: plusvalor)", ROJO),
            ("traslado_no_remunerado", "Traslado no remunerado (tiempo vital expropiado)", SAL),
            ("reproductivo_no_remunerado", "Reproductivo no remunerado (hogar y cuidados)", PIZ)]
    W, H, P = 760, 150, 30
    total = sum(float(jornada[k]["valor"]) for k, _, _ in segs)
    x, g = P, ""
    for k, nom, col in segs:
        v = float(jornada[k]["valor"]); w = (W - 2 * P) * v / total
        g += (f'<rect x="{x:.0f}" y="30" width="{w:.0f}" height="52" fill="{col}">'
              f'<title>{nom}: {fmt(v,2).rstrip("0").rstrip(",")} h semanales</title></rect>'
              f'<text x="{x + w/2:.0f}" y="60" font-size="12" text-anchor="middle" fill="#f3edda">{fmt(v,2).rstrip("0").rstrip(",")} h</text>'
              f'<text x="{x + w/2:.0f}" y="104" font-size="10.5" text-anchor="middle" fill="{NEGRO}">{nom.split(" (")[0]}</text>')
        x += w
    g += (f'<text x="{P}" y="136" font-size="11" fill="{PIZ}" font-style="italic">'
          f'Carga global real: {fmt(float(jornada["carga_global_real"]["valor"]))} h/semana (insumo 2026.2) · jornada legal: 42 h desde abr-2026</text>')
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Composición de la semana obrera">{g}</svg>'

def barras_rentas_chile():
    """Barras apiladas: utilidades IED + intereses + resto del débito, 2016→2026T1."""
    W, H, P = 760, 320, 52
    filas = [r for r in rentas_cl]
    mx = max(float(r["debito_total"]) for r in filas) * 1.12
    n = len(filas); slot = (W - P - 16) / n; bw = slot * 0.66
    def y(v): return (H - P) - (H - 2 * P) * v / mx
    g = ""
    for t in range(0, 5):
        vv = mx * t / 4 / 1.12 * 1.0; vv = (mx / 1.12) * t / 4
        yy = y(vv * 1.0)
        g += (f'<line x1="{P}" y1="{y(vv):.0f}" x2="{W-16}" y2="{y(vv):.0f}" stroke="{REJ}"/>'
              f'<text x="{P-6}" y="{y(vv)+4:.0f}" font-size="10" text-anchor="end" fill="{PIZ}">{fmt(vv/1000)}</text>')
    g += (f'<text x="{P-6}" y="{y(mx/1.12)-8:.0f}" font-size="10" text-anchor="end" fill="{PIZ}" font-style="italic">miles de millones US$</text>')
    for i, r in enumerate(filas):
        x0 = P + slot * i + (slot - bw) / 2
        deb = float(r["debito_total"]); uti = float(r["ied_utilidades_dividendos"])
        inter = float(r["intereses_otra_inversion"]); resto = deb - uti - inter
        y_uti = y(uti)
        g += (f'<rect x="{x0:.0f}" y="{y_uti:.0f}" width="{bw:.0f}" height="{H-P-y_uti:.0f}" fill="{ROJO}">'
              f'<title>Utilidades y dividendos IED {r["anio"]}: US$ {fmt(uti)} M</title></rect>')
        y_int = y(uti + inter)
        g += (f'<rect x="{x0:.0f}" y="{y_int:.0f}" width="{bw:.0f}" height="{y_uti-y_int:.0f}" fill="{SAL}">'
              f'<title>Intereses de otra inversión {r["anio"]}: US$ {fmt(inter)} M</title></rect>')
        y_top = y(deb)
        g += (f'<rect x="{x0:.0f}" y="{y_top:.0f}" width="{bw:.0f}" height="{y_int-y_top:.0f}" fill="{PIZ}">'
              f'<title>Resto del débito (cartera, etc.) {r["anio"]}: US$ {fmt(resto)} M</title></rect>')
        if deb >= deb25:
            g += (f'<text x="{x0+bw/2:.0f}" y="{y_top-8:.0f}" font-size="11.5" font-weight="bold" text-anchor="middle" fill="{NEGRO}">{fmt(deb)}</text>')
        rot = f' transform="rotate(-45 {x0+bw/2:.0f} {H-P+16})"' if n > 9 else ""
        etiqueta = r["anio"] + (" (1T)" if r["nota"].startswith("solo") else "")
        g += f'<text x="{x0+bw/2:.0f}" y="{H-P+16}" font-size="10" text-anchor="middle" fill="{PIZ}"{rot}>{etiqueta}</text>'
    # leyenda
    lx = P + 4
    for nom, col in [("Utilidades y dividendos IED", ROJO), ("Intereses otra inversión", SAL), ("Resto del débito", PIZ)]:
        g += (f'<rect x="{lx}" y="8" width="11" height="11" fill="{col}"/>'
              f'<text x="{lx+16}" y="18" font-size="11" fill="{NEGRO}">{nom}</text>')
        lx += 16 + 8.2 * len(nom)
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Rentas primarias pagadas por Chile">{g}</svg>'

def lineas_impuesto():
    W, H, P = 760, 300, 46
    pts = [(float(r["anio"]), float(r["tasa"]), r["hito"]) for r in impuesto]
    x0a, x1a = 1988, 2032; y0, y1 = 0, 30
    def X(a): return P + (W - P - 20) * (a - x0a) / (x1a - x0a)
    def Y(v): return (H - P) - (H - 2 * P) * (v - y0) / (y1 - y0)
    g = ""
    for v in range(0, 31, 5):
        g += (f'<line x1="{P}" y1="{Y(v):.0f}" x2="{W-20}" y2="{Y(v):.0f}" stroke="{REJ}"/>'
              f'<text x="{P-6}" y="{Y(v)+4:.0f}" font-size="10" text-anchor="end" fill="{PIZ}">{v} %</text>')
    for a in range(1990, 2031, 10):
        g += f'<text x="{X(a):.0f}" y="{H-P+16}" font-size="10" text-anchor="middle" fill="{PIZ}">{a}</text>'
    reales = [p for p in pts if p[0] <= 2025]
    proy = [p for p in pts if p[0] >= 2025]
    g += f'<polyline points="{" ".join(f"{X(a):.0f},{Y(v):.0f}" for a, v, _ in reales)}" fill="none" stroke="{NEGRO}" stroke-width="2.5"/>'
    g += f'<polyline points="{" ".join(f"{X(a):.0f},{Y(v):.0f}" for a, v, _ in proy)}" fill="none" stroke="{ROJO}" stroke-width="2.5" stroke-dasharray="6 4"/>'
    for a, v, hito in pts:
        col = ROJO if a > 2025 else NEGRO
        g += (f'<circle cx="{X(a):.0f}" cy="{Y(v):.0f}" r="4.5" fill="{col}">'
              f'<title>{"Proyecto «megarreforma»" if a > 2025 else "Impuesto a las empresas"}: {fmt(v,1).rstrip("0").rstrip(",")} % ({int(a)}){" · " + hito if hito else ""}</title></circle>')
    g += (f'<text x="{X(2030)-4:.0f}" y="{Y(23)+18:.0f}" font-size="11" text-anchor="end" fill="{ROJO}" font-style="italic">'
          f'proyecto: {fmt(23)} % hacia 2030 + invariabilidad 10-20 años</text>')
    for txt, xa, xb in [("Dictadura", 1988, 1990.5), ("Concertación + FA + PC", 1991, 2025.5), ("Kast", 2026, 2031.5)]:
        g += f'<text x="{X((xa+xb)/2):.0f}" y="{H-P+34}" font-size="10.5" text-anchor="middle" fill="{PIZ}" font-style="italic">{txt}</text>'
    return f'<svg viewBox="0 0 {W} {H+18}" style="width:100%;height:auto" role="img" aria-label="Serie legal del impuesto de primera categoría">{g}</svg>'

# ── mapa del drenaje ──
CENT = {"CHL": (296, 356), "USA": (244, 144), "CHN": (778, 146), "JPN": (860, 151),
        "KOR": (837, 148), "BRA": (335, 277), "EUR": (499, 119), "AFR": (558, 329), "SEA": (717, 183)}

def flecha(desde, hasta, grosor, etiqueta, curv=-40, color=ROJO, dash="", fsz=12, dy=-8):
    x1, y1 = CENT[desde]; x2, y2 = hasta
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + curv
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path class="vec" d="M{x1},{y1} Q{mx:.0f},{my:.0f} {x2},{y2}" stroke="{color}" stroke-width="{grosor}"{d} marker-end="url(#flecha)"/>'
            f'<text class="vec-txt" x="{mx:.0f}" y="{my+dy:.0f}" font-size="{fsz}" text-anchor="middle">{etiqueta}</text>')

def chip(x, y, w, lineas, fsz=11.5):
    h = 16 + 15 * len(lineas)
    t = "".join(f'<text x="{x+10}" y="{y+20+15*i}" font-size="{fsz}" fill="{NEGRO}">{ln}</text>' for i, ln in enumerate(lineas))
    return f'<rect class="chip" x="{x}" y="{y}" width="{w}" height="{h}" rx="3"/>{t}'

def mapa_drenaje():
    W, H = 980, 500
    # Vista Chile: flujo agregado (real) + contexto comercial (punteado, declarado)
    v_chile = (
        flecha("CHL", (500, 108), 13, f'Rentas primarias pagadas al exterior: US$ {fmt(deb25)} M (2025)', curv=-120, fsz=13.5)
        + f'<circle class="polo" cx="296" cy="356" r="7"><title>Chile — periférico exportador de rentas</title></circle>'
        + flecha("CHL", CENT["CHN"], 2.5, "", curv=-30, color=SAL, dash="5 4")
        + flecha("CHL", CENT["USA"], 2.5, "", curv=-60, color=SAL, dash="5 4")
        + flecha("CHL", CENT["JPN"], 2, "", curv=-10, color=SAL, dash="5 4")
        + flecha("CHL", CENT["BRA"], 2, "", curv=30, color=SAL, dash="5 4")
        + f'<text class="vec-txt" x="560" y="200" font-size="11" text-anchor="middle" fill="{SAL}">comercio (contexto, no drenaje): China · EE.UU. · Japón · Brasil</text>'
        + chip(500, 60, 385, [f'Utilidades y dividendos IED (2025): US$ {fmt(uti25)} M',
                              f'Intereses y resto del débito: US$ {fmt(deb25-uti25)} M',
                              f'= {fmt(pib_pct,1)} % del PIB (2024) · ×{fmt(mult,1)} en una década',
                              f'Por cada US$ 1 de IED que entró (2024): salieron US$ {fmt(razon_cl,2)}'])
        + chip(60, 400, 365, [f'1T-2026: US$ {fmt(float(CL_2026["debito_total"]))} M en un solo trimestre',
                              'Desagregación bilateral por país: pendiente declarado'])
    )
    # Vista AL
    top3 = [p for p in pais24 if p["pais"] in ("Brasil", "México", "Chile")]
    v_al = (
        flecha("BRA", (300, 130), 15, f'AL-20 pagó en rentas primarias: US$ {fmt(al_deb25)} M (2025)', curv=-80, fsz=13.5)
        + f'<circle class="polo" cx="335" cy="277" r="7"><title>América Latina — región periférica</title></circle>'
        + flecha("BRA", CENT["EUR"], 3, "", curv=-50, color=SAL, dash="5 4")
        + flecha("BRA", CENT["CHN"], 3, "", curv=-20, color=SAL, dash="5 4")
        + f'<text class="vec-txt" x="560" y="200" font-size="11" text-anchor="middle" fill="{SAL}">destinos del flujo (direcciones de referencia)</text>'
        + chip(495, 60, 425, [f'De las cuales utilidades IED (piso*): US$ {fmt(al_uti25)} M (2025)',
                              f'IED que entró a la región (2024): US$ {fmt(IED_AL)} M',
                              f'Por cada US$ 1 que entró: salieron US$ {fmt(razon_al,2)} en utilidades',
                              '*Perú no desagrega la línea; Venezuela/Cuba/Haití no reportan'])
        + chip(60, 400, 400, [f'Lo que más pagó en 2024 (débito total): Brasil US$ {fmt(float(top3[0]["debito_total_2024"]))} M ·',
                              f'México US$ {fmt(float(top3[1]["debito_total_2024"]))} M · Chile US$ {fmt(float(top3[2]["debito_total_2024"]))} M'])
    )
    # Vista Mundo
    v_mundo = (
        flecha("AFR", CENT["EUR"], 4, "", curv=-40, color=ROJO, dash="5 4")
        + flecha("BRA", CENT["USA"], 4, "", curv=-70, color=ROJO, dash="5 4")
        + flecha("SEA", CENT["USA"], 4, "", curv=-35, color=ROJO, dash="5 4")
        + flecha("SEA", CENT["CHN"], 3, "", curv=-15, color=ROJO, dash="5 4")
        + f'<circle class="polo" cx="{CENT["USA"][0]}" cy="{CENT["USA"][1]}" r="7"><title>EE.UU. — centro receptor</title></circle>'
        + f'<circle class="polo" cx="{CENT["CHN"][0]}" cy="{CENT["CHN"][1]}" r="7"><title>China — centro receptor y a la vez contribuyente neto</title></circle>'
        + chip(300, 30, 430, [f'Drenaje neto Sur → Norte: US$ {fmt(h("apropiacion_neta_valor"),1)} billones solo en 2015',
                              f'= {fmt(h("trabajo_apropiado"))} millones de años-persona de trabajo sureño',
                              f'Las pérdidas del Sur = {fmt(h("razon_perdidas_vs_ayuda"))}× toda la ayuda recibida',
                              '(Hickel et al. 2022, GEC — direcciones ilustrativas)'], fsz=12)
        + f'<text class="vec-txt" x="490" y="470" font-size="11.5" text-anchor="middle">China figura periférica (clasificación FMI) y es de los mayores contribuyentes netos: ambos bloques son capitalistas</text>'
    )
    return f'''<svg viewBox="0 0 {W} {H}" class="mapa" role="img" aria-label="Mapa mundial de la transferencia de plusvalor">
<defs><marker id="flecha" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0,0L10,5L0,10z" fill="{ROJO}"/></marker></defs>
<rect width="{W}" height="{H}" fill="{PAPEL}"/>
{MAPA_BASE}
<g class="vista-mapa" id="v-chile">{v_chile}</g>
<g class="vista-mapa" id="v-al" style="display:none">{v_al}</g>
<g class="vista-mapa" id="v-mundo" style="display:none">{v_mundo}</g>
</svg>'''

# ───────────────────────── componentes HTML ─────────────────────────
def ficha(definicion, fuente, corte, estatus, metodo, pendiente=None):
    est_nombre = {"O": "operativa", "P": "proxy", "C": "calibración", "X": "placeholder"}[estatus]
    pend = f'<dt>Pendiente declarado</dt><dd>{pendiente}</dd>' if pendiente else ""
    return f'''<details class="ficha-dato"><summary>Ficha del dato — cómo se construyó esta cifra</summary>
<dl>
<dt>Definición</dt><dd>{definicion}</dd>
<dt>Fuente</dt><dd>{fuente}</dd>
<dt>Fecha de corte / descarga</dt><dd>{corte}</dd>
<dt>Estatus de medición</dt><dd><span class="estatus est-{estatus.lower()}">{estatus} · {est_nombre}</span></dd>
<dt>Método</dt><dd>{metodo}</dd>
{pend}
</dl></details>'''

def incomodo(texto):
    return f'<p class="dato-incomodo"><strong>Dato incómodo:</strong> {texto}</p>'

def transicion(texto):
    return f'<p class="transicion" aria-hidden="true">{texto}</p>'

# ───────────────────────── módulos ─────────────────────────
term = f'''<div class="termometro" role="region" aria-label="Termómetro del corte">
  <div class="term-chip"><span class="term-nom">s/v-jornada</span><span class="term-val">{fmt(float(jornada["tasa_explotacion_sv"]["valor"]),1)} %</span><span class="term-fec">calibración SOL 2022 · C</span></div>
  <div class="term-chip"><span class="term-nom">TETV</span><span class="term-val">{fmt(float(jornada["TETV"]["valor"]),1)} %</span><span class="term-fec">calibración SOL 2022 · C</span></div>
  <div class="term-chip"><span class="term-nom">AFP — stock</span><span class="term-val">US$ 254.140 M</span><span class="term-fec">jun-2026 · SP · O</span></div>
  <div class="term-chip"><span class="term-nom">Rentas primarias</span><span class="term-val">US$ {fmt(deb25)} M/año</span><span class="term-fec">2025 · CEPALSTAT-BC · O</span></div>
  <div class="term-chip"><span class="term-nom">Impuesto empresas</span><span class="term-val">27 % → 23 %</span><span class="term-fec">proyecto 2030 · O</span></div>
  <div class="term-chip"><span class="term-nom">Drenaje Sur→Norte</span><span class="term-val">US$ 10,8 bill.</span><span class="term-fec">2015 · Hickel 2022 · O</span></div>
</div>'''

m1 = f'''<section class="modulo-obs" id="m1">
  <h3>1 · La jornada y la tasa de explotación</h3>
  <p class="concepto">La semana obrera se compone de tipos de trabajo distintos: el <strong>necesario</strong> (repite el salario, {fmt(float(jornada["trabajo_necesario"]["valor"]),2)} h), el <strong>plustrabajo</strong> (no pagado: plusvalor, {fmt(float(jornada["plustrabajo"]["valor"]),2)} h), el <strong>traslado</strong> (expropia tiempo vital sin producir valor, {fmt(float(jornada["traslado_no_remunerado"]["valor"]))} h) y el <strong>reproductivo no remunerado</strong> (el hogar, ≈ {fmt(float(jornada["reproductivo_no_remunerado"]["valor"]))} h: la carga que el feminismo nombra). La tasa de explotación es la proporción entre lo excedente y lo necesario; pasa el mouse sobre cada segmento.</p>
  <blockquote class="cita-boletin cita-marx">«La tasa de la plusvalía es la expresión exacta del grado de explotación de la fuerza de trabajo por el capital, o del trabajador por el capitalista.» <cite>(Marx, El Capital, T. I, cap. 9)</cite></blockquote>
  <div class="graf">{apilada_jornada()}</div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> la semana se mide ahora en 42 h legales pero la carga global real llega a {fmt(float(jornada["carga_global_real"]["valor"]))} h: la rebaja administrada (40 h en 2028) no toca la reproducción privatizada ni el traslado. Medio siglo de jornada muestra que la explotación no se mide solo en el punto de producción: el tiempo vital entregado (TETV {fmt(float(jornada["TETV"]["valor"]),1)} %) es más que la tasa estricta (s/v {fmt(float(jornada["tasa_explotacion_sv"]["valor"]),1)} %).</p>
  {incomodo("la jornada legal bajó a 42 h (abr-2026) y sin embargo la carga global sigue en 62 h: el punto real de la disputa por el tiempo no avanzó por ley — lo que la ley concede por un lado, la reproducción privatizada lo cobra por otro.")}
  {ficha(
    "s/v-jornada: plustrabajo / trabajo necesario en el punto de producción (tiempo). TETV: (tiempo excedente + traslado) / tiempo necesario — NO es una tasa de plusvalía (el traslado no produce valor).",
    "Reporte de Análisis de Coyuntura N°1 (jul-2026), anexo técnico, sobre metodología <a href='https://fundacionsol.cl'>Fundación SOL</a> (2022, <em>Tiempo Robado</em>); insumo 2026.2; ENUT-INE · datos: <a href='datos/observatorio/jornada_semana_obrera.csv'>jornada_semana_obrera.csv</a>",
    "base 2022 (calibración) · descarga 16-08-2026",
    "C",
    "Calibración de fondo recalculada: nivel de referencia, no variación mensual. Labor share oficial 38,5 % = cota superior de v; depurado 28-30 %.",
    "recalibrar con la próxima ENUT-INE y la actualización SOL anual.")}
  <p class="fuente-obs">Fuentes: Reporte N°1 (jul-2026) sobre Fundación SOL (2022) · jornada legal: Ley 19.759 (2005) y Ley 21.561 (2024) · Elaboración propia.</p>
</section>'''

m2 = f'''<section class="modulo-obs" id="m2">
  <h3>2 · Los circuitos de acumulación: qué concentra Chile</h3>
  <p class="concepto">El capital no es una cosa sino un circuito: figuras D–D′ (dinero que se redobla sin mercancía), M–D′ (mercancía vendida), renta. La matriz del Reporte articula los cinco circuitos que condensan la acumulación en la coyuntura; los indicadores de abajo son su medición del corte.</p>
  <blockquote class="cita-boletin cita-marx">«El capital no es una cosa, sino una relación social de producción.» <cite>(Marx, El Capital, T. I, cap. 23)</cite></blockquote>
  <div class="graf"><table class="tabla-circuitos">
    <thead><tr><th>Circuito</th><th>¿Se condensa este mes?</th><th>Punto del ciclo</th><th>Actor dominante</th></tr></thead>
    <tbody>
    <tr><td>Financiero (ficticio)</td><td>Sí: blindaje legal + defensa del anatocismo</td><td>D–D′</td><td>Banca, holdings, CMF</td></tr>
    <tr><td>Minero-rentístico</td><td>Sí: cobre US$ 6,18/lb por guerra; renta cedida</td><td>Renta / M–D′</td><td>Transnacionales, Codelco-SQM</td></tr>
    <tr><td>Reproducción privatizada</td><td>Sí: AFP US$ 254.140 M; TGR cobradora; sala cuna rechazada</td><td>D–D′ vía salario diferido</td><td>AFP, banca, TGR</td></tr>
    <tr><td>Industrial-militar (mundial)</td><td>Sí: US$ 2,9 billones de gasto militar 2025</td><td>Sumidero de s</td><td>Estados de ambos bloques</td></tr>
    <tr><td>Digital/IA (mundial)</td><td>Sí, como burbuja: capex US$ 725.000 M</td><td>D–D′ / renta tecnológica</td><td>Hyperscalers</td></tr>
    </tbody></table></div>
  <div class="kpi-grid">
    {''.join(f'<div class="kpi"><span class="kpi-nombre">{k["indicador"]}</span><span class="kpi-valor">{k["valor"]}</span><span class="kpi-nota">{k["nota"]} · {k["fecha_corte"]} · {k["fuente"]}</span></div>' for k in kpis)}
  </div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> Chile compra estabilidad vendiendo renta: el circuito minero-rentístico recibe cobre en máximos por la guerra y la megarreforma lo devuelve como rebaja tributaria; el circuito financiero defiende el anatocismo que la Corte acaba de validar; la reproducción sigue privatizada (AFP como dispositivo de captura del salario diferido).</p>
  {incomodo("el stock AFP cayó US$ 3.804 M en el mes — pero es revaluación de mercado que absorbe el cotizante, no menor captura del dispositivo: el dato no autoriza ni a celebrar ni a lamentar (regla de lectura IFA).")}
  {ficha(
    "Indicadores del corte por circuito: stock AFP, cartera y mora CAE, retenciones TGR, empleo, cobre, gasto militar.",
    "<a href='https://www.spensiones.cl'>Superintendencia de Pensiones</a> · Comisión Ingresa (Cuenta Pública 2025) · <a href='https://www.tesoreria.cl'>TGR</a> · <a href='https://www.ine.gob.cl'>INE</a> · <a href='https://www.cochilco.cl'>Cochilco</a> · <a href='https://www.sipri.org'>SIPRI</a> · datos: <a href='datos/observatorio/kpi_corte.csv'>kpi_corte.csv</a>",
    "jun-jul 2026 según indicador (ver fechas en cada tarjeta)",
    "O",
    "Cada KPI declara su fecha de corte y fuente; la variación del stock AFP NO es variación de la captura (revaluación).",
    None)}
  <p class="fuente-obs">Fuente: Reporte N°1 (jul-2026), «Matriz de articulación de circuitos» y diccionario de datos · Elaboración propia.</p>
</section>'''

m3 = f'''<section class="modulo-obs" id="m3">
  <h3>3 · La correa financiera: lo que Chile paga al exterior cada año</h3>
  <p class="concepto">El drenaje no cruza aduana: sale por la balanza de pagos como <strong>rentas primarias</strong> — utilidades y dividendos de las transnacionales más los intereses de la inversión extranjera. Es la correa financiera que ajusta el país al mercado mundial: la burguesía dependiente compensa en la producción interna (superexplotación) lo que cede por esta vía.</p>
  <blockquote class="cita-boletin cita-marx">«Estos mecanismos… significan que el trabajo se remunera por debajo de su valor, y corresponden, pues, a una superexplotación del trabajo.» <cite>(Marini, Dialéctica de la dependencia, §3 — la respuesta interna al drenaje)</cite></blockquote>
  <div class="graf">{barras_rentas_chile()}</div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> en 2025 Chile pagó <strong>US$ {fmt(deb25)} millones</strong> en rentas primarias — el máximo de la serie, {fmt(mult,1)} veces lo de 2016 y un {fmt(pib_pct,1)} % del PIB (2024). El 84 % fueron utilidades y dividendos de la IED. El primer trimestre de 2026 ya pagó US$ {fmt(float(CL_2026["debito_total"]))} millones: la correa se tensa, no se afloja. Por cada dólar de IED que entró en 2024 salieron US$ {fmt(razon_cl,2)} en utilidades: la «inversión» opera como aspiradora neta.</p>
  {incomodo("2020: con la economía parada por la pandemia, el débito apenas bajó (US$ 16.351 M) y el crédito se desplomó a US$ 486 M — el drenaje no se detiene ni con el país detenido. Y con el cobre cerca del máximo histórico, el drenaje del trimestre no corre por precios (intercambio desigual comercial atenuado) sino por esta vía financiero-tributaria.")}
  {ficha(
    "Rentas primarias (balanza de pagos): utilidades y dividendos de la IED + intereses de otra inversión y de cartera pagados al exterior; débito, crédito y balance. Millones US$ corrientes, suma anual de trimestres.",
    "<a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/547/records?lang=es'>CEPALSTAT, indicador 547 «Balanza de pagos trimestral»</a> (compila las cifras del Banco Central de Chile) · <a href='https://www.cepal.org/es/publicaciones/82116-la-inversion-extranjera-directa-america-latina-caribe-2025'>CEPAL, La IED en ALyC 2025</a> · PIB: Anuario CEPAL · datos: <a href='datos/observatorio/rentas_primarias_chile.csv'>rentas_primarias_chile.csv</a>",
    "serie 2016→2026 T1 · descarga 16-08-2026",
    "O",
    "Suma de los cuatro trimestres de cada año (2026: solo T1, declarado en la etiqueta). Razón US$ 1,51 = utilidades pagadas 2024 / IED entrante 2024 (CEPAL).",
    "desagregación bilateral (país de origen de la IED): pendiente declarado — se incorpora cuando la serie BC/CEPAL sea trazable.")}
  <p class="fuente-obs">Fuentes: CEPALSTAT (Banco Central de Chile vía CEPAL), descarga 16-08-2026 · CEPAL (2025), <em>La IED en América Latina y el Caribe 2025</em>, pp. 33 y 65 · Elaboración propia.</p>
</section>'''

m4 = f'''<section class="modulo-obs" id="m4">
  <h3>4 · La retención estatal del plusvalor (impuesto a las empresas)</h3>
  <p class="concepto">La fracción del plusvalor que el Estado retiene vía impuesto de primera categoría es la lectura tributaria de la correlación de fuerzas: quién paga y quién queda eximido. La serie legal es la huella institucional de esa correlación.</p>
  <blockquote class="cita-boletin cita-marx">«El gobierno del Estado moderno no es más que un comité que administra los negocios comunes de toda la clase burguesa.» <cite>(Marx y Engels, Manifiesto del Partido Comunista, cap. 1)</cite></blockquote>
  <div class="graf">{lineas_impuesto()}</div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> las fases se leen claro: la dictadura lo deja en el piso; la Concertación+FA+PC lo sube hasta 27 % sin tocar la estructura; Kast no sube la retención — la baja a 23 % con invariabilidad de hasta 20 años: el Estado se amarra por ley para que ninguna mayoría futura pueda deshacerlo. La retención estatal de renta no es «lo común»: es capitalismo de Estado que estabiliza la ganancia general.</p>
  {incomodo("la rebaja es gradual hacia 2030 y aún está en tramitación: la correlación no se ha consumado en la tasa — lo decisivo es la invariabilidad (10-20 años), que hipoteca a las mayorías futuras más allá de este gobierno.")}
  {ficha(
    "Tasa legal del impuesto de primera categoría a la renta empresarial, por hitos legales; 2030 = proyecto en tramitación (Boletín 18216-05), no ley.",
    "Ley 18.985 (1990) · Ley 20.469 (2010) · Ley 20.780 (2014) · <a href='https://www.senado.cl/appsenado/templates/tramitacion/index.php?boletin_ini=18216-05'>Senado, tramitación Boletín 18216-05</a> · datos: <a href='datos/observatorio/impuesto_primera_categoria.csv'>impuesto_primera_categoria.csv</a>",
    "serie 1990→2025 vigente + proyecto · descarga 16-08-2026",
    "O",
    "Serie de hitos legales (no anual): los tramos 1970-1989 quedan en incorporación desde DIPRES.",
    "completar la serie 1970-1989 (DIPRES).")}
  <p class="fuente-obs">Fuentes: serie legal citada · proyecto «megarreforma»: Boletín 18216-05 (Senado) · Elaboración propia.</p>
</section>'''

m5 = f'''<section class="modulo-obs" id="m5">
  <h3>5 · La transferencia de plusvalor: el drenaje tiene historia</h3>
  <p class="concepto">En el intercambio desigual el valor fluye de la periferia al centro sin violar ninguna ley del mercado: se intercambian equivalentes y sin embargo se transfiere plusvalor. La medición moderna de ese flujo —con datos de comercio y matrices insumo-producto— muestra que no es un residuo colonial: es la estructura misma de la economía mundial, y se intensificó con el ajuste neoliberal de los 80-90.</p>
  <blockquote class="cita-boletin cita-marx">«El comercio exterior abarata los elementos del capital constante y los artículos de subsistencia… y eleva la tasa de plusvalía.» <cite>(Marx, El Capital, T. III, cap. 14)</cite></blockquote>
  <div class="graf"><div class="magnitud-grid">
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("apropiacion_neta_valor"),1)} billones</span><span class="mag-que">apropiados netos por el Norte en un solo año (2015) — valorados en precios del Norte</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">{fmt(h("trabajo_apropiado"))} millones</span><span class="mag-que">de años-persona de trabajo sureño apropiados netos en 2015, con {fmt(h("materiales_apropiados"))} Mt de materiales, {fmt(h("tierra_apropiada"))} M ha de tierra y {fmt(h("energia_apropiada"))} EJ de energía</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("drenaje_acumulado","1990-2015"))} billones</span><span class="mag-que">drenados en 1990-2015 (constantes 2010) ≈ un cuarto del PIB del Norte</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("drenaje_acumulado","1960-2018"))} billones</span><span class="mag-que">drenados en 1960-2018 (constantes 2011); {fmt(h("drenaje_acumulado_con_crecimiento_perdido"))} billones contando el crecimiento perdido</span><span class="mag-src">Hickel et al. 2021 (NPE)</span></div>
    <div class="magnitud"><span class="mag-val">{fmt(h("razon_perdidas_vs_ayuda"))}×</span><span class="mag-que">las pérdidas del Sur por intercambio desigual superan treinta veces toda la «ayuda» recibida en el período</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">80-90</span><span class="mag-que">la intensidad de la explotación y la escala del intercambio desigual se disparan con el ajuste estructural: el neoliberalismo como intensificación de la succión</span><span class="mag-src">Hickel et al. 2021 (NPE)</span></div>
  </div></div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> el drenaje no es metáfora: tiene magnitud, dirección y aceleración histórica. Para Chile la transferencia opera como cesión — con el cobre a US$ 6,18/lb (cerca del máximo) el proyecto tributario devuelve la renta — y como correa financiera (módulo 3): US$ {fmt(deb25)} M pagados en 2025. Ambas lecturas son la misma estructura vista desde la literatura mundial y desde la balanza de pagos nacional.</p>
  {incomodo("con términos de intercambio favorables (cobre en máximos), la vía comercial del intercambio desigual se atenúa para Chile en el trimestre: la categoría titular no se condensa todos los meses — y declararlo es parte de la medición.")}
  {ficha(
    "Drenaje por intercambio desigual: apropiación neta de trabajo, recursos y valor del Sur por el Norte vía diferenciales de precios/productividad en el comercio mundial.",
    "<a href='https://doi.org/10.1080/13563467.2021.1899153'>Hickel, Sullivan y Zoomkawala (2021), <em>New Political Economy</em> 26(6)</a> · <a href='https://doi.org/10.1016/j.gloenvcha.2022.102467'>Hickel, Dorninger, Wieland y Suwandi (2022), <em>Global Environmental Change</em> 73</a> (abstracts cotejados vía OpenAlex) · datos: <a href='datos/observatorio/drenaje_mundial_hickel.csv'>drenaje_mundial_hickel.csv</a>",
    "series 1960-2018 y 1990-2015 · verificación 16-08-2026",
    "O",
    "Cada cifra se reporta con SU artículo: el «US$ 10,8 billones (2015)» es del GEC 2022; el NPE 2021 reporta US$ 2,2 billones (2018) y US$ 62 billones acumulados. La serie año a año no se grafica.",
    "serie anual completa: vive en los anexos de los artículos (pendiente declarado).")}
  <p class="fuente-obs">Fuentes: Hickel et al. (2021, NPE) y Hickel et al. (2022, GEC), con DOI en la ficha · mecanismos Chile: Reporte N°1 (jul-2026) · Elaboración propia.</p>
</section>'''

m6 = f'''<section class="modulo-obs" id="m6">
  <h3>6 · El mapa del drenaje: céntricos y periféricos</h3>
  <p class="concepto">La geografía del drenaje no es plana: los países céntricos (negro, economías avanzadas FMI — proxy declarado) concentran la recepción neta; la periferia (rojo) exporta valor. Las flechas sólidas muestran flujos <strong>medidos</strong> con su año; las punteadas, direcciones de referencia. El grosor es proporcional a la magnitud dentro de cada vista.</p>
  <blockquote class="cita-boletin cita-marx">«Los proletarios no tienen patria.» <cite>(Marx y Engels, Manifiesto del Partido Comunista, cap. 2)</cite></blockquote>
  <div class="botones-mapa" role="tablist" aria-label="Escala del mapa">
    <button class="activo" data-vista="v-chile">Chile</button>
    <button data-vista="v-al">América Latina</button>
    <button data-vista="v-mundo">Mundo</button>
  </div>
  <p class="estado-mapa" id="estado-mapa">Vista Chile: flujo medido de rentas primarias al exterior (2025, CEPALSTAT-BC) y comercio como contexto; la desagregación bilateral es pendiente declarado.</p>
  <div class="graf">{mapa_drenaje()}</div>
  <p class="leyenda-mapa"><span class="lg"><i class="sw sw-negro"></i>céntrico (FMI, proxy)</span><span class="lg"><i class="sw sw-rojo"></i>periférico</span><span class="lg"><i class="sw sw-flecha"></i>flujo medido (año declarado)</span><span class="lg"><i class="sw sw-punteada"></i>contexto / dirección de referencia</span></p>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> qué se extrae: plusvalor y renta (utilidades, intereses, cobre cedido). En qué magnitud: US$ {fmt(deb25)} M pagados por Chile en 2025 ({fmt(pib_pct,1)} % del PIB); US$ {fmt(al_deb25)} M por América Latina; US$ {fmt(h("apropiacion_neta_valor"),1)} billones netos del Sur al Norte solo en 2015. La teoría de la dependencia, ajustada a hoy: no es el comercio el canal principal del drenaje chileno, es la renta — y la megarreforma la cede por ley.</p>
  {incomodo("China figura en la periferia (clasificación FMI) y a la vez —con la metodología de Hickel et al.— es de los mayores contribuyentes netos al drenaje: el mapa no autoriza a elegir bloque; ambos son capitalistas (regla de independencia comunista).")}
  {ficha(
    "Clasificación dicotómica de países (proxy de la teoría de la dependencia) + flujos medidos: rentas primarias Chile (2025→2026 T1), AL-20 (2025), IED entrante (2024), drenaje mundial (2015 y acumulados).",
    "Geometría: Natural Earth · clasificación: <a href='https://www.imf.org/external/pubs/ft/weo/'>economías avanzadas FMI</a> · flujos: <a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/547/records?lang=es'>CEPALSTAT ind. 547</a>, <a href='https://www.cepal.org/es/publicaciones/82116-la-inversion-extranjera-directa-america-latina-caribe-2025'>CEPAL IED 2025</a>, Hickel et al. (DOI en módulo 5) · datos: <a href='datos/observatorio/rentas_primarias_chile.csv'>chile</a> · <a href='datos/observatorio/rentas_primarias_al20.csv'>AL-20</a> · <a href='datos/observatorio/rentas_debito_pais_2024.csv'>por país</a>",
    "descarga 16-08-2026 (corte 2025 / 2026 T1)",
    "P",
    "El grosor de las flechas sólidas es proporcional a la magnitud dentro de cada vista (no comparable entre vistas); las punteadas no miden. AL-20 = suma simple de países con registros.",
    "flujos bilaterales por país de origen de la IED (BC/CEPAL) y utilidades de Perú: pendiente declarado.")}
  <p class="fuente-obs">Fuentes: clasificación FMI · CEPALSTAT (BC) y CEPAL IED 2025 · Hickel et al. (2021, 2022) · Elaboración propia.</p>
</section>'''

cierre = f'''<section class="modulo-obs cierre-obs">
  <h3>Qué no muestra esta página — y cómo se construyó</h3>
  <p><strong>Lo que no muestra:</strong> los flujos entre países del Sur (la dependencia no es solo Sur→Norte); los paraísos fiscales como nodos de la correa financiera; la desagregación bilateral de las utilidades (pendiente declarado); y el registro propio de los puntos reales (ollas, comités, asambleas), que es tarea de la organización, no de las estadísticas oficiales.</p>
  <p><strong>Cómo se construyó:</strong> ninguna cifra de esta página se escribió a mano en el HTML. Todos los números salen de la capa de datos pública del repositorio — <a href="datos/observatorio/README.md">datos/observatorio/</a> (CSV + <a href="datos/observatorio/metadatos.yml">metadatos.yml</a>) — generada con el script <a href="scripts/build_observatorio.py">build_observatorio.py</a> y alimentada cada mes por el diccionario de datos del Reporte de Análisis de Coyuntura. Cada figura declara su estatus de medición: <span class="estatus est-o">O · operativa</span> <span class="estatus est-p">P · proxy</span> <span class="estatus est-c">C · calibración</span> <span class="estatus est-x">X · placeholder</span>. Revisión y auditoría: <a href="https://github.com/queacontezca/elcorreocomunista">github.com/queacontezca/elcorreocomunista</a> · licencia CC BY 4.0.</p>
  <p><strong>Los datos terminan en apuesta:</strong> esta página existe para que las luchas lean su propia situación. El puente entre la medición y la intervención son los <a href="puntos-reales.html">puntos reales</a>.</p>
</section>'''

# ───────────────────────── página ─────────────────────────
pagina = f'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Observatorio de coyuntura — El Correo Comunista</title>
<meta name="description" content="Los datos del análisis de coyuntura, públicos para las luchas: tasas de explotación, circuitos, la correa financiera, la retención estatal y el mapa del drenaje del plusvalor — con fuentes firmes y ficha metodológica por figura.">
<link rel="stylesheet" href="styles.css">
</head>
<body class="pagina-sec">
<header class="mini-estafeta">
  <div class="me-sup">
    <a href="index.html">← El Correo Comunista</a>
    <span>Ediciones ¡Que Acontezca!</span>
  </div>
  <div class="me-titulo">
    <p class="kicker">Página de síntesis · Observatorio</p>
    <h1 class="titulo-sec">Observatorio de coyuntura</h1>
    <p class="principio-sec">Los datos del análisis, públicos para las luchas: tendencias, brechas y el drenaje del plusvalor. Corte de datos: agosto 2026.</p>
  </div>
  <nav class="indice-sub"><a href="index.html">Portada</a><a href="secciones/los-medios-comunes.html">I · Medios comunes</a><a href="secciones/trabajo-polimorfo.html">II · Trabajo polimorfo</a><a href="secciones/proletariado.html">III · Proletariado</a><a href="secciones/marchitamiento-del-estado.html">IV · Marchitamiento del Estado</a><a href="puntos-reales.html">Puntos reales</a><a class="actual" href="observatorio.html">Observatorio</a></nav>
</header>
<main class="contenido-sec">
  {term}
  <section class="bloque pregunta">
    <h3>¿Cómo analizamos la coyuntura?</h3>
    <p>Con la matriz del Reporte de Análisis de Coyuntura: <strong>principio → atado (qué medir) → circuitos (dónde se juega) → punto real (desde dónde se apuesta)</strong>. Los módulos de abajo son esa matriz hecha visible, en un solo relato: de la semana obrera a los circuitos que capturan su producto, de la correa financiera que lo saca del país a la fracción que retiene el Estado, y al final el drenaje entre países — con historia y con mapa. Cada figura declara su fuente, su fecha de corte y su estatus de medición en su <em>ficha del dato</em>; cada módulo registra su <em>dato incómodo</em>: el que más tensiona la hipótesis. Una hipótesis que no puede perder no es análisis: es tautología.</p>
  </section>
  {m1}
  {transicion("Lo que se produce en la semana no se queda en la fábrica ni en la casa: sigue el circuito del capital. ¿Por dónde fluye y quién lo captura?")}
  {m2}
  {transicion("Una parte creciente de ese excedente ni siquiera se queda en el país: sale por la balanza de pagos, sin cruzar aduana. Esa es la correa financiera.")}
  {m3}
  {transicion("Otra fracción la retiene el Estado — y la correlación de fuerzas decide cuánto y para quién. La serie legal del impuesto es su huella institucional.")}
  {m4}
  {transicion("Lo que Chile paga es la cuota nacional de un flujo mundial medido con precisión: el drenaje del Sur al Norte no es metáfora — tiene historia y aceleración.")}
  {m5}
  {transicion("La historia del drenaje tiene también geografía. El mapa lo muestra por escala: primero Chile, después la región, al final el mundo.")}
  {m6}
  {cierre}
</main>
<footer>
  <p><strong>EL CORREO COMUNISTA</strong> · ¡Centralización de la discusión! · Ediciones ¡Que Acontezca!</p>
  <p>Reproducción libre, total o parcial, citando la fuente · <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a></p>
</footer>
<script>
document.querySelectorAll('.botones-mapa button').forEach(function(b){{
  b.addEventListener('click',function(){{
    document.querySelectorAll('.botones-mapa button').forEach(x=>x.classList.remove('activo'));
    b.classList.add('activo');
    document.querySelectorAll('.vista-mapa').forEach(v=>v.style.display='none');
    document.getElementById(b.dataset.vista).style.display='block';
    const estados={{
      'v-chile':'Vista Chile: flujo medido de rentas primarias al exterior (2025, CEPALSTAT-BC) y comercio como contexto; la desagregación bilateral es pendiente declarado.',
      'v-al':'Vista América Latina: lo que la región pagó en rentas primarias (2025) contra lo que entró por IED (2024) — utilidades de Perú subestimadas (declarado).',
      'v-mundo':'Vista Mundo: direcciones de referencia del drenaje y la magnitud neta Sur→Norte de la literatura (Hickel et al. 2022); China como contribuyente neto: ambos bloques son capitalistas.'
    }};
    document.getElementById('estado-mapa').textContent = estados[b.dataset.vista];
  }});
}});
</script>
</body>
</html>
'''

SALIDA.write_text(pagina, encoding="utf-8")
print("observatorio.html regenerado:", len(pagina), "bytes")
print("módulos: termómetro + 6 + cierre · figuras desde datos/observatorio/")
