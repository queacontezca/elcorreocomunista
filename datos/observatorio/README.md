# Datos del Observatorio — El Correo Comunista

Esta carpeta es la **fuente única de verdad** de las cifras que aparecen en
`observatorio.html`. Ningún número de la página se escribe a mano en el HTML:
el script `scripts/build_observatorio.py` lee estos CSV y genera las figuras.

Reproducción libre, total o parcial, citando la fuente (CC BY 4.0).

## Archivos

| Archivo | Qué contiene | Fuente | Estatus |
|---|---|---|---|
| `rentas_primarias_chile.csv` | Rentas primarias de la balanza de pagos de Chile (2016→2026 T1), millones US$ | CEPALSTAT ind. 547 (compila Banco Central de Chile) | O |
| `rentas_primarias_al20.csv` | Lo mismo para América Latina (20 países, suma simple) | elaboración propia sobre CEPALSTAT | O |
| `rentas_debito_pais_2024.csv` | Renta (débito) por país latinoamericano, 2024 | elaboración propia sobre CEPALSTAT | O |
| `drenaje_mundial_hickel.csv` | Cifras del drenaje Sur→Norte, con su artículo y DOI | Hickel et al. (2021, NPE) y Hickel et al. (2022, GEC) | O |
| `ied_entradas_cepal.csv` | Entradas de IED en AL y Chile; razones de drenaje | CEPAL, *La IED en ALyC 2025* + CEPALSTAT | O |
| `impuesto_primera_categoria.csv` | Serie legal del impuesto a las empresas (1990→2030 proyecto) | leyes citadas; Senado (Boletín 18216-05) | O |
| `jornada_semana_obrera.csv` | Composición de la semana obrera y tasas | Fundación SOL 2022 recalculada (Reporte N°1) | C |
| `kpi_corte.csv` | Indicadores del corte (AFP, CAE, TGR, empleo, cobre, gasto militar) | SP · Comisión Ingresa · TGR · INE · Cochilco · SIPRI | O |
| `mapa_base_paises.svg` | Geometría de 179 países + clasificación céntrico/periférico | Natural Earth · FMI (proxy declarado) | P |

El detalle por serie (definición, URL, frecuencia, fecha de descarga y notas
metodológicas) está en `metadatos.yml`.

## Cómo se actualiza (continuidad con el Reporte de Análisis de Coyuntura)

1. El **Reporte mensual** produce su diccionario de datos del mes.
2. Las cifras que alimentan el Observatorio se **agregan como filas nuevas** a
   estos CSV (nunca se sobrescribe la historia: cada corte queda registrado).
3. Se actualiza `ultima_descarga` en `metadatos.yml`.
4. Se ejecuta `python3 scripts/build_observatorio.py` → regenera
   `observatorio.html` completo.
5. Se sube el paquete (HTML + `datos/`) por la web de GitHub.

## Estatus de medición (declarado en cada figura)

- **O · operativa**: variable fresca con fuente oficial declarada.
- **P · proxy**: mide por aproximación declarada, no el concepto mismo.
- **C · calibración**: base envejecida recalculada — nivel de fondo, no variación.
- **X · placeholder**: sin variable operativa aún — no titula módulos.

## Pendientes declarados (honestidad metodológica)

- Desagregación **bilateral** de las utilidades pagadas (Chile → país de origen
  de la IED): se incorpora desde Banco Central / CEPAL cuando la serie esté
  trazable; mientras, el mapa muestra el flujo agregado con su magnitud real.
- Serie **año a año** del drenaje mundial: vive en los anexos de los artículos
  de Hickel et al.; la página solo grafica los anclajes verificados en abstract.
- `ied_utilidades` de AL es un **piso**: Perú no desagrega esa línea en
  CEPALSTAT y Venezuela/Cuba/Haití no reportan.
