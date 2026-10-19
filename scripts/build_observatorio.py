# -*- coding: utf-8 -*-
"""
build_observatorio.py — Genera observatorio.html desde la capa de datos.

REGLA DE ORO (continuidad): ninguna cifra de la página se escribe a mano aquí;
todo número sale de datos/observatorio/*.csv (fuente única de verdad, compartida
con el Reporte de Análisis de Coyuntura). Los textos analíticos sí son editoriales.

Uso:  python3 scripts/build_observatorio.py
      (desde la raíz del sitio; stdlib pura, sin dependencias)
"""
import csv, json, pathlib, re

RAIZ = pathlib.Path(__file__).resolve().parent.parent
DATOS = RAIZ / "datos" / "observatorio"
SALIDA = RAIZ / "observatorio.html"
PORTADA = RAIZ / "index.html"

# ───────────────────────── utilidades ─────────────────────────
def lee_csv(nombre):
    with open(DATOS / nombre, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def fmt(v, dec=0):
    """Punto de miles, coma decimal (es-CL)."""
    if v is None: return "—"
    s = f"{v:,.{dec}f}"
    return s.replace(",", "X").replace(".", ",").replace("X", ".")

# Tokens del sistema «Ediciones ¡Que Acontezca!» (rojo-ladrillo, salmon, tinta, pizarra, azul-palido, papel)
ROJO, SAL, NEGRO, PIZ, REJ, PAPEL = "#bf4245", "#e69089", "#000000", "#43454a", "#bbc7d1", "#FBF7E9"

# ───────────────────────── datos ─────────────────────────
rentas_cl = lee_csv("rentas_primarias_chile.csv")
rentas_tri = lee_csv("rentas_primarias_chile_trimestral.csv")
rentas_al = lee_csv("rentas_primarias_al20.csv")
pais24 = lee_csv("rentas_debito_pais_2024.csv")
hickel = lee_csv("drenaje_mundial_hickel.csv")
ied = lee_csv("ied_entradas_cepal.csv")
impuesto = lee_csv("impuesto_primera_categoria.csv")
jornada = {r["concepto"]: r for r in lee_csv("jornada_semana_obrera.csv")}
kpis = lee_csv("kpi_corte.csv")
gasto = lee_csv("gasto_social_chile.csv")
ied_pais = lee_csv("renta_ied_chile_pais_2024.csv")
pib_min = lee_csv("pib_y_mineria_chile.csv")
ajuste = lee_csv("ajuste_fiscal_2026.csv")
sol_des = lee_csv("desempleo_integral_sol.csv")
sind = lee_csv("sindicalizacion_por_rama.csv")
pib_act = lee_csv("pib_por_actividad_chile.csv")
tnr = lee_csv("trabajo_no_remunerado_chile.csv")[-1]
ied_comp = {r["componente"]: float(r["usd_millones"]) for r in lee_csv("ied_componentes_chile.csv")}
tributos = lee_csv("ingresos_tributarios_chile.csv")
MAPA_BASE = (DATOS / "mapa_base_paises.svg").read_text(encoding="utf-8")

def h(indicador, periodo=None):
    for r in hickel:
        if r["indicador"] == indicador and (periodo is None or r["periodo"] == periodo):
            return float(r["valor"])
    raise KeyError(indicador)

def kpi(nombre):
    """Fila cruda de kpi_corte.csv por indicador (KeyError si no existe)."""
    for r in kpis:
        if r["indicador"] == nombre:
            return r
    raise KeyError(nombre)

def kpi_valor(nombre):
    """Valor numérico principal de un KPI (float). Falla si está pendiente (estatus X sin valor)."""
    r = kpi(nombre)
    if not r["valor_numerico"]:
        raise ValueError(f"«{nombre}» no tiene valor_numerico — está pendiente (estatus {r['estatus']})")
    return float(r["valor_numerico"])

def _fmt_kpi_row(r):
    """Cifra formateada de una fila cruda de kpi_corte.csv según su propia plantilla."""
    if not r["valor_numerico"]:
        return "fuente pendiente"
    s = r["plantilla"].replace("{v}", fmt(float(r["valor_numerico"]), int(r["decimales"] or 0)))
    if r["valor2_numerico"]:
        s = s.replace("{v2}", fmt(float(r["valor2_numerico"]), int(r["decimales2"] or 0)))
    return s

def kpi_fmt(nombre):
    """Cifra formateada de un KPI por nombre (p. ej. 'US$ 254.140 M')."""
    return _fmt_kpi_row(kpi(nombre))

CL_2025 = next(r for r in rentas_cl if r["anio"] == "2025")
CL_2024 = next(r for r in rentas_cl if r["anio"] == "2024")
CL_2026 = next(r for r in rentas_cl if r["anio"] == "2026")
CL_2016 = next(r for r in rentas_cl if r["anio"] == "2016")
AL_2025 = next(r for r in rentas_al if r["anio"] == "2025")
AL_2024 = next(r for r in rentas_al if r["anio"] == "2024")
IED_AL = float(next(r["valor"] for r in ied if r["indicador"] == "AL_entradas_ied"))
IED_CL = float(next(r["valor"] for r in ied if r["indicador"] == "Chile_entradas_ied"))
PIB25 = float(next(r["pib_usd_millones"] for r in pib_min if r["anio"] == "2025"))
PIB24 = float(next(r["pib_usd_millones"] for r in pib_min if r["anio"] == "2024"))
MIN25 = float(next(r["mineria_pct_pib"] for r in pib_min if r["anio"] == "2025"))
AJ_TOTAL = float(next(r["valor"] for r in ajuste if r["indicador"] == "ajuste_total_anunciado"))
AJ_ANO = float(next(r["valor"] for r in ajuste if r["indicador"] == "ajuste_primer_anio"))

deb25 = float(CL_2025["debito_total"]); uti25 = float(CL_2025["ied_utilidades_dividendos"])
int25 = float(CL_2025["intereses_otra_inversion"]); deb16 = float(CL_2016["debito_total"])
cre25 = float(CL_2025["credito_total"]); neto25 = deb25 - cre25
al_deb25 = float(AL_2025["debito_total"]); al_uti25 = float(AL_2025["ied_utilidades_piso"])
razon_cl = float(CL_2024["ied_utilidades_dividendos"]) / IED_CL
razon_al = float(AL_2024["ied_utilidades_piso"]) / IED_AL
pib_pct24 = float(CL_2024["debito_total"]) / PIB24 * 100
pib_pct25 = deb25 / PIB25 * 100
mult = deb25 / deb16
afp_stock = kpi_valor("AFP — stock de fondos")  # datos/observatorio/kpi_corte.csv

# Flujo trimestral (CEPALSTAT 547): semestre en curso contra el mismo semestre del año anterior
def tri(anio, q, campo="debito_total"):
    return float(next(r[campo] for r in rentas_tri if r["anio"] == str(anio) and r["trimestre"] == str(q)))
TRI_ULT = rentas_tri[-1]                                   # último trimestre disponible
TRI_ANIO, TRI_Q = int(TRI_ULT["anio"]), int(TRI_ULT["trimestre"])
deb_parcial = float(CL_2026["debito_total"]); uti_parcial = float(CL_2026["ied_utilidades_dividendos"])
deb_parcial_prev = sum(tri(TRI_ANIO - 1, q) for q in range(1, TRI_Q + 1))
uti_parcial_prev = sum(tri(TRI_ANIO - 1, q, "ied_utilidades_dividendos") for q in range(1, TRI_Q + 1))
var_deb = (deb_parcial / deb_parcial_prev - 1) * 100
var_uti = (uti_parcial / uti_parcial_prev - 1) * 100
neto_parcial = -float(CL_2026["balance_neto"])
deb_tri_ult = float(TRI_ULT["debito_total"])
tasa_final = float(impuesto[-1]["tasa"]); anio_final = impuesto[-1]["anio"]
PRES27 = float(next(r["valor"] for r in ajuste if r["indicador"] == "presupuesto_2027_crecimiento_gasto"))
afp_pct = afp_stock / PIB25 * 100

def ip(destino):
    return next(r for r in ied_pais if r["destino"] == destino)
V_EUR = float(ip("Europa")["neto"]); V_USA = float(ip("Estados Unidos")["neto"])
V_CAN = float(ip("Canadá")["pagado"]); V_ASI = float(ip("Asia (Japón)")["neto"])
V_OCE = float(ip("Oceanía")["neto"]); V_NOA = float(ip("Otros y no asignados")["pagado"])
INT_NOIED = float(CL_2024["debito_total"]) - float(CL_2024["ied_utilidades_dividendos"])

# Tasa del impuesto, una fila por año: cada año lleva la última tasa legal registrada en el CSV
# (los años intermedios se rellenan hacia adelante; el CSV solo registra hitos).
ANIO_HOY = 2026
ANIO_FIN_TASA = int(impuesto[-1]["anio"]) + 1          # un año más: la tasa final ya en régimen
def tasa_por_anio():
    hitos = {int(r["anio"]): float(r["tasa"]) for r in impuesto}
    filas, tasa = [], None
    for a in range(int(impuesto[0]["anio"]), ANIO_FIN_TASA + 1):
        if a in hitos: tasa = hitos[a]
        filas.append({"anio": a, "tasa": tasa, "proy": a > ANIO_HOY})
    return filas
TASAS = tasa_por_anio()
# cambios legales que se marcan con línea segmentada: (año desde el que rige en el CSV, rótulo)
LEYES = [(2012, "Ley 20.469"), (2015, "Ley 20.780"), (ANIO_HOY + 1, "Ofensiva burguesa (Kast)")]
def titulo_tasa(r):
    base = f'Impuesto a las empresas {r["anio"]}: {fmt(r["tasa"],1).rstrip("0").rstrip(",")} %'
    if r["proy"]: base += " · calendario de la ley promulgada el 09-10-2026"
    return base

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

def barras_circuitos():
    """Peso de los circuitos nacionales (% del PIB, proxy declarada) + chips mundiales."""
    W, H = 760, 218
    items = [
        ("Reproducción privatizada", "stock de fondos AFP (stock, no flujo) · 2025", afp_pct, ROJO),
        ("Minero-rentístico", "explotación de minas y canteras · % del PIB · 2025", MIN25, NEGRO),
        ("Correa financiera", "rentas primarias pagadas al exterior · % del PIB · 2025", pib_pct25, SAL),
    ]
    P = 300; mx = 80.0
    g = ""
    for i, (nom, proxy, v, col) in enumerate(items):
        y = 18 + i * 44
        w = (W - P - 90) * v / mx
        g += (f'<text x="{P-8}" y="{y+11}" font-size="12.5" text-anchor="end" fill="{NEGRO}" font-weight="bold">{nom}</text>'
              f'<text x="{P-8}" y="{y+26}" font-size="10" text-anchor="end" fill="{PIZ}">{proxy}</text>'
              f'<rect x="{P}" y="{y}" width="{w:.0f}" height="28" fill="{col}"><title>{nom}: {fmt(v,1)} % del PIB</title></rect>'
              f'<text x="{P+w+8:.0f}" y="{y+19}" font-size="13" font-weight="bold" fill="{NEGRO}">{fmt(v,1)} %</text>')
    y2 = 18 + 3 * 44 + 8
    g += (f'<text x="20" y="{y2+12}" font-size="11" fill="{PIZ}" font-style="italic">Circuitos mundiales (sobredeterminan a los nacionales):</text>'
          f'<rect x="20" y="{y2+20}" width="350" height="40" fill="#f7f3ea" stroke="{REJ}"/>'
          f'<text x="30" y="{y2+36}" font-size="11.5" fill="{NEGRO}">Industrial-militar: gasto militar mundial {kpi_fmt("Gasto militar mundial")} ({kpi("Gasto militar mundial")["fecha_corte"]}, {kpi("Gasto militar mundial")["fuente"]})</text>'
          f'<text x="30" y="{y2+51}" font-size="11.5" fill="{PIZ}" font-style="italic">Digital/IA: capex hyperscalers — {kpi_fmt("Digital/IA — capex hyperscalers")} (ver ficha del dato)</text>')
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Peso de los circuitos de acumulación en Chile">{g}</svg>'

def barras_rentas_chile():
    """Barras apiladas: utilidades IED + intereses + resto del débito, 2016→año en curso (parcial)."""
    W, H, P = 760, 320, 52
    filas = [r for r in rentas_cl]
    mx = max(float(r["debito_total"]) for r in filas) * 1.12
    n = len(filas); slot = (W - P - 16) / n; bw = slot * 0.66
    def y(v): return (H - P) - (H - 2 * P) * v / mx
    g = ""
    for t in range(0, 5):
        vv = (mx / 1.12) * t / 4
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
        etiqueta = r["anio"] + (f" ({TRI_Q}T)" if r["nota"].startswith("parcial") else "")
        g += f'<text x="{x0+bw/2:.0f}" y="{H-P+16}" font-size="10" text-anchor="middle" fill="{PIZ}"{rot}>{etiqueta}</text>'
    lx = P + 4
    for nom, col in [("Utilidades y dividendos IED", ROJO), ("Intereses otra inversión", SAL), ("Resto del débito", PIZ)]:
        g += (f'<rect x="{lx}" y="8" width="11" height="11" fill="{col}"/>'
              f'<text x="{lx+16}" y="18" font-size="11" fill="{NEGRO}">{nom}</text>')
        lx += 16 + 8.2 * len(nom)
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Rentas primarias pagadas por Chile">{g}</svg>'

def barras_trimestrales():
    """Flujo trimestral de rentas primarias pagadas por Chile (débito), con la parte de utilidades IED."""
    W, H, P = 760, 250, 52
    filas = rentas_tri
    mx = max(float(r["debito_total"]) for r in filas) * 1.15
    n = len(filas); slot = (W - P - 16) / n; bw = slot * 0.7
    def y(v): return (H - P) - (H - P - 30) * v / mx
    g = ""
    for t in range(0, 5):
        vv = (mx / 1.15) * t / 4
        g += (f'<line x1="{P}" y1="{y(vv):.0f}" x2="{W-16}" y2="{y(vv):.0f}" stroke="{REJ}"/>'
              f'<text x="{P-6}" y="{y(vv)+4:.0f}" font-size="10" text-anchor="end" fill="{PIZ}">{fmt(vv/1000,1)}</text>')
    g += f'<text x="{P}" y="14" font-size="10" fill="{PIZ}" font-style="italic">miles de millones US$ por trimestre</text>'
    for i, r in enumerate(filas):
        x0 = P + slot * i + (slot - bw) / 2
        deb = float(r["debito_total"]); uti = float(r["ied_utilidades_dividendos"])
        en_curso = r["anio"] == str(TRI_ANIO)
        g += (f'<rect x="{x0:.0f}" y="{y(deb):.0f}" width="{bw:.0f}" height="{H-P-y(deb):.0f}" fill="{PIZ}">'
              f'<title>Rentas primarias pagadas {r["anio"]} T{r["trimestre"]}: US$ {fmt(deb)} M</title></rect>'
              f'<rect x="{x0:.0f}" y="{y(uti):.0f}" width="{bw:.0f}" height="{H-P-y(uti):.0f}" fill="{ROJO if en_curso else SAL}">'
              f'<title>Utilidades y dividendos IED {r["anio"]} T{r["trimestre"]}: US$ {fmt(uti)} M</title></rect>')
        if en_curso or deb >= deb_tri_ult:
            g += f'<text x="{x0+bw/2:.0f}" y="{y(deb)-6:.0f}" font-size="11" font-weight="bold" text-anchor="middle" fill="{NEGRO}">{fmt(deb)}</text>'
        g += f'<text x="{x0+bw/2:.0f}" y="{H-P+14}" font-size="10" text-anchor="middle" fill="{PIZ}">T{r["trimestre"]}</text>'
        if r["trimestre"] == "1":
            g += f'<text x="{x0:.0f}" y="{H-P+29}" font-size="10.5" font-weight="bold" fill="{NEGRO}">{r["anio"]}</text>'
    lx = P + 250
    for nom, col in [(f"Utilidades y dividendos IED ({TRI_ANIO} en rojo)", SAL), ("Resto del débito", PIZ)]:
        g += f'<rect x="{lx}" y="5" width="11" height="11" fill="{col}"/><text x="{lx+16}" y="15" font-size="11" fill="{NEGRO}">{nom}</text>'
        lx += 16 + 7.2 * len(nom)
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Flujo trimestral de rentas primarias pagadas por Chile">{g}</svg>'

def panel_doble_retencion_gasto():
    """Panel A: tasa de retención (serie legal). Panel B: gasto público social (% PIB). Eje de años compartido."""
    W, P = 760, 46
    HA0, HA1 = 22, 165      # panel A vertical (tasa 0-32 %)
    HB0, HB1 = 254, 432     # panel B vertical (gasto 0-27 %)
    H = 470
    # bloque entre paneles (coordenadas explícitas, de arriba hacia abajo, para que
    # anotación · título B · leyenda B no se pisen entre sí):
    ANN_Y1, ANN_Y2 = HA1 + 22, HA1 + 37   # anotación «megarreforma», 2 líneas
    TITULO_B_Y = HB0 - 32                  # título del panel B
    LEYENDA_B_RECT_Y, LEYENDA_B_TXT_Y = HB0 - 24, HB0 - 15   # leyenda del panel B
    x0a, x1a = 1988, 2032
    def X(a): return P + (W - P - 20) * (a - x0a) / (x1a - x0a)
    def YA(v): return HA1 - (HA1 - HA0) * v / 32
    def YB(v): return HB1 - (HB1 - HB0) * v / 27
    g = ""
    # rejillas y rótulos
    for v in range(0, 33, 8):
        g += (f'<line x1="{P}" y1="{YA(v):.0f}" x2="{W-20}" y2="{YA(v):.0f}" stroke="{REJ}"/>'
              f'<text x="{P-6}" y="{YA(v)+4:.0f}" font-size="10" text-anchor="end" fill="{PIZ}">{v} %</text>')
    for v in range(0, 28, 5):
        g += (f'<line x1="{P}" y1="{YB(v):.0f}" x2="{W-20}" y2="{YB(v):.0f}" stroke="{REJ}"/>'
              f'<text x="{P-6}" y="{YB(v)+4:.0f}" font-size="10" text-anchor="end" fill="{PIZ}">{v} %</text>')
    for a in range(1990, 2031, 7):
        g += f'<text x="{X(a):.0f}" y="{H-8}" font-size="10" text-anchor="middle" fill="{PIZ}">{a}</text>'
    g += (f'<text x="{P}" y="{HA0-6}" font-size="11.5" font-weight="bold" fill="{NEGRO}">A · Lo que el Estado retiene: impuesto a las empresas (tasa legal por año, %; en rojo, lo ya legislado hacia {ANIO_FIN_TASA})</text>'
          f'<text x="{P}" y="{TITULO_B_Y}" font-size="11.5" font-weight="bold" fill="{NEGRO}">B · Lo que el Estado solventa: gasto público social (% del PIB, Gobierno Central)</text>')
    # Panel A: retención — una columna por año; líneas segmentadas en los cambios legales
    paso = X(2001) - X(2000); bwA = paso * 0.78
    for r in TASAS:
        col = ROJO if r["proy"] else PIZ
        g += (f'<rect x="{X(r["anio"]) - bwA/2:.1f}" y="{YA(r["tasa"]):.1f}" width="{bwA:.1f}" height="{HA1 - YA(r["tasa"]):.1f}" fill="{col}">'
              f'<title>{titulo_tasa(r)}</title></rect>')
    for anio, rot in LEYES:
        xl = X(anio) - paso / 2; fin = anio > ANIO_HOY
        g += (f'<line x1="{xl:.1f}" y1="{HA0}" x2="{xl:.1f}" y2="{HA1}" stroke="{ROJO if fin else NEGRO}" stroke-width="1.2" stroke-dasharray="4 3"/>'
              f'<text x="{xl + (4 if anio == 2015 else -4):.1f}" y="{HA0 + 9}" font-size="9.5" text-anchor="{"start" if anio == 2015 else "end"}" fill="{ROJO if fin else NEGRO}">{rot}</text>')
    g += (f'<text x="{X(ANIO_FIN_TASA) + paso/2:.0f}" y="{YA(tasa_final) - 5:.0f}" font-size="10.5" text-anchor="end" fill="{ROJO}" font-weight="bold">{fmt(tasa_final)} %</text>')
    # Panel B: gasto social
    series = [("gasto_social_total", "Gasto social total", NEGRO, 2.5, ""),
              ("salud", "Salud", ROJO, 2, ""),
              ("educacion", "Educación", SAL, 2, ""),
              ("vivienda_y_servicios_comunitarios", "Vivienda y serv. comunitarios", PIZ, 1.5, "5 3")]
    lx = P + 4
    for clave, nom, col, sw, dash in series:
        pts_b = [(float(r["anio"]), float(r[clave])) for r in gasto]
        d = f' stroke-dasharray="{dash}"' if dash else ""
        g += f'<polyline points="{" ".join(f"{X(a):.0f},{YB(v):.0f}" for a, v in pts_b)}" fill="none" stroke="{col}" stroke-width="{sw}"{d}/>'
        for a, v in pts_b:
            g += f'<circle cx="{X(a):.0f}" cy="{YB(v):.0f}" r="3" fill="{col}"><title>{nom}: {fmt(v,1)} % del PIB ({int(a)})</title></circle>'
        g += f'<rect x="{lx}" y="{LEYENDA_B_RECT_Y}" width="10" height="10" fill="{col}"/><text x="{lx+14}" y="{LEYENDA_B_TXT_Y}" font-size="10.5" fill="{NEGRO}">{nom}</text>'
        lx += 14 + 7.6 * len(nom)
    # hito del ajuste 2026 (cruza ambos paneles)
    g += (f'<line x1="{X(2026.5):.1f}" y1="{HA1}" x2="{X(2026.5):.1f}" y2="{HB1}" stroke="{ROJO}" stroke-width="1.2" stroke-dasharray="4 3"/>'
          f'<text x="{X(2026)-8:.0f}" y="{ANN_Y1}" font-size="11" text-anchor="end" fill="{ROJO}" font-weight="bold">megarreforma promulgada + ajuste de US$ {fmt(AJ_TOTAL)} M (2026):</text>'
          f'<text x="{X(2026)-8:.0f}" y="{ANN_Y2}" font-size="11" text-anchor="end" fill="{ROJO}">PGU, gratuidad y bonos en revisión</text>')
    return f'<svg viewBox="0 0 {W} {H}" style="width:100%;height:auto" role="img" aria-label="Retención estatal y gasto público social">{g}</svg>'

# ── mapa del drenaje ──
CENT = {"CHL": (296, 356), "USA": (244, 144), "CAN": (201, 94), "CHN": (778, 146),
        "JPN": (860, 151), "BRA": (335, 277), "EUR": (510, 105), "AFR": (558, 329), "SEA": (717, 183)}

def flecha(desde, hasta, grosor, etiqueta, curv=-40, color=ROJO, dash="", fsz=14, dy=-10):
    x1, y1 = CENT[desde]; x2, y2 = hasta
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + curv
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path class="vec" d="M{x1},{y1} Q{mx:.0f},{my:.0f} {x2},{y2}" stroke="{color}" stroke-width="{grosor}"{d} marker-end="url(#flecha)"/>'
            + (f'<text class="vec-txt" x="{mx:.0f}" y="{my+dy:.0f}" font-size="{fsz}" text-anchor="middle">{etiqueta}</text>' if etiqueta else ""))

def chip(x, y, w, lineas, fsz=13.5):
    h = 18 + 17.5 * len(lineas)
    t = "".join(f'<text x="{x+11}" y="{y+22+17.5*i}" font-size="{fsz}" fill="{NEGRO}">{ln}</text>' for i, ln in enumerate(lineas))
    return f'<rect class="chip" x="{x}" y="{y}" width="{w}" height="{h:.0f}" rx="3"/>{t}'

def mapa_drenaje():
    W, H = 980, 500
    # Vista Chile: vectores NETOS reales por destino (BC 2024) + intereses + contexto China
    v_chile = (
        flecha("CHL", CENT["EUR"], 13, f'Europa: neto US$ {fmt(V_EUR)} M', curv=-85, fsz=14.5)
        + flecha("CHL", CENT["USA"], 9, f'EE.UU.: neto US$ {fmt(V_USA)} M', curv=-70, fsz=14.5)
        + flecha("CHL", CENT["CAN"], 7, f'Canadá: pagado US$ {fmt(V_CAN)} M', curv=-95, fsz=14.5)
        + flecha("CHL", CENT["JPN"], 2.5, f'Asia: neto US$ {fmt(V_ASI)} M', curv=-15, fsz=14.5)
        + flecha("CHL", CENT["CHN"], 2, "", curv=-35, color=SAL, dash="5 4")
        + f'<text class="vec-txt" x="600" y="230" font-size="13" text-anchor="middle" fill="{SAL}">China: 1er socio comercial — origen marginal de la renta (3 %)</text>'
        + f'<circle class="polo" cx="296" cy="356" r="7"><title>Chile — periférico exportador de rentas</title></circle>'
        + chip(450, 30, 508, [f'Vector de transferencia neta (2024, BC): pagado − recibido',
                              f'Intereses no-IED: US$ {fmt(INT_NOIED)} M → banca y bonistas internacionales',
                              f'Otros y no asignados: US$ {fmt(V_NOA)} M · minería: 43 % de la renta IED',
                              f'Grosor ∝ magnitud (1 px ≈ US$ 400 M; mínimo visual)'])
        + chip(55, 400, 430, [f'Neto total 2025 (todas las rentas, CEPALSTAT):',
                              f'US$ {fmt(neto25)} M = sale US$ {fmt(deb25)} M − entra US$ {fmt(cre25)} M',
                              f'Canadá: recibido no desagregado — se reporta lo pagado'])
    )
    # Vista AL
    top3 = [p for p in pais24 if p["pais"] in ("Brasil", "México", "Chile")]
    v_al = (
        flecha("BRA", (300, 130), 15, f'AL-20 pagó en rentas primarias: US$ {fmt(al_deb25)} M (2025)', curv=-80, fsz=15)
        + f'<circle class="polo" cx="335" cy="277" r="7"><title>América Latina — región periférica</title></circle>'
        + flecha("BRA", CENT["EUR"], 3, "", curv=-50, color=SAL, dash="5 4")
        + flecha("BRA", CENT["CHN"], 3, "", curv=-20, color=SAL, dash="5 4")
        + f'<text class="vec-txt" x="580" y="210" font-size="13" text-anchor="middle" fill="{SAL}">destinos del flujo (direcciones de referencia)</text>'
        + chip(455, 40, 480, [f'De las cuales utilidades IED (piso*): US$ {fmt(al_uti25)} M (2025)',
                              f'IED que entró a la región (2024): US$ {fmt(IED_AL)} M',
                              f'Por cada US$ 1 que entró: salieron US$ {fmt(razon_al,2)} en utilidades',
                              '*Perú no desagrega la línea; Venezuela/Cuba/Haití no reportan'])
        + chip(55, 400, 470, [f'Lo que más pagó en 2024 (débito total): Brasil US$ {fmt(float(top3[0]["debito_total_2024"]))} M',
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
        + chip(270, 28, 480, [f'Drenaje neto Sur → Norte: US$ {fmt(h("apropiacion_neta_valor"),1)} billones solo en 2015',
                              f'= {fmt(h("trabajo_apropiado"))} millones de años-persona de trabajo sureño',
                              f'Las pérdidas del Sur = {fmt(h("razon_perdidas_vs_ayuda"))}× toda la ayuda recibida',
                              '(Hickel et al. 2022, GEC — direcciones ilustrativas)'], fsz=13.5)
        + f'<text class="vec-txt" x="490" y="472" font-size="13" text-anchor="middle">China figura periférica (clasificación FMI) y es de los mayores contribuyentes netos: ambos bloques son capitalistas</text>'
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

def chispa(valores, tipo="linea"):
    """Mini serie para una ficha del termómetro (sin ejes: solo la forma de la tendencia)."""
    W, H = 120, 30
    mn, mx = min(valores), max(valores); rango = (mx - mn) or 1
    n = len(valores)
    if tipo == "barras":
        bw = W / n
        g = "".join(f'<rect x="{i*bw+1:.1f}" y="{H - (H-3)*v/mx:.1f}" width="{bw-2:.1f}" height="{(H-3)*v/mx:.1f}"/>' for i, v in enumerate(valores))
    else:
        pts = " ".join(f"{i*(W-4)/(n-1)+2:.1f},{H-3-(H-6)*(v-mn)/rango:.1f}" for i, v in enumerate(valores))
        g = f'<polyline points="{pts}"/>'
    return f'<svg class="chispa chispa-{tipo}" viewBox="0 0 {W} {H}" aria-hidden="true" preserveAspectRatio="none">{g}</svg>'

CH_RENTAS = chispa([float(r["debito_total"]) for r in rentas_tri], "barras")
CH_IMPUESTO = chispa([float(r["tasa"]) for r in impuesto])

# ───────────────────────── módulos ─────────────────────────
term = f'''<p class="term-titulo"><strong>El termómetro del corte:</strong> las seis cifras clave de este Observatorio, cada una con su fecha y su estatus de medición (O · operativa — dato oficial fresco · C · calibración — nivel de fondo). Cada ficha lleva a su módulo.</p>
<div class="termometro" id="termometro" role="region" aria-label="Termómetro del corte">
  <a class="term-chip" href="#m1"><span class="term-nom">s/v-jornada</span><span class="term-val">{fmt(float(jornada["tasa_explotacion_sv"]["valor"]),1)} %</span><span class="term-fec">calibración SOL 2022 · C</span></a>
  <a class="term-chip" href="#m1"><span class="term-nom">TETV</span><span class="term-val">{fmt(float(jornada["TETV"]["valor"]),1)} %</span><span class="term-fec">calibración SOL 2022 · C</span></a>
  <a class="term-chip" href="#m2"><span class="term-nom">AFP — stock</span><span class="term-val">{kpi_fmt("AFP — stock de fondos")}</span><span class="term-fec">{kpi("AFP — stock de fondos")["fecha_corte"]} · SP · O</span></a>
  <a class="term-chip" href="#m3"><span class="term-nom">Rentas primarias</span><span class="term-val">US$ {fmt(deb_parcial)} M</span><span class="term-fec">{TRI_Q} trim. de {TRI_ANIO} · +{fmt(var_deb)} % interanual · CEPALSTAT-BC · O</span>{CH_RENTAS}</a>
  <a class="term-chip" href="#m4"><span class="term-nom">Impuesto empresas</span><span class="term-val">{fmt(float(next(r["tasa"] for r in impuesto if r["anio"]=="2026")),0)} % → {fmt(tasa_final,0)} %</span><span class="term-fec">ley promulgada 09-10-2026 · rige 2027-{anio_final} · O</span>{CH_IMPUESTO}</a>
  <a class="term-chip" href="#m5"><span class="term-nom">Drenaje Sur→Norte</span><span class="term-val">US$ {fmt(h("apropiacion_neta_valor"),1)} bill.</span><span class="term-fec">2015 · Hickel 2022 · O</span></a>
</div>'''

m1 = f'''<section class="modulo-obs" id="m1">
  <h3>1 · La jornada y la tasa de explotación</h3>
  <p class="concepto">La semana obrera se compone de tipos de trabajo distintos: el <strong>necesario</strong> (repite el salario, {fmt(float(jornada["trabajo_necesario"]["valor"]),2)} h), el <strong>plustrabajo</strong> (no pagado: plusvalor, {fmt(float(jornada["plustrabajo"]["valor"]),2)} h), el <strong>traslado</strong> (expropia tiempo vital sin producir valor, {fmt(float(jornada["traslado_no_remunerado"]["valor"]))} h) y el <strong>reproductivo no remunerado</strong> (el hogar, ≈ {fmt(float(jornada["reproductivo_no_remunerado"]["valor"]))} h: la carga que el feminismo nombra). La tasa de explotación es la proporción entre lo excedente y lo necesario; pasa el cursor o toca cada segmento.</p>
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
  <p class="fuente-obs">Fuentes: Reporte N°1 (jul-2026) sobre Fundación SOL (2022) · jornada legal: Ley 19.759 (2005) y Ley 21.561 (2024) · Elaboración propia. Ver también: Harnecker y Uribe, <em>Cuadernos de Educación Popular 02 — Explotación capitalista</em> (1971), pp. 23-24 (fórmula operativa de la tasa de explotación).</p>
</section>'''

m2 = f'''<section class="modulo-obs" id="m2">
  <h3>2 · Los circuitos de acumulación: qué concentra Chile y con qué peso</h3>
  <p class="concepto">El capital no es una cosa sino un circuito: figuras D–D′ (dinero que se redobla sin mercancía), M–D′ (mercancía vendida), renta. La cartografía completa tiene <strong>siete circuitos</strong> (financiero, industrial-militar, minero-rentístico, logístico, agroindustrial, digital/IA y reproducción privatizada). La tabla los muestra los siete: <strong>cinco con peso medido en esta coyuntura</strong>, y dos — logístico y agroindustrial — todavía sin dato propio, marcados como pendientes en vez de omitidos. Los circuitos no son sectores del PIB ni un ranking: se interpenetran — el capital ficticio atraviesa a todos. Desde 1981 la estructura chilena es <em>primario-exportador + financiero-AFP</em>; los dos circuitos mundiales la sobredeterminan.</p>
  <blockquote class="cita-boletin cita-marx">«El capital no es una cosa, sino una relación social de producción.» <cite>(Marx, El Capital, T. I, cap. 23)</cite></blockquote>
  <div class="graf">{barras_circuitos()}</div>
  <div class="graf"><table class="tabla-circuitos">
    <thead><tr><th>Circuito</th><th>¿Se condensa este mes?</th><th>Punto del ciclo</th><th>Actor dominante</th></tr></thead>
    <tbody>
    <tr><td>Financiero (ficticio)</td><td>Sí: blindaje legal + defensa del anatocismo</td><td>D–D′</td><td>Banca, holdings, CMF</td></tr>
    <tr><td>Minero-rentístico</td><td>Sí: cobre {kpi_fmt("Cobre")} ({kpi("Cobre")["fecha_corte"]}); renta cedida por ley</td><td>Renta / M–D′</td><td>Transnacionales, Codelco-SQM</td></tr>
    <tr><td>Reproducción privatizada</td><td>Sí: AFP {kpi_fmt("AFP — stock de fondos")}; TGR cobradora; sala cuna rechazada</td><td>D–D′ vía salario diferido</td><td>AFP, banca, TGR</td></tr>
    <tr><td>Industrial-militar (mundial)</td><td>Sí: {kpi_fmt("Gasto militar mundial")} de gasto militar {kpi("Gasto militar mundial")["fecha_corte"]}</td><td>Sumidero de s</td><td>Estados de ambos bloques</td></tr>
    <tr><td>Digital/IA (mundial)</td><td>Como burbuja — <span class="estatus est-x">X · pendiente</span> {kpi_fmt("Digital/IA — capex hyperscalers")}</td><td>D–D′ / renta tecnológica</td><td>Hyperscalers</td></tr>
    <tr><td>Logístico</td><td>No medido aún — <span class="estatus est-x">X · placeholder</span></td><td>M–D′ (circulación)</td><td>Navieras, puertos, logística global</td></tr>
    <tr><td>Agroindustrial</td><td>No medido aún — <span class="estatus est-x">X · placeholder</span></td><td>M–D′ / renta de la tierra</td><td>Agroexportadoras, forestales</td></tr>
    </tbody></table></div>
  <div class="kpi-grid">
    {''.join(f'<div class="kpi"><span class="kpi-nombre">{k["indicador"]}</span><span class="kpi-valor">{_fmt_kpi_row(k)}</span><span class="kpi-nota">{k["nota"]} · {k["fecha_corte"]} · {k["fuente"]} <span class="estatus est-{k["estatus"].lower()}">{k["estatus"]}</span></span></div>' for k in kpis)}
  </div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> Chile compra estabilidad vendiendo renta: el circuito minero-rentístico ({fmt(MIN25,1)} % del PIB) recibe cobre en máximos ({kpi_fmt("Cobre")}) y la megarreforma, promulgada el 9 de octubre, lo devuelve como rebaja tributaria; la reproducción privatizada es el circuito de mayor peso nacional (stock AFP ≈ {fmt(afp_pct)} % del PIB: el salario diferido convertido en capital ficticio); la correa financiera saca del país el {fmt(pib_pct25,1)} % del PIB cada año.</p>
  {incomodo(f"el stock AFP ({kpi_fmt('AFP — stock de fondos')}, {kpi('AFP — stock de fondos')['fecha_corte']}) está por debajo del corte anterior de este Observatorio (US$ 254.140 M, jun-2026) aunque agosto fue un mes de rentabilidad positiva — es variación de mercado y de tipo de cambio que absorbe el cotizante, no menor captura del dispositivo: el dato no autoriza ni a celebrar ni a lamentar (regla de lectura IFA). Y el desempleo sube a {kpi_fmt('Desempleo / informalidad').split(' /')[0]} con el cobre en máximos: el precio de la renta no baja a la mesa de quien trabaja.")}
  {ficha(
    "Peso por circuito nacional: stock AFP / PIB; minería / PIB; rentas primarias pagadas / PIB. Los circuitos mundiales se reportan en magnitud (no son % del PIB chileno). Indicadores del corte por circuito: stock AFP, cartera y mora CAE, retenciones TGR, empleo, cobre, gasto militar.",
    "<a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/2215/records?lang=es'>CEPALSTAT ind. 2215 (PIB por actividad, compila BC)</a> · <a href='https://www.spensiones.cl'>Superintendencia de Pensiones</a> · Comisión Ingresa · <a href='https://www.tesoreria.cl'>TGR</a> · <a href='https://www.ine.gob.cl'>INE</a> · <a href='https://www.cochilco.cl'>Cochilco</a> · <a href='https://www.sipri.org'>SIPRI</a> · datos: <a href='datos/observatorio/pib_y_mineria_chile.csv'>pib_y_mineria_chile.csv</a> · <a href='datos/observatorio/kpi_corte.csv'>kpi_corte.csv</a>",
    "2025 / ago-oct 2026 según indicador (CAE: dic-2025 · TGR: jul-2026, sin dato nuevo) · actualización 11-10-2026",
    "O",
    "Cada barra usa la proxy declarada bajo su rótulo (los circuitos NO son sectores del PIB: el gráfico mide peso, no composición). La variación del stock AFP NO es variación de la captura (revaluación).",
    "participación de servicios financieros estricta (sin inmobiliarias): pendiente por trazabilidad BC. Circuitos logístico y agroindustrial: sin serie propia todavía — declarados como pendientes (X) en la tabla, no omitidos.")}
  <p class="fuente-obs">Fuente: Reporte N°1 (jul-2026), «Matriz de articulación de circuitos» y diccionario de datos · CEPALSTAT (BC) · Elaboración propia. Ver también: Dussel, <em>16 tesis de economía política</em> (2014), Tesis 6 [6.6-6.7] y Tesis 7 [7.3-7.5] (ciclo y fetichización del capital); Katz, <em>Bajo el imperio del capital</em> («circuitos de la acumulación»); Rikap, <em>Teoría de la dependencia digital</em> (circuito digital/IA); Dussel, Tesis 11 [11.6] «La guerra como negocio» (circuito industrial-militar).</p>
</section>'''

m3 = f'''<section class="modulo-obs" id="m3">
  <h3>3 · La correa financiera: cuánto plusvalor sale del país</h3>
  <p class="concepto"><strong>Esto es exactamente eso: el plusvalor que sale.</strong> Las utilidades y dividendos de la IED son plusvalor producido en Chile y apropiado por el capital extranjero (ganancia empresarial repatriada); los intereses son una <em>fracción del plusvalor</em> cedida al capital a interés — banca y bonistas de afuera, incluidos los organismos internacionales (Marx, T. III: la ganancia se escinde en ganancia empresarial e interés; el interés no es una categoría aparte). Es una <strong>medición conservadora (piso)</strong>: no incluye el intercambio desigual vía precios — la ventana de Hickel en el módulo 5 — ni los precios de transferencia intraempresa. Dos ventanas sobre la misma transferencia: no se suman, se complementan.</p>
  <blockquote class="cita-boletin cita-marx">«Estos mecanismos… significan que el trabajo se remunera por debajo de su valor, y corresponden, pues, a una superexplotación del trabajo.» <cite>(Marini, Dialéctica de la dependencia — la respuesta interna al drenaje)</cite></blockquote>
  <div class="graf">{barras_rentas_chile()}</div>
  <p class="concepto"><strong>El flujo, trimestre a trimestre:</strong> la serie anual esconde el ritmo. Vista por trimestres, la correa muestra su aceleración: el segundo trimestre de {TRI_ANIO} es el de mayor salida de rentas de toda la serie de CEPALSTAT para Chile (que parte en 1993).</p>
  <div class="graf">{barras_trimestrales()}</div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> en 2025 Chile pagó <strong>US$ {fmt(deb25)} millones</strong> en rentas primarias — el máximo de la serie, {fmt(mult,1)} veces lo de 2016 y un {fmt(pib_pct25,1)} % del PIB (2025). El 84 % fueron utilidades y dividendos de la IED. En los dos primeros trimestres de {TRI_ANIO} ya salieron <strong>US$ {fmt(deb_parcial)} millones</strong> — un {fmt(var_deb)} % más que en el mismo semestre de {TRI_ANIO-1} (US$ {fmt(deb_parcial_prev)} M) —, de los cuales US$ {fmt(uti_parcial)} M son utilidades y dividendos de la IED ({fmt(var_uti)} % más): la correa se tensa, no se afloja. El trimestre abril-junio marcó US$ {fmt(deb_tri_ult)} M, el más alto registrado. El neto del semestre (lo que sale menos lo que entra) es US$ {fmt(neto_parcial)} M. Por cada dólar de IED que entró en 2024 salieron US$ {fmt(razon_cl,2)} en utilidades: la «inversión» opera como aspiradora neta. Y el vector neto (lo que sale menos lo que entra) es US$ {fmt(neto25)} M al año: las AFP ganan US$ {fmt(cre25)} M en el exterior — el salario diferido financiarizado compensa una fracción de lo que se llevan las transnacionales.</p>
  {incomodo("2020: con la economía parada por la pandemia, el débito apenas bajó (US$ 16.351 M) y el crédito se desplomó a US$ 486 M — el drenaje no se detiene ni con el país detenido. Y con el cobre cerca del máximo histórico, el drenaje del trimestre no corre por precios (intercambio desigual comercial atenuado) sino por esta vía financiero-tributaria.")}
  {ficha(
    "Rentas primarias (balanza de pagos): utilidades y dividendos de la IED + intereses de otra inversión y de cartera pagados al exterior; débito, crédito y balance (= vector neto). Millones US$ corrientes, suma anual de trimestres. Revisión conceptual: las utilidades son plusvalor repatriado; los intereses son fracción del plusvalor (la ganancia se escinde, T. III). Piso: excluye intercambio desigual vía precios y precios de transferencia.",
    "<a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/547/records?lang=es'>CEPALSTAT, indicador 547 «Balanza de pagos trimestral»</a> (compila las cifras del Banco Central de Chile) · <a href='https://www.cepal.org/es/publicaciones/82116-la-inversion-extranjera-directa-america-latina-caribe-2025'>CEPAL, La IED en ALyC 2025</a> · datos: <a href='datos/observatorio/rentas_primarias_chile.csv'>rentas_primarias_chile.csv</a> · <a href='datos/observatorio/rentas_primarias_chile_trimestral.csv'>rentas_primarias_chile_trimestral.csv</a>",
    f"serie anual 2016→{TRI_ANIO} (parcial: {TRI_Q} trimestres) · serie trimestral 2023 T1→{TRI_ANIO} T{TRI_Q} · descarga 11-10-2026",
    "O",
    f"Suma de los cuatro trimestres de cada año ({TRI_ANIO}: {TRI_Q} trimestres acumulados, declarado en la etiqueta; el primer trimestre fue revisado al alza por la fuente respecto del corte de agosto: US$ 8.071 M → US$ 8.386 M). Comparación semestral: mismos trimestres del año anterior. Razón US$ 1,51 = utilidades pagadas 2024 / IED entrante 2024 (CEPAL). Neto = débito − crédito.",
    "ninguno en la serie; la desagregación por destino está en el mapa (módulo 5) con datos BC.")}
  <p class="fuente-obs">Fuentes: CEPALSTAT (Banco Central de Chile vía CEPAL), descarga 11-10-2026 · CEPAL (2025), <em>La IED en América Latina y el Caribe 2025</em>, pp. 33 y 65 · Elaboración propia. Ver también: Dussel, <em>16 tesis de economía política</em>, Tesis 10 [10.4] «Transferencia de plusvalor como esencia de la dominación social globalizada».</p>
</section>'''

# Gasto social (serie CEPALSTAT 3127): inicio, máximo (pandemia) y último año, para el texto del módulo 4 y la síntesis
GS0, GS1 = gasto[0], gasto[-1]
GSMAX = max(gasto, key=lambda r: float(r["gasto_social_total"]))
GS19 = next(r for r in gasto if r["anio"] == "2019")  # último año previo a la pandemia

m4 = f'''<section class="modulo-obs" id="m4">
  <h3>4 · La retención estatal del plusvalor — y las condiciones fundamentales que solventa</h3>
  <p class="concepto">La fracción del plusvalor que el Estado retiene vía impuesto de primera categoría es la lectura tributaria de la correlación de fuerzas. El cruce es directo: <strong>mientras más retención, más condiciones fundamentales (salud, educación, vivienda) se pueden solventar</strong> — y al revés: la apuesta de Kast, ya convertida en ley, es reducir la retención y devolver ese terreno al mercado. Dos paneles, mismo eje de tiempo: arriba lo que el Estado retiene; abajo lo que el Estado solventa.</p>
  <blockquote class="cita-boletin cita-marx">«El gobierno del Estado moderno no es más que un comité que administra los negocios comunes de toda la clase burguesa.» <cite>(Marx y Engels, Manifiesto del Partido Comunista, cap. 1)</cite></blockquote>
  <div class="graf">{panel_doble_retencion_gasto()}</div>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> la retención subió del 15 % al 27 % y con ella el gasto social total pasó del {fmt(float(GS0["gasto_social_total"]),1)} % del PIB ({GS0["anio"]}) a un máximo de {fmt(float(GSMAX["gasto_social_total"]),1)} % ({GSMAX["anio"]}, año de gasto de pandemia) y quedó en {fmt(float(GS1["gasto_social_total"]),1)} % en {GS1["anio"]}, último año disponible (de {GS0["anio"]} a {GS1["anio"]}: salud {fmt(float(GS0["salud"]),1)} → {fmt(float(GS1["salud"]),1)}; educación {fmt(float(GS0["educacion"]),1)} → {fmt(float(GS1["educacion"]),1)}; vivienda plano en {fmt(float(GS1["vivienda_y_servicios_comunitarios"]),1)}: la gran ausente). La megarreforma — promulgada el 9 de octubre de 2026 como Ley de Reconstrucción Nacional y Desarrollo Económico y Social — revierte ambos lados del panel: −4 puntos de retención en tres tramos (25,5 % en 2027, 24 % en 2028, {fmt(tasa_final)} % en {anio_final}) con invariabilidad tributaria por contrato de 10, 15 o 20 años, y el primer Presupuesto del gobierno llega con el gasto creciendo apenas {fmt(PRES27,1)} % para 2027. Se suma un ajuste de US$ {fmt(AJ_TOTAL)} millones (US$ {fmt(AJ_ANO)} M el primer año) con PGU, gratuidad y bonos en revisión. Es un solo punto de los principios — el gasto social es capitalismo de Estado, no lo común — pero es el terreno que el mercado quiere recuperar.</p>
  {incomodo(f"el gasto social total no venía cayendo antes de Kast: el {fmt(float(GSMAX['gasto_social_total']),1)} % del PIB de {GSMAX['anio']} fue gasto de emergencia (protección social {fmt(float(GSMAX['proteccion_social']),1)} %) y, retirado, quedó en {fmt(float(GS1['gasto_social_total']),1)} % en {GS1['anio']}, sobre el {fmt(float(GS19['gasto_social_total']),1)} % de {GS19['anio']}. Lo que sí venía bajando es la educación: {fmt(float(GS19['educacion']),1)} % del PIB en {GS19['anio']} → {fmt(float(GS1['educacion']),1)} % en {GS1['anio']}. De 2024-2025 no hay serie publicada: el recorte del total aún no se puede medir.")}
  {ficha(
    "Panel A: tasa legal del impuesto de primera categoría por hitos legales (2027-2029 = calendario de la ley promulgada el 09-10-2026; al 11-10-2026 falta su publicación en el Diario Oficial, por eso se dibuja punteado y sin número de ley). Panel B: gasto público social del Gobierno Central en % del PIB, por función (clasificación COFOG). Unidades separadas por panel (tasa % ≠ % del PIB).",
    "Leyes 18.985 / 20.469 / 20.780 · <a href='https://www.senado.cl/appsenado/templates/tramitacion/index.php?boletin_ini=18216-05'>Senado, Boletín 18216-05</a> · <a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/3127/records?lang=es'>CEPALSTAT ind. 3127 (compila DIPRES)</a> · promulgación y calendario: prensa (Emol 09-10-2026, CNN Chile) · ajuste y Presupuesto 2027: prensa (BioBioChile, Ex-ante, El Desconcierto, mar-abr 2026; Emol y Meganoticias, 05-10-2026) · datos: <a href='datos/observatorio/impuesto_primera_categoria.csv'>impuesto_primera_categoria.csv</a> · <a href='datos/observatorio/gasto_social_chile.csv'>gasto_social_chile.csv</a> · <a href='datos/observatorio/ajuste_fiscal_2026.csv'>ajuste_fiscal_2026.csv</a>",
    "gasto social 2012-2023 (último año disponible) · ley promulgada 09-10-2026 · Presupuesto 2027 ingresado 30-09-2026 · actualización 11-10-2026",
    "O",
    "Serie de hitos legales (panel A); serie anual COFOG Gobierno Central (panel B). 2020-2021 con gasto de pandemia.",
    "gasto social 2024-2025 (DIPRES aún no publica la serie en CEPALSTAT); tramos 1970-1989 del impuesto; número de ley y texto del Diario Oficial (se reemplaza la cita de prensa cuando se publique).")}
  <p class="fuente-obs">Fuentes: serie legal citada · CEPALSTAT (DIPRES) · prensa citada en ficha · Elaboración propia. Ver también: Lenin, <em>El Estado y la revolución</em>; Harnecker, <em>Los conceptos elementales del materialismo histórico</em>, cap. 7, apartado «La doble función del Estado».</p>
</section>'''

m5 = f'''<section class="modulo-obs" id="m5">
  <h3>5 · La transferencia de plusvalor: historia y mapa del drenaje</h3>
  <p class="concepto">En el intercambio desigual el valor fluye de la periferia al centro sin violar ninguna ley del mercado: se intercambian equivalentes y sin embargo se transfiere plusvalor. La medición moderna muestra que no es un residuo colonial sino la estructura misma de la economía mundial — y que se intensificó con el ajuste neoliberal de los 80-90. La historia tiene también geografía: <strong>el mapa de abajo es la figura de este módulo</strong>, por escala — primero Chile, después la región, al final el mundo. <em>Revisión conceptual del vector: transferencia neta = lo que sale − lo que entra; las utilidades son plusvalor repatriado y los intereses su fracción financiera (módulo 3).</em></p>
  <p class="concepto"><strong>Nota de escala:</strong> la vista <em>Chile</em> es medición operativa propia — series que este Observatorio mantiene y actualiza cada mes con fuente primaria (Banco Central, CEPALSTAT). Las vistas <em>América Latina</em> y <em>Mundo</em> son referencia de literatura académica (Hickel et al.), no series propias con la misma cadencia de actualización: se amplían «de a poco», cuando los módulos 1-4 tengan su propia base país por país tan consistente como la de Chile.</p>
  <blockquote class="cita-boletin cita-marx">«Los proletarios no tienen patria.» <cite>(Marx y Engels, Manifiesto del Partido Comunista, cap. 2)</cite></blockquote>
  <div class="graf"><div class="magnitud-grid">
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("apropiacion_neta_valor"),1)} billones</span><span class="mag-que">apropiados netos por el Norte en un solo año (2015) = {fmt(h("trabajo_apropiado"))} millones de años-persona de trabajo sureño</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("drenaje_acumulado","1990-2015"))} billones</span><span class="mag-que">drenados en 1990-2015 (constantes 2010) ≈ un cuarto del PIB del Norte</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
    <div class="magnitud"><span class="mag-val">US$ {fmt(h("drenaje_acumulado","1960-2018"))} billones</span><span class="mag-que">drenados en 1960-2018 (constantes 2011); la intensidad se dispara en los 80-90</span><span class="mag-src">Hickel et al. 2021 (NPE)</span></div>
    <div class="magnitud"><span class="mag-val">{fmt(h("razon_perdidas_vs_ayuda"))}×</span><span class="mag-que">las pérdidas del Sur por intercambio desigual superan treinta veces toda la «ayuda» recibida en el período</span><span class="mag-src">Hickel et al. 2022 (GEC)</span></div>
  </div></div>
  <div class="botones-mapa" role="tablist" aria-label="Escala del mapa">
    <button class="activo" role="tab" aria-selected="true" data-vista="v-chile">Chile</button>
    <button role="tab" aria-selected="false" tabindex="-1" data-vista="v-al">América Latina</button>
    <button role="tab" aria-selected="false" tabindex="-1" data-vista="v-mundo">Mundo</button>
  </div>
  <p class="estado-mapa" id="estado-mapa">Vista Chile: vectores netos medidos por destino (BC 2024) — Europa, EE.UU., Canadá, Asia — más los intereses a la banca internacional; China como socio comercial, no como destino de la renta.</p>
  <div class="graf">{mapa_drenaje()}</div>
  <p class="leyenda-mapa"><span class="lg"><i class="sw sw-negro"></i>céntrico (FMI, proxy)</span><span class="lg"><i class="sw sw-rojo"></i>periférico</span><span class="lg"><i class="sw sw-flecha"></i>flujo medido (año declarado)</span><span class="lg"><i class="sw sw-punteada"></i>contexto / dirección de referencia</span></p>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> la teoría de la dependencia, ajustada a hoy y medida: el mercado de Chile es China, pero la renta va al Norte — Europa (neto US$ {fmt(V_EUR)} M), EE.UU. (US$ {fmt(V_USA)} M) y Canadá (US$ {fmt(V_CAN)} M) concentran la succión, y la minería pone el 43 % de ella. En magnitud: US$ {fmt(deb25)} M pagados por Chile en 2025; US$ {fmt(al_deb25)} M por América Latina; US$ {fmt(h("apropiacion_neta_valor"),1)} billones netos del Sur al Norte solo en 2015. El drenaje no es metáfora: tiene magnitud, dirección, historia y mapa.</p>
  {incomodo("China figura en la periferia (clasificación FMI) y a la vez —con la metodología de Hickel et al.— es de los mayores contribuyentes netos al drenaje: el mapa no autoriza a elegir bloque; ambos son capitalistas (regla de independencia comunista). Y con términos de intercambio favorables, la vía comercial del intercambio desigual se atenúa para Chile en el trimestre: la categoría no se condensa todos los meses — y declararlo es parte de la medición.")}
  {ficha(
    "Historia del drenaje (Hickel et al.): apropiación neta de trabajo, recursos y valor del Sur por el Norte. Mapa: clasificación dicotómica FMI (proxy) + flujos medidos — vectores Chile por destino: renta IED pagada (BC, principio direccional, 2024) neta donde el BC desagrega lo recibido; neto total: débito − crédito (CEPALSTAT 2025).",
    "<a href='https://doi.org/10.1080/13563467.2021.1899153'>Hickel, Sullivan y Zoomkawala (2021), <em>New Political Economy</em> 26(6)</a> · <a href='https://doi.org/10.1016/j.gloenvcha.2022.102467'>Hickel, Dorninger, Wieland y Suwandi (2022), <em>Global Environmental Change</em> 73</a> · <a href='https://si3.bcentral.cl/estadisticas/Principal1/excel/SE/BDP/Excel/Anual/IED_pais_sector_region.xlsx'>Banco Central, «IED por país, sector y región» (hoja Renta Direccional)</a> · <a href='https://api-cepalstat.cepal.org/cepalstat/api/v1/indicator/547/records?lang=es'>CEPALSTAT ind. 547</a> · <a href='https://www.imf.org/external/pubs/ft/weo/'>clasificación FMI</a> · datos: <a href='datos/observatorio/drenaje_mundial_hickel.csv'>hickel.csv</a> · <a href='datos/observatorio/renta_ied_chile_pais_2024.csv'>renta_ied_chile_pais_2024.csv</a>",
    "Hickel: series 1960-2018 y 1990-2015 (verificación 16-08-2026) · vectores: 2024 (último anual BC) · neto total: 2025",
    "P",
    "Cada cifra de Hickel con SU artículo (el «10,8» es del GEC 2022, no del NPE 2021). El grosor de las flechas sólidas es proporcional a la magnitud dentro de cada vista (1 px ≈ US$ 400 M en la vista Chile; no comparable entre vistas). Las punteadas no miden. La serie año a año del drenaje mundial vive en los anexos de los artículos.",
    "Canadá: recibido no desagregado por el BC (se reporta lo pagado) · utilidades reinvertidas por destino (el BC publica las distribuidas) · serie anual Hickel.")}
  <p class="fuente-obs">Fuentes: Hickel et al. (2021, 2022), con DOI en la ficha · Banco Central de Chile · CEPALSTAT · clasificación FMI · Elaboración propia. Ver también: Lenin, <em>El imperialismo, fase superior del capitalismo</em>; Dussel, <em>16 tesis de economía política</em>, Tesis 11 [11.4-11.5] (mecanismos de transferencia del plusvalor periferia-centro).</p>
</section>'''

# Lo neto: último año con las tres series (impuestos CEPALSTAT 821, gasto social 3127, rentas BC) y el PIB
NETO_ANIO = max(set(r["anio"] for r in tributos) & set(r["anio"] for r in gasto)
                & set(r["anio"] for r in rentas_cl) & set(r["anio"] for r in pib_min))
TR = next(r for r in tributos if r["anio"] == NETO_ANIO)
GN = next(r for r in gasto if r["anio"] == NETO_ANIO)
RN = next(r for r in rentas_cl if r["anio"] == NETO_ANIO)
PN = float(next(r for r in pib_min if r["anio"] == NETO_ANIO)["pib_usd_millones"])
N_TRIB, N_EMP, N_IVA = (float(TR[k]) for k in ("total_tributario", "corporaciones_y_empresas", "generales_bienes_y_servicios"))
N_GS, N_PROT = float(GN["gasto_social_total"]), float(GN["proteccion_social"])
N_SEV = sum(float(GN[k]) for k in ("salud", "educacion", "vivienda_y_servicios_comunitarios"))
N_DEB, N_NETO = float(RN["debito_total"]), -float(RN["balance_neto"])
N_DEB_PCT, N_NETO_PCT = N_DEB / PN * 100, N_NETO / PN * 100

sintesis = f'''<section class="modulo-obs sintesis-obs" id="sintesis">
  <h3>Síntesis de la coyuntura</h3>
  <p class="analisis"><strong>Interpretación política de la coyuntura:</strong> los cinco módulos son una sola secuencia leída en cinco escalas. En la semana obrera, la jornada legal baja a 42 h pero la carga global real sigue en {fmt(float(jornada["carga_global_real"]["valor"]))} h: lo que la ley concede, la reproducción privatizada y el traslado lo cobran por otro lado. Lo que ese trabajo produce circula por circuitos que lo capturan — el minero-rentístico ({fmt(MIN25,1)} % del PIB, con el cobre en máximos) y el de las pensiones (stock AFP ≈ {fmt(afp_pct)} % del PIB: el salario diferido convertido en capital ficticio) — y una fracción sale del país por la correa financiera: US$ {fmt(deb25)} M pagados en 2025, el {fmt(pib_pct25,1)} % del PIB, y en el primer semestre de {TRI_ANIO} un {fmt(var_deb)} % más que un año antes. La fracción que el Estado retiene para solventar salud, educación y vivienda va en sentido contrario: la megarreforma baja la tasa del 27 % al {fmt(tasa_final)} % hacia {anio_final}, el Presupuesto 2027 crece apenas {fmt(PRES27,1)} % y el ajuste suma US$ {fmt(AJ_TOTAL)} M, con PGU, gratuidad y bonos en revisión — sobre un gasto social que había llegado a {fmt(float(GSMAX["gasto_social_total"]),1)} % del PIB en {GSMAX["anio"]} y estaba en {fmt(float(GS1["gasto_social_total"]),1)} % en {GS1["anio"]}. Y lo que sale por la correa es la cuota nacional de un flujo mundial: US$ {fmt(h("apropiacion_neta_valor"),1)} billones netos del Sur al Norte solo en 2015.</p>
  <p class="analisis"><strong>Lo neto — qué retiene el Estado, qué reparte y qué se va ({NETO_ANIO}, último año con las tres series):</strong> el Gobierno Central recaudó en impuestos el {fmt(N_TRIB,1)} % del PIB. De eso, las empresas pagaron el {fmt(N_EMP,1)} % y el IVA y los demás impuestos generales al consumo —que paga cualquiera que compre pan— el {fmt(N_IVA,1)} %. Como gasto social repartió el {fmt(N_GS,1)} % del PIB, pero salud, educación y vivienda juntas fueron apenas el {fmt(N_SEV,1)} %; el resto ({fmt(N_PROT,1)} %) es protección social: pensiones y transferencias. Ese mismo año salieron del país, sobre todo como utilidades e intereses pagados al capital extranjero, US$ {fmt(N_DEB)} M: el {fmt(N_DEB_PCT,1)} % del PIB ({fmt(N_NETO_PCT,1)} % neto de lo que entró). <strong>Lo que salió por la correa superó todo lo que tributaron las empresas.</strong> Las tres series vienen de fuentes distintas sobre el mismo PIB: se comparan, no se suman como un balance contable.</p>
  <p class="analisis"><strong>El tablero mundial y el debate local:</strong> ese reparto se juega en un tablero que se mueve. Estados Unidos y China disputan la hegemonía, y Washington reordena sus fuerzas: presiona a sus propios aliados de la OTAN —en enero amenazó con aranceles a ocho países europeos por Groenlandia y los suspendió tras un «principio de acuerdo» con la alianza—, retira unos 5.000 efectivos de Alemania (confirmado por la OTAN en mayo) y anuncia repliegue en Medio Oriente, mientras su Estrategia de Seguridad Nacional declara el «corolario Trump» a la doctrina Monroe y concentra el esfuerzo en América Latina (ver <a href="america-latina.html">América Latina</a>). Chile está en la falla: China es el principal destino de sus exportaciones mineras, y en febrero Washington retiró la visa a tres funcionarios del gobierno saliente por el cable submarino Chile–China; en marzo Kast firmó con Estados Unidos un acuerdo de minerales críticos y en septiembre adhirió al «Escudo de las Américas». La arista europea pesa menos aquí y queda por documentar. <strong>Para el debate:</strong> ambos bloques son capitalistas; la pregunta no es a cuál alinearse, sino si la disputa entre ellos abre o cierra margen para retener lo que hoy se va por la correa — y quién decide qué se hace con eso.</p>
  <p class="analisis"><strong>Lectura:</strong> sale más y se retiene menos para solventar la vida. Ninguna de estas cifras decide por sí sola: lo que decide es la correlación de fuerzas — cuánto retiene cada cual, cuánto se devuelve y para quién. Estos datos terminan, en el mejor de los casos, en los <a href="puntos-reales.html">puntos reales</a>.</p>
  <p class="fuente-obs">Fuentes: CEPALSTAT, indicadores 821 (ingresos tributarios, Gobierno Central) y 3127 (gasto social, DIPRES), descarga 19-10-2026 · Banco Central de Chile vía CEPALSTAT (rentas primarias y PIB) · Elaboración propia. Prensa (borrador pendiente de revisión): <a href="https://www.meganoticias.cl/mundo/512456-trump-amenaza-nuevos-aranceles-europa-hasta-que-eeuu-adquiera-groenlandia-17-01-2026.html">Meganoticias, 17-01-2026</a> y <a href="https://www.elimparcial.com/mundo/2026/01/21/trump-anuncia-acuerdo-con-la-otan-sobre-groenlandia-y-suspende-aranceles-a-europa-tras-reunion-en-davos/">El Imparcial, 21-01-2026</a> (Groenlandia) · <a href="https://www.metro.pr/noticias/2026/05/19/otan-confirma-retirada-de-5000-militares-de-estados-unidos-de-europa/">Metro, 19-05-2026</a> y <a href="https://es.euronews.com/2026/05/06/puede-la-ley-estadounidense-impedir-que-trump-retire-las-tropas-de-europa">Euronews, 06-05-2026</a> (tropas en Europa) · <a href="https://www.tvazteca.com/aztecanoticias/estados-unidos-avanza-en-retiro-militar-total-en-siria-10-anos-operacion-isis/">TV Azteca, sobre WSJ</a> (Siria; plazos y cifras por confirmar) · <a href="https://forbes.cl/actualidad/2026-02-20/estados-unidos-revoca-visado-a-tres-funcionarios-del-gobierno-chileno">Forbes Chile, 20-02-2026</a> y <a href="https://expansion.mx/mundo/2026/02/25/un-cable-submarino-que-conecta-con-china-esta-en-el-centro-de-la-disputa-entre-chile-y-eu">Expansión, 25-02-2026</a> (cable) · <a href="https://eldesconcierto.cl/2026/03/12/cancilleria-anuncia-acuerdo-con-eeuu-para-reforzar-suministro-de-minerales-criticos-y-tierras-raras">El Desconcierto, 12-03-2026</a> (minerales críticos) y <a href="https://www.elperuano.pe/noticia/291126-pacto-para-buscar-minerales-criticos">El Peruano</a> (China, destino de la minería chilena) · Escudo de las Américas y «corolario Trump»: fuentes en <a href="america-latina.html">América Latina</a>.</p>
</section>'''

cierre = f'''<section class="modulo-obs cierre-obs">
  <h3>Qué no muestra esta página — y cómo se construyó</h3>
  <p><strong>Lo que no muestra:</strong> los flujos entre países del Sur (la dependencia no es solo Sur→Norte); los paraísos fiscales como nodos de la correa financiera (Bermuda e Islas Vírgenes aparecen en la balanza del BC como «otros y no asignados»); las utilidades reinvertidas por destino; y el registro propio de los puntos reales (ollas, comités, asambleas), que es tarea de la organización, no de las estadísticas oficiales.</p>
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
    <p class="principio-sec">Los datos del análisis, públicos para las luchas: tendencias, brechas y el drenaje del plusvalor. Corte de datos: 11 de octubre de 2026.</p>
  </div>
  <nav class="indice-sub"><a href="index.html">Portada</a><a href="secciones/los-medios-comunes.html">I · Medios comunes</a><a href="secciones/trabajo-polimorfo.html">II · Trabajo polimorfo</a><a href="secciones/proletariado.html">III · Proletariado</a><a href="secciones/marchitamiento-del-estado.html">IV · Marchitamiento del Estado</a><a href="especial-18-de-octubre.html">Especial 18-O</a><a href="puntos-reales.html">Puntos reales</a><a class="actual" href="observatorio.html">Observatorio</a></nav>
</header>
<nav class="nav-obs" aria-label="Módulos del Observatorio">
  <a href="#termometro">Termómetro</a><a href="#m1">1 · Jornada</a><a href="#m2">2 · Circuitos</a><a href="#m3">3 · Correa financiera</a><a href="#m4">4 · Retención estatal</a><a href="#m5">5 · Mapa del drenaje</a><a href="#sintesis">Síntesis</a>
</nav>
<main class="contenido-sec">
  <p class="ayuda-graf">Los gráficos responden: pasa el cursor, toca o recorre con las flechas del teclado para leer cada dato; «Ver los datos de este gráfico» abre la tabla completa.</p>
  {term}
  <section class="bloque pregunta">
    <h3>¿Cómo analizamos la coyuntura?</h3>
    <p>Con la matriz del Reporte de Análisis de Coyuntura: <strong>principio → atado (qué medir) → circuitos (dónde se juega) → punto real (desde dónde se apuesta)</strong>. Los módulos de abajo son esa matriz hecha visible, en un solo relato: de la semana obrera a los circuitos que capturan su producto y su peso, de la correa financiera que mide cuánto plusvalor sale del país a la fracción que el Estado retiene y lo que solventa con ella, y al final la transferencia entre países — con historia y con mapa. Cada figura declara su fuente, su fecha de corte y su estatus de medición en su <em>ficha del dato</em>; cada módulo registra su <em>dato incómodo</em>: el que más tensiona la hipótesis. Una hipótesis que no puede perder no es análisis: es tautología.</p>
  </section>
  {m1}
  {transicion("Lo que se produce en la semana no se queda en la fábrica ni en la casa: sigue el circuito del capital. ¿Por dónde fluye, quién lo captura y con qué peso?")}
  {m2}
  {transicion("Una parte creciente de ese excedente ni siquiera se queda en el país: sale por la balanza de pagos, sin cruzar aduana. Esa es la correa financiera — la medición directa de cuánto plusvalor sale.")}
  {m3}
  {transicion("Otra fracción la retiene el Estado — y la correlación de fuerzas decide cuánto y para quién. Con ella se solventan, o no, las condiciones fundamentales.")}
  {m4}
  {transicion("Lo que Chile paga es la cuota nacional de un flujo mundial medido con precisión. La transferencia tiene historia — y también geografía: el mapa del drenaje.")}
  {m5}
  {sintesis}
  {cierre}
</main>
<footer>
  <p><strong>EL CORREO COMUNISTA</strong> · ¡Centralización de la discusión! · Ediciones ¡Que Acontezca!</p>
  <p>Reproducción libre, total o parcial, citando la fuente · <a href="https://creativecommons.org/licenses/by/4.0/deed.es">CC BY 4.0</a></p>
</footer>
<script>
document.querySelectorAll('.botones-mapa button').forEach(function(b){{
  b.addEventListener('click',function(){{
    document.querySelectorAll('.botones-mapa button').forEach(x=>{{x.classList.remove('activo'); x.setAttribute('aria-selected','false'); x.setAttribute('tabindex','-1');}});
    b.classList.add('activo');
    b.setAttribute('aria-selected','true');
    b.setAttribute('tabindex','0');
    document.querySelectorAll('.vista-mapa').forEach(v=>v.style.display='none');
    document.getElementById(b.dataset.vista).style.display='block';
    const estados={{
      'v-chile':'Vista Chile: vectores netos medidos por destino (BC 2024) — Europa, EE.UU., Canadá, Asia — más los intereses a la banca internacional; China como socio comercial, no como destino de la renta.',
      'v-al':'Vista América Latina (referencia de literatura, no serie propia): lo que la región pagó en rentas primarias (2025) contra lo que entró por IED (2024) — utilidades de Perú subestimadas (declarado).',
      'v-mundo':'Vista Mundo (referencia de literatura, no serie propia): direcciones de referencia del drenaje y la magnitud neta Sur→Norte de la literatura (Hickel et al. 2022); China como contribuyente neto: ambos bloques son capitalistas.'
    }};
    document.getElementById('estado-mapa').textContent = estados[b.dataset.vista];
  }});
}});
</script>
<script src="interactivo.js" defer></script>
</body>
</html>
'''

# ───────────────────────── portada: franja «cifras del corte» ─────────────────────────
def franja_portada():
    """Franja de portada generada desde los mismos CSV (se inserta entre los marcadores de index.html)."""
    # ── (iv) extracción: columnas por año y por destino ──
    campo_bal = "balance" if "balance" in rentas_cl[0] else "balance_neto"
    def serie_anual(campo, signo=1):
        filas, prev = [], None
        campo_tri = "balance_neto" if campo == campo_bal else campo
        for r in rentas_cl:
            v = signo * float(r[campo]); parcial = r["nota"].startswith("parcial")
            if parcial:
                base = sum(signo * tri(TRI_ANIO - 1, q, campo_tri) for q in range(1, TRI_Q + 1))
                cmp_ = f'{TRI_Q} trimestres · {"+" if v >= base else "−"}{fmt(abs(v / base - 1) * 100)} % sobre los mismos de {TRI_ANIO - 1}'
            elif prev:
                cmp_ = f'{"+" if v >= prev else "−"}{fmt(abs(v / prev - 1) * 100, 1)} % sobre {int(r["anio"]) - 1}'
            else:
                cmp_ = "inicio de la serie"
            filas.append({"e": r["anio"] + (" (parcial)" if parcial else ""), "eje": r["anio"][2:], "v": v, "cmp": cmp_, "par": parcial})
            if not parcial: prev = v
        return filas
    tot_ied = float(ip("TOTAL IED")["pagado"])
    CORTO = {"Europa": "Europa", "Estados Unidos": "EE.UU.", "Canadá": "Canadá", "Asia (Japón)": "Asia", "Oceanía": "Oceanía", "Otros y no asignados": "Otros"}
    destinos = [{"e": r["destino"], "eje": CORTO.get(r["destino"], r["destino"]), "v": float(r["pagado"]),
                 "cmp": f'{fmt(float(r["pagado"]) / tot_ied * 100)} % de la renta de la inversión extranjera pagada en 2024'}
                for r in ied_pais if r["destino"] != "TOTAL IED"]
    fte = "CEPALSTAT, ind. 547 (compila Banco Central)"
    i_max = max(range(len(rentas_cl)), key=lambda i: float(rentas_cl[i]["debito_total"]))
    datos = {"prefijo": "US$ ", "sufijo": " M", "fuente": fte, "series": [
        {"clave": "deb", "corto": "Total por año", "nombre": "Rentas primarias pagadas al exterior, por año", "nota": "En rojo, el año más alto; 2026 va incompleto.", "inicio": i_max, "filas": serie_anual("debito_total")},
        {"clave": "uti", "corto": "Utilidades IED", "nombre": "Utilidades y dividendos de la inversión extranjera, por año", "nota": "2026 va incompleto.", "inicio": i_max, "filas": serie_anual("ied_utilidades_dividendos")},
        {"clave": "neto", "corto": "Saldo neto", "nombre": "Saldo neto: lo que sale menos lo que entra, por año", "nota": "2026 va incompleto.", "inicio": i_max, "filas": serie_anual(campo_bal, -1)},
        {"clave": "dest", "corto": "Por destino", "nombre": "Renta de la inversión extranjera pagada en 2024, por destino", "nota": "Utilidades distribuidas.", "fuente": "Banco Central, IED por país (renta direccional), 2024", "inicio": 0, "filas": destinos}]}
    W, H = 420, 170; fa = datos["series"][0]["filas"]; n = len(fa); gap = 5; bw = (W - gap * (n - 1)) / n; mx = max(x["v"] for x in fa)
    est = f'<line class="b-base" x1="0" y1="{H-22}" x2="{W}" y2="{H-22}"/>'
    for i, x in enumerate(fa):
        hh = x["v"] / mx * (H - 36); xx = i * (bw + gap)
        est += (f'<rect class="b{" b-ult" if x["v"] == mx else ""}{" b-par" if x["par"] else ""}" x="{xx:.1f}" y="{H-22-hh:.1f}" width="{bw:.1f}" height="{hh:.1f}"/>'
                f'<text class="b-eje" x="{xx+bw/2:.1f}" y="{H-7}" text-anchor="middle">{x["eje"]}</text>')

    # ── (iii) retención: una columna por año, con línea segmentada en cada cambio legal ──
    RW, RH, RB = 420, 170, 148
    n_t = len(TASAS); rbw = RW / n_t
    def ry(v): return RB - (RB - 40) * v / 30
    ret = f'<line class="eje-l" x1="0" y1="{RB}" x2="{RW}" y2="{RB}"/>'
    for i, r in enumerate(TASAS):
        ret += (f'<rect class="{"col-proy" if r["proy"] else "col"}" x="{i*rbw+0.8:.1f}" y="{ry(r["tasa"]):.1f}" width="{rbw-1.6:.1f}" height="{RB-ry(r["tasa"]):.1f}"><title>{titulo_tasa(r)}</title></rect>')
        if r["anio"] % 10 == 0: ret += f'<text class="eje-t" x="{i*rbw+rbw/2:.1f}" y="{RH-7}" text-anchor="middle">{r["anio"]}</text>'
    for anio, rot in LEYES:
        xl = (anio - TASAS[0]["anio"]) * rbw; fin = anio > ANIO_HOY
        cls = " ley-proy" if fin else ""
        ytx = 10 if fin else 26
        ret += (f'<line class="ley-l{cls}" x1="{xl:.1f}" y1="{ytx - 8}" x2="{xl:.1f}" y2="{RB}"/>'
                f'<text class="ley-t{cls}" x="{xl + (4 if anio == 2015 else -4):.1f}" y="{ytx}" text-anchor="{"start" if anio == 2015 else "end"}">{rot}</text>')
    tasa_max = max(r["tasa"] for r in TASAS); tasa_ini = TASAS[0]["tasa"]

    # ── (ii) explotación: la semana obrera y sus dos tasas ──
    segs = [("trabajo_necesario", "Necesario", "seg-a"), ("plustrabajo", "Plustrabajo", "seg-b"),
            ("traslado_no_remunerado", "Traslado", "seg-c"), ("reproductivo_no_remunerado", "Hogar y cuidados", "seg-d")]
    tot = sum(float(jornada[k]["valor"]) for k, _, _ in segs); x = 0; sem = ""
    for k, nom, cls in segs:
        v = float(jornada[k]["valor"]); w = 420 * v / tot; h_txt = fmt(v, 2).rstrip("0").rstrip(",")
        sem += (f'<rect class="{cls}" x="{x:.1f}" y="6" width="{w:.1f}" height="40"><title>{nom}: {h_txt} horas a la semana — {jornada[k]["nota"]}</title></rect>'
                f'<text class="seg-n" x="{x + w/2:.1f}" y="31" text-anchor="middle">{h_txt} h</text>'
                f'<text class="seg-r" x="{x + w/2:.1f}" y="62" text-anchor="middle">{nom}</text>')
        x += w
    sv = float(jornada["tasa_explotacion_sv"]["valor"]); tetv = float(jornada["TETV"]["valor"])

    # ── (i) desempleo: oficial e integral, mismo trimestre ──
    s = sol_des[-1]; td = float(s["tasa_desempleo"]); tdi = float(s["tasa_desempleo_integral"])
    des = kpi("Desempleo / informalidad")
    TRIM = {"DEF": "diciembre-febrero", "EFM": "enero-marzo", "FMA": "febrero-abril", "MAM": "marzo-mayo", "AMJ": "abril-junio", "MJJ": "mayo-julio",
            "JJA": "junio-agosto", "JAS": "julio-septiembre", "ASO": "agosto-octubre", "SON": "septiembre-noviembre", "OND": "octubre-diciembre", "NDE": "noviembre-enero"}
    periodo_ine = TRIM.get(des["fecha_corte"].split("-")[0], des["fecha_corte"])
    def dh(v): return 120 * v / 16.0
    dcol = (f'<line class="eje-l" x1="0" y1="140" x2="240" y2="140"/>'
            f'<rect class="col" x="22" y="{140-dh(td):.1f}" width="84" height="{dh(td):.1f}"><title>Tasa de desempleo, {s["trimestre_movil"]}: {fmt(td,1)} % (Fundación SOL sobre la ENE del INE)</title></rect>'
            f'<rect class="col-proy" x="134" y="{140-dh(tdi):.1f}" width="84" height="{dh(tdi):.1f}"><title>Tasa de Desempleo Integral, {s["trimestre_movil"]}: {fmt(tdi,1)} % — suma subempleo y desaliento (hombres {fmt(float(s["tdi_hombres"]),1)} %, mujeres {fmt(float(s["tdi_mujeres"]),1)} %)</title></rect>'
            f'<text class="col-n" x="64" y="{140-dh(td)-7:.1f}" text-anchor="middle">{fmt(td,1)} %</text>'
            f'<text class="col-n" x="176" y="{140-dh(tdi)-7:.1f}" text-anchor="middle">{fmt(tdi,1)} %</text>'
            f'<text class="eje-t" x="64" y="156" text-anchor="middle">oficial</text><text class="eje-t" x="176" y="156" text-anchor="middle">integral</text>')

    return f"""<section class="cifras-corte" aria-label="Cifras del Observatorio">
    <div class="cifra cifra-exp">
      <p class="cifra-rot">Explotación · la semana obrera</p>
      <div class="cifra-par"><p><strong class="cifra-num">{fmt(sv,1)} %</strong><span>tasa de explotación: plustrabajo sobre trabajo necesario</span></p><p><strong class="cifra-num">{fmt(tetv,1)} %</strong><span>si se suma el traslado no pagado: tiempo vital expropiado</span></p></div>
      <div class="graf-est"><svg class="est-graf" viewBox="0 0 420 70" role="img" aria-label="Composición de la semana obrera en horas">{sem}</svg></div>
      <p class="cifra-nota">{fmt(float(jornada["carga_global_real"]["valor"]))} horas de carga real a la semana. Nivel de referencia, no dato del mes. <span>Reporte N°1 sobre Fundación SOL (2022)</span></p>
      <a class="cifra-ir" href="observatorio.html#m1">Ver el módulo 1 →</a>
    </div>
    <div class="cifra cifra-des">
      <p class="cifra-rot">Desempleo · oficial e integral</p>
      <div class="cifra-lado">
        <div class="graf-est"><svg class="est-graf" viewBox="0 0 240 162" role="img" aria-label="Desempleo oficial e integral, {s["trimestre_movil"]}">{dcol}</svg></div>
        <p class="cifra-nota"><strong>{fmt(tdi - td,1)} puntos</strong> separan la cifra oficial de la que suma el subempleo y el desaliento, en {s["trimestre_movil"]}.<br>Último dato oficial: {fmt(float(des["valor_numerico"]),1)} % en {periodo_ine}. <span>Fundación SOL, IMCE (28-08-2026) · {des["fuente"]}</span></p>
      </div>
      <a class="cifra-ir" href="observatorio.html#m2">Ver el módulo 2 →</a>
    </div>
    <div class="cifra cifra-ret">
      <p class="cifra-rot">Retención del Estado · impuesto a las empresas</p>
      <div class="graf-est"><svg class="est-graf" viewBox="0 0 {RW} {RH}" role="img" aria-label="Tasa legal del impuesto a las empresas por año, de {TASAS[0]["anio"]} a {ANIO_FIN_TASA}">{ret}</svg></div>
      <p class="cifra-nota"><strong>{fmt(tasa_ini)} % → {fmt(tasa_max)} % → {fmt(tasa_final)} %.</strong> Tasa legal por año; las líneas marcan cada cambio de ley y, en rojo, la rebaja ya promulgada hacia {ANIO_FIN_TASA}. <span>leyes citadas en el Observatorio · prensa, 09-10-2026</span></p>
      <a class="cifra-ir" href="observatorio.html#m4">Ver el módulo 4 →</a>
    </div>
    <div class="cifra cifra-graf">
      <p class="cifra-rot">Extracción · rentas que salen de Chile</p>
      <div class="graf-serie" data-datos="datos-extraccion">
        <svg class="mini-graf" viewBox="0 0 {W} {H}" role="img" aria-label="Rentas primarias pagadas por Chile, por año">{est}</svg>
        <p class="cifra-nota"><strong>US$ {fmt(deb25)} M</strong> en 2025, el año más alto de la serie; US$ {fmt(deb_parcial)} M en los primeros {TRI_Q} trimestres de {TRI_ANIO}. <span>{fte}</span></p>
      </div>
      <script type="application/json" id="datos-extraccion">{json.dumps(datos, ensure_ascii=False, separators=(",", ":"))}</script>
      <a class="cifra-ir" href="observatorio.html#m3">Ver el módulo 3 →</a>
    </div>
  </section>"""

INI, FIN = "<!-- CIFRAS:INICIO (generado por scripts/build_observatorio.py; no editar a mano) -->", "<!-- CIFRAS:FIN -->"
portada = PORTADA.read_text(encoding="utf-8")
if INI in portada and FIN in portada:
    a, b = portada.index(INI) + len(INI), portada.index(FIN)
    PORTADA.write_text(portada[:a] + "\n  " + franja_portada() + "\n  " + portada[b:], encoding="utf-8")
    print("index.html: franja «cifras del corte» regenerada")
else:
    print("AVISO: index.html no tiene los marcadores CIFRAS; la franja de portada no se actualizó")


# ───────────────────────── gráfica por sección (portada y páginas de sección) ─────────────────────────
# Cada principio lleva una banda con un gráfico chico y dos cifras, tomadas de los mismos CSV.
# Cada página de sección lleva además «la sección en cifras»: despachos, fuentes y despachos por mes,
# contados sobre el propio HTML de la página.
def svg_semana():
    segs = [("trabajo_necesario", "Necesario", "seg-a"), ("plustrabajo", "Plustrabajo", "seg-b"),
            ("traslado_no_remunerado", "Traslado", "seg-c"), ("reproductivo_no_remunerado", "Hogar y cuidados", "seg-d")]
    tot = sum(float(jornada[k]["valor"]) for k, _, _ in segs); x = 0; g = ""
    for k, nom, cls in segs:
        v = float(jornada[k]["valor"]); w = 420 * v / tot; h_txt = fmt(v, 2).rstrip("0").rstrip(",")
        g += (f'<rect class="{cls}" x="{x:.1f}" y="6" width="{w:.1f}" height="40"><title>{nom}: {h_txt} horas a la semana — {jornada[k]["nota"]}</title></rect>'
              f'<text class="seg-n" x="{x + w/2:.1f}" y="31" text-anchor="middle">{h_txt} h</text>'
              f'<text class="seg-r" x="{x + w/2:.1f}" y="62" text-anchor="middle">{nom}</text>')
        x += w
    return f'<svg class="est-graf" viewBox="0 0 420 70" role="img" aria-label="Composición de la semana obrera en horas">{g}</svg>'

def svg_tasa():
    RW, RH, RB = 420, 150, 128
    rbw = RW / len(TASAS)
    def ry(v): return RB - (RB - 36) * v / 30
    g = f'<line class="eje-l" x1="0" y1="{RB}" x2="{RW}" y2="{RB}"/>'
    for i, r in enumerate(TASAS):
        g += f'<rect class="{"col-proy" if r["proy"] else "col"}" x="{i*rbw+0.8:.1f}" y="{ry(r["tasa"]):.1f}" width="{rbw-1.6:.1f}" height="{RB-ry(r["tasa"]):.1f}"><title>{titulo_tasa(r)}</title></rect>'
        if r["anio"] % 10 == 0: g += f'<text class="eje-t" x="{i*rbw+rbw/2:.1f}" y="{RH-7}" text-anchor="middle">{r["anio"]}</text>'
    for anio, rot in LEYES:
        if anio <= ANIO_HOY: continue
        xl = (anio - TASAS[0]["anio"]) * rbw
        g += (f'<line class="ley-l ley-proy" x1="{xl:.1f}" y1="6" x2="{xl:.1f}" y2="{RB}"/>'
              f'<text class="ley-t ley-proy" x="{xl - 4:.1f}" y="14" text-anchor="end">{rot}</text>')
    return f'<svg class="est-graf" viewBox="0 0 {RW} {RH}" role="img" aria-label="Tasa legal del impuesto a las empresas por año">{g}</svg>'

def svg_barras_h(items, unidad):
    """items: [(rótulo, valor, clase)] → barras horizontales con el valor al final."""
    mx = max(v for _, v, _ in items); g = ""
    for i, (nom, v, cls) in enumerate(items):
        y = 4 + i * 40; w = 300 * v / mx
        g += (f'<text class="seg-r" x="0" y="{y + 9}">{nom}</text>'
              f'<rect class="{cls}" x="0" y="{y + 14}" width="{w:.1f}" height="16"><title>{nom}: {fmt(v, 1)} {unidad}</title></rect>'
              f'<text class="col-n col-n-ch" x="{w + 8:.1f}" y="{y + 28}">{fmt(v, 1)} %</text>')
    return f'<svg class="est-graf" viewBox="0 0 420 {8 + 40 * len(items)}" role="img" aria-label="Peso de cada circuito, en porcentaje del PIB">{g}</svg>'

def svg_destinos():
    CORTO = {"Europa": "Europa", "Estados Unidos": "EE.UU.", "Canadá": "Canadá", "Asia (Japón)": "Asia", "Oceanía": "Oceanía", "Otros y no asignados": "Otros"}
    filas = [r for r in ied_pais if r["destino"] != "TOTAL IED"]
    mx = max(float(r["pagado"]) for r in filas); n = len(filas); gap = 10; bw = (420 - gap * (n - 1)) / n; g = '<line class="eje-l" x1="0" y1="118" x2="420" y2="118"/>'
    for i, r in enumerate(filas):
        v = float(r["pagado"]); hh = 96 * v / mx; x = i * (bw + gap)
        g += (f'<rect class="{"col-proy" if v == mx else "col"}" x="{x:.1f}" y="{118 - hh:.1f}" width="{bw:.1f}" height="{hh:.1f}"><title>{r["destino"]}: US$ {fmt(v)} M de renta de la inversión extranjera pagada en 2024</title></rect>'
              f'<text class="eje-t" x="{x + bw/2:.1f}" y="134" text-anchor="middle">{CORTO.get(r["destino"], r["destino"])}</text>')
    return f'<svg class="est-graf" viewBox="0 0 420 140" role="img" aria-label="Renta de la inversión extranjera pagada en 2024, por destino">{g}</svg>'


# ── IV · acciones de protesta por año y tema (COES, solo totales) ──
prot = lee_csv("acciones_de_protesta_coes.csv")
P_ANIOS = sorted({int(r["anio"]) for r in prot})
P_VAL = {(int(r["anio"]), r["tema"]): int(r["acciones"]) for r in prot}
P_NOMBRE = {"educacion": "Educación", "laboral": "Trabajo", "pensiones": "Pensiones", "salud": "Salud", "vivienda": "Vivienda",
            "pueblos_originarios": "Pueblos originarios", "ambiental_y_territorial": "Ambiente y territorio",
            "feminista_y_diversidad": "Feminismo y diversidad", "ddhh_y_memoria": "Derechos humanos y memoria",
            "sistema_politico": "Sistema político", "otras": "Otras demandas", "sin_demanda_registrada": "Sin demanda registrada"}
# en el gráfico resumen se apilan cinco temas con nombre y dos grupos de resto
P_PILA = [("educacion", ["educacion"]), ("laboral", ["laboral"]), ("pensiones", ["pensiones"]), ("salud", ["salud"]), ("vivienda", ["vivienda"]),
          ("otras", ["pueblos_originarios", "ambiental_y_territorial", "feminista_y_diversidad", "ddhh_y_memoria", "sistema_politico", "otras"]),
          ("sin", ["sin_demanda_registrada"])]
P_ROTULO = {"educacion": "Educación", "laboral": "Trabajo", "pensiones": "Pensiones", "salud": "Salud", "vivienda": "Vivienda", "otras": "Otras demandas", "sin": "Sin demanda registrada"}
def p_total(a): return sum(v for (y, _), v in P_VAL.items() if y == a)
P_MAX_ANIO = max(P_ANIOS, key=p_total)

def svg_protestas(alto=150):
    W = 420; n = len(P_ANIOS); gap = 3; bw = (W - gap * (n - 1)) / n; base = alto - 20; mx = p_total(P_MAX_ANIO)
    g = f'<line class="eje-l" x1="0" y1="{base}" x2="{W}" y2="{base}"/>'
    for i, a in enumerate(P_ANIOS):
        x = i * (bw + gap); y = base
        for clave, temas in P_PILA:
            v = sum(P_VAL[(a, t)] for t in temas)
            if not v: continue
            hh = (base - 8) * v / mx; y -= hh
            g += f'<rect class="tm-{clave}" x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{hh:.1f}"><title>{a} · {P_ROTULO[clave]}: {fmt(v)} acciones</title></rect>'
        if a % 5 == 0 or a == P_ANIOS[-1]: g += f'<text class="eje-t" x="{x + bw/2:.1f}" y="{alto - 5}" text-anchor="middle">{a}</text>'
    return f'<svg class="est-graf" viewBox="0 0 {W} {alto}" role="img" aria-label="Acciones de protesta en Chile por año, de {P_ANIOS[0]} a {P_ANIOS[-1]}, según el tema de la demanda">{g}</svg>'

def leyenda_protestas():
    return '<p class="tm-leyenda">' + "".join(f'<span><i class="tm-{c}"></i>{P_ROTULO[c]}</span>' for c, _ in P_PILA) + '</p>'

def svg_tema(tema):
    """Columnas chicas de un solo tema, 2005-2024, con el año más alto destacado."""
    vals = [P_VAL[(a, tema)] for a in P_ANIOS]; mx = max(vals) or 1; n = len(vals); gap = 2; bw = (200 - gap * (n - 1)) / n
    g = '<line class="eje-l" x1="0" y1="56" x2="200" y2="56"/>'
    for i, (a, v) in enumerate(zip(P_ANIOS, vals)):
        hh = 50 * v / mx
        g += f'<rect class="{"col-proy" if v == mx else "col"}" x="{i*(bw+gap):.1f}" y="{56 - hh:.1f}" width="{bw:.1f}" height="{max(hh, 0.5):.1f}"><title>{P_NOMBRE[tema]} {a}: {fmt(v)} acciones</title></rect>'
    g += f'<text class="eje-t" x="0" y="68">{P_ANIOS[0]}</text><text class="eje-t" x="200" y="68" text-anchor="end">{P_ANIOS[-1]}</text>'
    return f'<svg class="est-graf" viewBox="0 0 200 72" role="img" aria-label="{P_NOMBRE[tema]}: acciones de protesta por año">{g}</svg>', P_ANIOS[vals.index(mx)], mx, sum(vals)

def protestas_pagina():
    """Desarrollo para la página de la sección IV."""
    tot = sum(P_VAL.values()); sin19 = P_VAL[(2019, "sin_demanda_registrada")]
    fichas = ""
    for t in [k for k in P_NOMBRE if k != "sin_demanda_registrada"]:
        svg, a_max, v_max, suma = svg_tema(t)
        fichas += f'<div class="tm-ficha graf-est"><p class="cifra-rot">{P_NOMBRE[t]}</p>{svg}<p class="tm-nota"><strong>{fmt(suma)}</strong> acciones · máximo en {a_max} ({fmt(v_max)})</p></div>'
    registro = sorted(lee_csv("movilizaciones_registro.csv"), key=lambda r: r["fecha"])
    TEMA_R = {"educacion": "Educación", "vivienda": "Vivienda", "trabajo": "Trabajo", "salud": "Salud", "pensiones": "Pensiones", "internacionalismo": "Internacionalismo", "antimilitarismo": "Contra el rearme"}
    MES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]
    filas_reg = "".join(
        f'<tr><td>{int(r["fecha"][8:])} {MES[int(r["fecha"][5:7]) - 1]}</td><td>{r["pais"]}<span>{r["lugar"]}</span></td><td>{TEMA_R.get(r["tema"], r["tema"])}</td>'
        f'<td>{r["descripcion"]}<span>{r["convocante"]}{" · convocada, sin confirmar su realización" if r["estado"] == "convocada" else ""}</span></td>'
        f'<td><a href="{r["fuente_url"]}" target="_blank" rel="noopener">{r["fuente"]}</a>{"<span>fuente sin abrir</span>" if r["verificacion"].startswith("solo") else ""}</td></tr>' for r in registro)
    por_tema = {}
    for r in registro: por_tema[TEMA_R.get(r["tema"], r["tema"])] = por_tema.get(TEMA_R.get(r["tema"], r["tema"]), 0) + 1
    resumen_reg = " · ".join(f"{k} {v}" for k, v in sorted(por_tema.items(), key=lambda kv: -kv[1]))
    en_chile = sum(1 for r in registro if r["pais"] == "Chile")
    return f'''<section class="dato-seccion ds-papel protestas">
  <div class="ds-graf graf-est"><p class="cifra-rot">Lo que se levanta por fuera del Estado · acciones de protesta por año y tema, {P_ANIOS[0]}-{P_ANIOS[-1]}</p>{svg_protestas(190)}{leyenda_protestas()}</div>
  <div class="ds-cifras"><p><strong class="cifra-num">{fmt(tot)}</strong><span>acciones de protesta registradas en veinte años</span></p><p><strong class="cifra-num">{fmt(p_total(P_MAX_ANIO))}</strong><span>en {P_MAX_ANIO}, el año más alto: {fmt(sin19)} de ellas sin una demanda registrada</span></p></div>
  <div class="tm-rejilla">{fichas}</div>
  <p class="ds-nota"><strong>Cómo leerlo:</strong> cada acción es un hecho de protesta recogido por los diarios y radios que el Observatorio codifica; el número depende de qué medios se cubren cada año, así que sirve para ver ciclos y temas, no para comparar al detalle un año con otro. El tema es el de la primera demanda registrada; la agrupación por temas es nuestra. En {P_MAX_ANIO} la mitad de las acciones no tiene demanda registrada, y la fuente no explica por qué. Contar protestas no es medir poder popular: es el dato más cercano que existe. Lo que falta —qué organización dejó cada una— es el registro propio que este Correo empieza a llevar ({len(registro)} movilizaciones anotadas a la fecha).</p>
  <div class="reg-propio">
    <p class="cifra-rot">Registro propio · {ANIO_HOY}, desde agosto · {len(registro)} movilizaciones, {en_chile} en Chile</p>
    <p class="tm-nota">{resumen_reg}. La base de COES llega a {P_ANIOS[-1]}: entre ambas queda sin cubrir {P_ANIOS[-1] + 1}. Este registro es un borrador hecho con las noticias reunidas para esta edición; no es exhaustivo ni comparable con la serie de arriba.</p>
    <table class="reg-tabla"><thead><tr><th>Fecha</th><th>Lugar</th><th>Tema</th><th>Qué</th><th>Fuente</th></tr></thead><tbody>{filas_reg}</tbody></table>
  </div>
  <p class="ds-pie">Fuente: Reproducible Research, Centre for Social Conflict and Cohesion Studies COES, «Observatory of Conflicts - Cumulative Dataset», Harvard Dataverse, <a href="https://doi.org/10.7910/DVN/GKQXBR">doi:10.7910/DVN/GKQXBR</a> · solo totales; elaboración propia</p>
</section>'''

def svg_cols(filas, aria, alto=118):
    """filas: [(rótulo del eje o "", valor, título, destacar)] → columnas verticales con el valor del extremo destacado."""
    mx = max(v for _, v, _, _ in filas); n = len(filas); gap = 6; bw = (420 - gap * (n - 1)) / n
    g = f'<line class="eje-l" x1="0" y1="{alto}" x2="420" y2="{alto}"/>'
    for i, (eje, v, tit, dest) in enumerate(filas):
        hh = (alto - 22) * v / mx; x = i * (bw + gap)
        g += f'<rect class="{"col-proy" if dest else "col"}" x="{x:.1f}" y="{alto - hh:.1f}" width="{bw:.1f}" height="{hh:.1f}"><title>{tit}</title></rect>'
        if eje: g += f'<text class="eje-t" x="{x + bw/2:.1f}" y="{alto + 16}" text-anchor="middle">{eje}</text>'
    return f'<svg class="est-graf" viewBox="0 0 420 {alto + 22}" role="img" aria-label="{aria}">{g}</svg>'

def svg_paises():
    """Lo que pagó en rentas primarias cada país de la región en 2024 (los seis mayores)."""
    filas = sorted(pais24, key=lambda r: -float(r["debito_total_2024"]))[:6]
    mx = float(filas[0]["debito_total_2024"]); g = ""
    for i, r in enumerate(filas):
        v = float(r["debito_total_2024"]); y = 2 + i * 22; w = 250 * v / mx
        g += (f'<text class="seg-r" x="62" y="{y + 12}" text-anchor="end">{r["pais"]}</text>'
              f'<rect class="{"col-proy" if r["pais"] == "Chile" else "col"}" x="70" y="{y}" width="{w:.1f}" height="16"><title>{r["pais"]}: US$ {fmt(v)} M pagados al exterior en rentas primarias (2024)</title></rect>'
              f'<text class="seg-r" x="{76 + w:.1f}" y="{y + 12}">US$ {fmt(v)} M</text>')
    return f'<svg class="est-graf" viewBox="0 0 420 {6 + 22 * len(filas)}" role="img" aria-label="Rentas primarias pagadas al exterior en 2024, por país de América Latina">{g}</svg>'

def svg_filas(items, aria, ref=None):
    """items: [(rótulo, valor, texto del valor, título, destacar)] → barras horizontales, cada una con su rótulo encima.
    ref: (valor, texto) dibuja una línea segmentada de referencia."""
    mx = max(v for _, v, _, _, _ in items) * 1.0; g = ""
    for i, (nom, v, txt, tit, dest) in enumerate(items):
        y = 2 + i * 38; w = 290 * v / mx
        g += (f'<text class="seg-r" x="0" y="{y + 9}">{nom}</text>'
              f'<rect class="{"col-proy" if dest else "col"}" x="0" y="{y + 13}" width="{w:.1f}" height="16"><title>{tit}</title></rect>'
              f'<text class="col-n col-n-ch" x="{w + 8:.1f}" y="{y + 27}">{txt}</text>')
    alto = 4 + 38 * len(items)
    if ref:
        xr = 290 * ref[0] / mx
        g += (f'<line class="ley-l" x1="{xr:.1f}" y1="10" x2="{xr:.1f}" y2="{alto}"/>'
              f'<text class="ley-t" x="{xr + 4:.1f}" y="{alto + 9}">{ref[1]}</text>')
        alto += 12
    return f'<svg class="est-graf" viewBox="0 0 420 {alto}" role="img" aria-label="{aria}">{g}</svg>'

def svg_sindicalizacion():
    """Columnas por rama (donde se trabaja), de mayor a menor, con la línea del total."""
    CORTO = {"Minería": "Minería", "Actividades financieras y de seguros": "Finanzas", "Construcción": "Construcción", "Agricultura y pesca": "Agro",
             "Alojamiento y servicio de comidas": "Alojamiento", "Comercio": "Comercio", "Enseñanza": "Enseñanza", "Salud y asistencia social": "Salud", "Industria manufacturera": "Industria"}
    total = float(next(r["tasa_rama_trabaja"] for r in sind if r["rama"] == "Total"))
    filas = sorted([r for r in sind if r["rama"] != "Total"], key=lambda r: -float(r["tasa_rama_trabaja"]))
    n = len(filas); gap = 4; bw = (420 - gap * (n - 1)) / n; base = 112; mx = float(filas[0]["tasa_rama_trabaja"])
    def yy(v): return base - (base - 14) * v / mx
    g = f'<line class="eje-l" x1="0" y1="{base}" x2="420" y2="{base}"/>'
    for i, r in enumerate(filas):
        v = float(r["tasa_rama_trabaja"]); x = i * (bw + gap)
        g += f'<rect class="{"col" if v >= total else "col-proy"}" x="{x:.1f}" y="{yy(v):.1f}" width="{bw:.1f}" height="{base - yy(v):.1f}"><title>{r["rama"]}: {fmt(v,1)} % de sindicalización (diciembre de 2024)</title></rect>'
        if r["rama"] in ("Minería", "Actividades financieras y de seguros", "Industria manufacturera", "Enseñanza", "Comercio", "Construcción"):
            g += f'<text class="eje-t eje-rot" x="{x + bw/2:.1f}" y="{base + 6}" transform="rotate(40 {x + bw/2:.1f} {base + 6})">{CORTO[r["rama"]]}</text>'
    g += (f'<line class="ley-l" x1="0" y1="{yy(total):.1f}" x2="420" y2="{yy(total):.1f}"/>'
          f'<text class="ley-t" x="416" y="{yy(total) - 4:.1f}" text-anchor="end">total {fmt(total,1)} %</text>')
    return f'<svg class="est-graf" viewBox="0 0 420 {base + 48}" role="img" aria-label="Tasa de sindicalización por rama de actividad, diciembre de 2024">{g}</svg>', total, filas

def svg_sale_queda(items):
    """items: [(rótulo, sale, queda, título)] → una barra por fila partida en lo que sale y lo que queda."""
    g = ""
    for i, (nom, sale, queda, tit) in enumerate(items):
        y = 2 + i * 44; tot = sale + queda; ws = 420 * sale / tot
        g += (f'<text class="seg-r" x="0" y="{y + 9}">{nom}</text>'
              f'<rect class="col-proy" x="0" y="{y + 13}" width="{ws:.1f}" height="20"><title>{tit[0]}</title></rect>'
              f'<rect class="col" x="{ws:.1f}" y="{y + 13}" width="{420 - ws:.1f}" height="20"><title>{tit[1]}</title></rect>'
              f'<text class="seg-n seg-n-ch" x="{ws/2:.1f}" y="{y + 28}" text-anchor="middle">sale {fmt(sale/tot*100)} %</text>'
              f'<text class="seg-n seg-n-ch" x="{ws + (420 - ws)/2:.1f}" y="{y + 28}" text-anchor="middle">queda {fmt(queda/tot*100)} %</text>')
    return f'<svg class="est-graf" viewBox="0 0 420 {2 + 44 * len(items)}" role="img" aria-label="De cada dólar de ganancia de la inversión extranjera, cuánto sale y cuánto queda reinvertido">{g}</svg>'

def bandas():
    cae = kpi("CAE — cartera / mora"); gs = gasto[-1]
    edu_max = max(float(r["educacion"]) for r in gasto); gst_max = max(gasto, key=lambda r: float(r["gasto_social_total"]))
    svg_edu = svg_cols([(r["anio"] if i % 2 == 0 or i == len(gasto) - 1 else "", float(r["educacion"]), f'Gasto público en educación {r["anio"]}: {fmt(float(r["educacion"]),1)} % del PIB', float(r["educacion"]) == edu_max) for i, r in enumerate(gasto)],
                       "Gasto público en educación, en porcentaje del PIB, por año")
    svg_gst = svg_cols([(r["anio"] if i % 2 == 0 or i == len(gasto) - 1 else "", float(r["gasto_social_total"]), f'Gasto público social {r["anio"]}: {fmt(float(r["gasto_social_total"]),1)} % del PIB', r is gst_max) for i, r in enumerate(gasto)],
                       "Gasto público social, en porcentaje del PIB, por año")
    s = sol_des[-1]
    # I · medios de producción, financieros y de reproducción: peso de cada uno en la economía
    pib_tot = float(next(r["usd_millones"] for r in pib_act if r["grupo"] == "total"))
    def grupo(gk): return sum(float(r["usd_millones"]) for r in pib_act if r["grupo"] == gk) / pib_tot * 100
    g_prod, g_fin, g_rep = grupo("produccion"), grupo("financiero_inmobiliario"), grupo("reproduccion_pagada")
    tnr_amp = float(tnr["pct_pib_ampliado"]); tnr_pib = tnr_amp / (100 - tnr_amp) * 100
    anio_pib = pib_act[0]["anio"]
    svg_medios = svg_filas([
        ("Producción · agro, minería, industria, energía, construcción, comercio, transporte", g_prod, f'{fmt(g_prod,1)} %', f'Actividades productivas: {fmt(g_prod,1)} % del PIB ({anio_pib})', False),
        ("Financieros · banca, seguros, inmobiliarias y servicios a empresas", g_fin, f'{fmt(g_fin,1)} %', f'Intermediación financiera, inmobiliarias y servicios empresariales: {fmt(g_fin,1)} % del PIB ({anio_pib})', False),
        ("Reproducción pagada · Estado, enseñanza, salud, servicios sociales", g_rep, f'{fmt(g_rep,1)} %', f'Administración pública, enseñanza, salud y servicios sociales y personales: {fmt(g_rep,1)} % del PIB ({anio_pib})', False),
        ("Reproducción no pagada · trabajo doméstico y de cuidados", tnr_pib, f'≈ {fmt(tnr_pib,1)} %', f'Trabajo doméstico y de cuidados no remunerado ({tnr["anio"]}): {fmt(tnr_amp,1)} % del PIB ampliado, equivalente a {fmt(tnr_pib,1)} % del PIB. No se cuenta en el PIB. {fmt(float(tnr["pct_aportado_por_mujeres"]),1)} % lo aportan mujeres', True)],
        "Peso de los medios de producción, financieros y de reproducción en la economía, en porcentaje del PIB")
    # II · quién decide en el trabajo: sindicalización por rama
    svg_sind, sind_total, sind_filas = svg_sindicalizacion()
    # III · de cada dólar de ganancia del capital extranjero, cuánto sale y cuánto queda
    uti24 = float(CL_2024["ied_utilidades_dividendos"]); reinv_cl = ied_comp["reinversion_de_utilidades"]
    fresco_cl = ied_comp["participaciones_en_el_capital"] + ied_comp["deuda_relacionada"]
    al_uti24 = float(AL_2024["ied_utilidades_piso"]); reinv_al = IED_AL * 0.52          # CEPAL: la reinversión es 52 % de la IED que entró a la región
    svg_patria = svg_sale_queda([
        ("Chile · ganancia de la inversión extranjera, 2024", uti24 - reinv_cl, reinv_cl,
         (f'Chile 2024: US$ {fmt(uti24 - reinv_cl)} M de utilidades remitidas al exterior', f'Chile 2024: US$ {fmt(reinv_cl)} M reinvertidos — quedan en el país, como capital del inversionista extranjero')),
        ("América Latina · lo mismo, para la región", al_uti24 - reinv_al, reinv_al,
         (f'América Latina 2024: cerca de US$ {fmt(al_uti24 - reinv_al)} M remitidos (estimación: utilidades menos reinversión)', f'América Latina 2024: cerca de US$ {fmt(reinv_al)} M reinvertidos (52 % de la inversión que entró, según CEPAL)'))])
    pos_cl = sorted(pais24, key=lambda r: -float(r["debito_total_2024"])).index(next(r for r in pais24 if r["pais"] == "Chile")) + 1
    return {
        "comun": {"pagina": "secciones/los-medios-comunes.html", "tono": "ds-azul", "modulo": "m2",
                  "titulo": "Lo común capturado · peso de cada circuito",
                  "svg": svg_barras_h([("Fondos de pensiones (AFP), stock", afp_pct, "col-proy"), ("Minería", MIN25, "col"), ("Rentas pagadas al exterior", pib_pct25, "col")], "% del PIB"),
                  "cifras": [(kpi_fmt("AFP — stock de fondos"), f'en fondos de AFP: el salario diferido convertido en capital ({kpi("AFP — stock de fondos")["fecha_corte"]})'),
                             (f'{fmt(float(cae["valor2_numerico"]),1)} %', f'de mora en la cartera del CAE ({cae["fecha_corte"]})')],
                  "pregunta": "¿Cuánto pesa cada medio en la economía? · % del PIB", "mini_svg": svg_medios,
                  "mini": (f'≈ {fmt(tnr_pib)} % del PIB', f'vale el trabajo doméstico y de cuidados que nadie paga ni cuenta: más que la reproducción pagada ({tnr["anio"]})'),
                  "fuente": "Superintendencia de Pensiones · Comisión Ingresa · CEPALSTAT"},
        "jerarquias": {"pagina": "secciones/trabajo-polimorfo.html", "tono": "ds-salmon", "modulo": "m1",
                  "titulo": "El tiempo dividido · la semana obrera",
                  "svg": svg_semana(),
                  "cifras": [(f'{fmt(float(jornada["carga_global_real"]["valor"]))} h', "de carga real a la semana, contra 42 h de jornada legal"),
                             (f'{fmt(float(jornada["tasa_explotacion_sv"]["valor"]),1)} %', "tasa de explotación: plustrabajo sobre trabajo necesario")],
                  "pregunta": "¿Quién decide en el trabajo? · sindicalización por rama", "mini_svg": svg_sind,
                  "mini": (f'{fmt(100 - sind_total)} de cada 100', f'trabajadores no tienen sindicato: sin voz colectiva en las decisiones de la empresa. De {fmt(float(sind_filas[0]["tasa_rama_trabaja"]))} % en minería a {fmt(float(sind_filas[-1]["tasa_rama_trabaja"]))} % en {sind_filas[-1]["rama"].lower()} (dic. 2024)'),
                  "fuente": "Reporte N°1 sobre Fundación SOL (2022) · nivel de referencia"},
        "fronteras": {"pagina": "secciones/proletariado.html", "tono": "ds-azul", "modulo": "m5",
                  "titulo": "Hacia dónde sale el plusvalor · renta pagada en 2024, por destino",
                  "svg": svg_destinos(),
                  "cifras": [(f'US$ {fmt(h("apropiacion_neta_valor"),1)} bill.', "drenados del Sur al Norte en un solo año (2015)"),
                             (f'US$ {fmt(razon_cl,2)}', "salieron de Chile en utilidades por cada dólar de inversión extranjera que entró (2024)")],
                  "pregunta": "De cada dólar de ganancia extranjera, ¿cuánto sale y cuánto queda?", "mini_svg": svg_patria,
                  "mini": (f'US$ {fmt((uti24 - reinv_cl) / fresco_cl, 2)}', "salen de Chile por cada dólar nuevo que entra; y lo que «queda» sigue siendo capital extranjero (2024)"),
                  "fuente": "Banco Central · CEPAL · Hickel et al. (2022)"},
        "estado": {"pagina": "secciones/marchitamiento-del-estado.html", "tono": "ds-salmon", "modulo": "m4",
                  "titulo": "Lo que el Estado retiene · impuesto a las empresas por año",
                  "svg": svg_tasa(),
                  "cifras": [(f'{fmt(next(r["tasa"] for r in TASAS if r["anio"] == ANIO_HOY))} → {fmt(tasa_final)} %', f'rebaja ya promulgada, en régimen en {anio_final}'),
                             (f'{fmt(float(gs["gasto_social_total"]),1)} %', f'del PIB en gasto público social ({gs["anio"]}); ajuste anunciado de US$ {fmt(AJ_TOTAL)} M')],
                  "pregunta": "¿Qué se levanta por fuera del Estado? · protestas por año y tema", "mini_svg": svg_protestas() + leyenda_protestas(), "mini_tono": "ds-papel",
                  "mini_enlace": "secciones/marchitamiento-del-estado.html", "mini_enlace_txt": "ver el detalle →",
                  "mini": (f'{fmt(p_total(P_MAX_ANIO))}', f'acciones de protesta en {P_MAX_ANIO}, el año más alto de veinte; {fmt(p_total(P_ANIOS[-1]))} en {P_ANIOS[-1]}. Fuente: COES'),
                  "fuente": "leyes citadas en el Observatorio · CEPALSTAT (DIPRES) · prensa"},
    }

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sept", "oct", "nov", "dic"]
def seccion_en_cifras(html):
    """Cuenta sobre el HTML de la página: despachos, fuentes distintas y despachos por mes de 2026."""
    arts = re.findall(r'<article class="(?:despacho|indicio)".*?</article>', html, re.S)
    fuentes, por_mes, antes = set(), [0] * 12, 0
    for a in arts:
        meta = re.search(r'<p class="meta">(.*?)</p>', a, re.S)
        if not meta: continue
        m = meta.group(1)
        org = re.search(r'<(?:a|span)[^>]*>(.*?)</(?:a|span)>', m, re.S)
        if org: fuentes.add(re.sub(r"<[^>]+>", "", org.group(1)).strip())
        plano = re.sub(r"<[^>]+>", " ", m)
        f = re.search(r'·\s*(?:corte\s+)?(?:\d{1,2}\s+)?(ene|feb|mar|abr|may|jun|jul|ago|sept?|oct|nov|dic)\b\.?\s*(\d{4})?', plano)
        if not f: continue
        mes = "sept" if f.group(1).startswith("sep") else f.group(1)
        if f.group(2) and f.group(2) != str(ANIO_HOY): antes += 1
        else: por_mes[MESES.index(mes)] += 1
    usados = [i for i, c in enumerate(por_mes) if c]
    if not usados: return ""
    i0, i1 = min(usados), max(usados)
    cols = ([("antes", antes)] if antes else []) + [(MESES[i], por_mes[i]) for i in range(i0, i1 + 1)]
    mx = max(c for _, c in cols); n = len(cols); gap = 8; bw = min(44, (300 - gap * (n - 1)) / n); g = '<line class="eje-l" x1="0" y1="70" x2="300" y2="70"/>'
    for i, (nom, c) in enumerate(cols):
        hh = 54 * c / mx; x = i * (bw + gap)
        if c: g += (f'<rect class="{"col-proy" if (nom != "antes" and c == max(por_mes)) else "col"}" x="{x:.1f}" y="{70 - hh:.1f}" width="{bw:.1f}" height="{hh:.1f}"><title>{"Anteriores a " + str(ANIO_HOY) if nom == "antes" else nom + " " + str(ANIO_HOY)}: {c} {"despacho" if c == 1 else "despachos"}</title></rect>'
                    f'<text class="eje-t" x="{x + bw/2:.1f}" y="{66 - hh:.1f}" text-anchor="middle">{c}</text>')
        g += f'<text class="eje-t" x="{x + bw/2:.1f}" y="84" text-anchor="middle">{nom}</text>'
    return f'''<section class="sec-cifras" aria-label="La sección en cifras">
  <p class="sc-num"><strong>{len(arts)}</strong><span>despachos en esta página</span></p>
  <p class="sc-num"><strong>{len(fuentes)}</strong><span>fuentes distintas</span></p>
  <div class="sc-graf graf-est"><p class="cifra-rot">Despachos por mes</p><svg class="est-graf" viewBox="0 0 300 88" role="img" aria-label="Despachos de esta página por mes">{g}</svg></div>
</section>'''

def banda_html(b, raiz):
    cif = "".join(f'<p><strong class="cifra-num">{v}</strong><span>{t}</span></p>' for v, t in b["cifras"])
    return f'''<section class="dato-seccion {b["tono"]}">
  <div class="ds-graf graf-est"><p class="cifra-rot">{b["titulo"]}</p>{b["svg"]}</div>
  <div class="ds-cifras">{cif}</div>
  <p class="ds-pie">{b["fuente"]} · <a href="{raiz}observatorio.html#{b["modulo"]}">ver en el Observatorio →</a></p>
</section>'''

def mini_html(b):
    v, t = b["mini"]
    return f'''<div class="dato-mini {b.get("mini_tono", b["tono"])}">
        <p class="cifra-rot">{b.get("pregunta", "")}</p>
        <div class="graf-est">{b.get("mini_svg", b["svg"])}</div>
        <p><strong>{v}</strong> {t} · <a href="{b.get("mini_enlace", "observatorio.html#" + b["modulo"])}">{b.get("mini_enlace_txt", "Observatorio →")}</a></p>
      </div>'''

def entre_marcas(texto, ini, fin, nuevo):
    a, b = texto.index(ini) + len(ini), texto.index(fin)
    return texto[:a] + "\n" + nuevo + "\n" + texto[b:]

B = bandas()
# páginas de sección: banda del principio (si la tiene) + la sección en cifras, antes de la rejilla
PAGINAS = ["secciones/los-medios-comunes.html", "secciones/trabajo-polimorfo.html", "secciones/proletariado.html",
           "secciones/marchitamiento-del-estado.html", "secciones/movimientos-de-masas.html", "secciones/estado.html",
           "secciones/organizacion-politica.html", "puntos-reales.html"]
G_INI, G_FIN = "<!-- GRAFICA:INICIO (generado por scripts/build_observatorio.py; no editar a mano) -->", "<!-- GRAFICA:FIN -->"
for ruta in PAGINAS:
    p = RAIZ / ruta; html = p.read_text(encoding="utf-8"); raiz = "../" if "/" in ruta else ""
    if G_INI not in html:
        ancla = '<div class="rejilla-sec">'
        if ancla not in html: print("AVISO: sin rejilla en", ruta); continue
        html = html.replace(ancla, G_INI + "\n" + G_FIN + "\n" + ancla, 1)
    banda = next((banda_html(b, raiz) for b in B.values() if b["pagina"] == ruta), "")
    if ruta == "secciones/marchitamiento-del-estado.html": banda = protestas_pagina()
    html = entre_marcas(html, G_INI, G_FIN, (banda + "\n" if banda else "") + seccion_en_cifras(html))
    if "interactivo.js" not in html:
        html = html.replace("</body>", f'<script src="{raiz}interactivo.js" defer></script>\n</body>')
    p.write_text(html, encoding="utf-8")
print("secciones: gráfica regenerada en", len(PAGINAS), "páginas")

# portada: una banda chica dentro de cada principio
portada = PORTADA.read_text(encoding="utf-8")
for clave, b in B.items():
    ini, fin = f"<!-- GRAFICA-{clave}:INICIO -->", f"<!-- GRAFICA-{clave}:FIN -->"
    if ini not in portada:
        m = re.search(r'(<section id="' + clave + r'" class="seccion"[^>]*>\s*<h2>.*?</h2>\s*<p class="principio">.*?</p>)', portada, re.S)
        if not m: print("AVISO: no se encontró la sección", clave, "en la portada"); continue
        portada = portada[:m.end()] + "\n      " + ini + "\n      " + fin + portada[m.end():]
    portada = entre_marcas(portada, ini, fin, "      " + mini_html(b) + "\n      ")
PORTADA.write_text(portada, encoding="utf-8")
print("index.html: gráfica de los cuatro principios regenerada")

SALIDA.write_text(pagina, encoding="utf-8")
print("observatorio.html regenerado:", len(pagina), "bytes")
print("módulos: termómetro + 5 + cierre · figuras desde datos/observatorio/")
