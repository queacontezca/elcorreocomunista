# Datos del Observatorio — El Correo Comunista

Esta carpeta es la **fuente única de verdad** de las cifras que aparecen en
`observatorio.html`. Ningún número de la página se escribe a mano en el HTML:
el script `scripts/build_observatorio.py` lee estos CSV y genera las figuras.

Reproducción libre, total o parcial, citando la fuente (CC BY 4.0).

## Archivos

| Archivo | Qué contiene | Fuente | Estatus |
|---|---|---|---|
| `rentas_primarias_chile.csv` | Rentas primarias de la balanza de pagos de Chile (2016→2026, parcial T1+T2), millones US$ | CEPALSTAT ind. 547 (compila Banco Central de Chile) | O |
| `rentas_primarias_chile_trimestral.csv` | El mismo flujo por trimestre (2023 T1→2026 T2) | CEPALSTAT ind. 547 | O |
| `rentas_primarias_al20.csv` | Lo mismo para América Latina (20 países, suma simple) | elaboración propia sobre CEPALSTAT | O |
| `rentas_debito_pais_2024.csv` | Renta (débito) por país latinoamericano, 2024 | elaboración propia sobre CEPALSTAT | O |
| `drenaje_mundial_hickel.csv` | Cifras del drenaje Sur→Norte, con su artículo y DOI | Hickel et al. (2021, NPE) y Hickel et al. (2022, GEC) | O |
| `ied_entradas_cepal.csv` | Entradas de IED en AL y Chile; razones de drenaje | CEPAL, *La IED en ALyC 2025* + CEPALSTAT | O |
| `impuesto_primera_categoria.csv` | Serie legal del impuesto a las empresas (1990→2029, ley promulgada el 09-10-2026) | leyes citadas; prensa mientras no se publique en el Diario Oficial | O |
| `acciones_de_protesta_coes.csv` | Acciones de protesta en Chile por año (2005-2024) y por tema de la demanda principal: **solo totales agregados**, no la base | Observatorio de Conflictos, COES (Harvard Dataverse, doi:10.7910/DVN/GKQXBR), base 2005-2024 v1; agrupación de temas propia | P |
| `movilizaciones_registro.csv` | Registro propio de movilizaciones, desde agosto de 2026: borrador con las noticias reunidas para la edición de octubre; cada fila declara si su fuente fue abierta | Elaboración propia sobre las fuentes enlazadas | X |
| `sindicalizacion_por_rama.csv` | Tasa de sindicalización por rama de actividad, diciembre de 2024 (según la empresa que paga y según donde se trabaja) | INE, Documento de Trabajo «Tasa de sindicalización según actividad económica» (febrero de 2026), Cuadro 9 | O |
| `pib_por_actividad_chile.csv` | PIB de Chile 2025 por actividad, agrupado en producción, financiero-inmobiliario y reproducción pagada (agrupación propia) | CEPALSTAT ind. 2215 (compila Banco Central) | O |
| `trabajo_no_remunerado_chile.csv` | Valor del trabajo doméstico y de cuidados no remunerado, 2023 | Ministerio de Hacienda y ComunidadMujer (nota del 13-10-2025) | P |
| `ied_componentes_chile.csv` | Componentes del flujo de inversión extranjera directa, 2024 | InvestChile sobre cifras del Banco Central | O |
| `desempleo_integral_sol.csv` | Tasa de desempleo, Tasa de Desempleo Integral (subempleo + desaliento), subempleo profesional, informalidad y externalización, por trimestre móvil | Fundación SOL, Serie IMCE (sobre la ENE del INE) | O |
| `jornada_semana_obrera.csv` | Composición de la semana obrera y tasas | Fundación SOL 2022 recalculada (Reporte N°1) | C |
| `kpi_corte.csv` | Indicadores del corte (AFP, CAE, TGR, empleo, cobre, gasto militar, capex digital/IA) — formato máquina: `valor_numerico` + `plantilla` de despliegue | SP · Comisión Ingresa · TGR · INE · Cochilco · SIPRI | O (capex digital/IA: X, pendiente) |
| `kpi_historial.csv` | Valores de los indicadores en cortes anteriores (no se pierde la historia) | las mismas fuentes | O |
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

- **Corte 11-10-2026:** la megarreforma está promulgada pero no publicada en el
  Diario Oficial; su calendario y la cifra del Presupuesto 2027 se citan de prensa
  y deben reemplazarse por la fuente oficial (Diario Oficial, DIPRES).
- La serie regional (`rentas_primarias_al20.csv`) no se actualizó: solo seis países
  reportan 2026 T2.
- Desagregación **bilateral** de las utilidades pagadas (Chile → país de origen
  de la IED): se incorpora desde Banco Central / CEPAL cuando la serie esté
  trazable; mientras, el mapa muestra el flujo agregado con su magnitud real.
- Serie **año a año** del drenaje mundial: vive en los anexos de los artículos
  de Hickel et al.; la página solo grafica los anclajes verificados en abstract.
- `ied_utilidades` de AL es un **piso**: Perú no desagrega esa línea en
  CEPALSTAT y Venezuela/Cuba/Haití no reportan.
