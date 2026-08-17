# El Correo Comunista — Sitio (en proceso de construcción; versión publicada actualmente no corresponde a la definitiva que se proyecta lanzar en octubre de este año)

Sitio público de **El Correo Comunista · ¡Centralización de la discusión!**, proyecto de Ediciones ¡Que Acontezca! (Organización Acontecimiento), de fines públicos.

**URL:** https://queacontezca.github.io/elcorreocomunista

## Nota editorial

Este correo nace de una convicción: la discusión comunista existe, pero circula dispersa entre organizaciones, revistas y militantes que escriben. Aquí la reunimos mes a mes para hacer visibles sus tensiones, sus puntos comunes y sus diferencias — no para dirimir quién tiene la razón, sino para empujar el debate, continuarlo, abrirle caminos. Este espacio es también el órgano de difusión de la Organización Acontecimiento: en él circulan nuestros boletines y nuestra propia voz, como una voz más entre las que apuestan por reorientar la Idea del comunismo en nuestro tiempo.

No es un diario de noticias: es un **repositorio del estado de la discusión** — qué es el Estado, qué hace un movimiento de masas, qué hace una organización —, porque ese es el eje de la discusión para reactivar la Idea del comunismo. Una vez al mes este repositorio queda en **revisión cero**.

El sitio se organiza así: la **portada local** (Chile) despacha lo publicado por organizaciones, revistas y militantes; las **secciones** ordenan esa discusión por los cuatro principios del comunismo —los medios comunes, el trabajo polimorfo, el proletariado, el marchitamiento del Estado— más los **puntos reales**; la fila **La Idea del comunismo** lee los tres elementos del eje — movimientos de masas (lo real), Estado (lo simbólico) y organización política (el anudamiento) —; el **observatorio** expone los datos del análisis de coyuntura; y los **boletines** son la producción propia. La fecha de la portada es la de su **última actualización**: la estructura es permanente y avanza el debate.

**Próxima edición del boletín:** N°4 · **«Justicia y política»** — prevista para **octubre de 2026**. Allí discutiremos: educación, movimientos de masa, Estado y organización política.

## 1. Estructura del repositorio

```
elcorreocomunista/
├── index.html            ← portada local (Chile)
├── styles.css            ← hoja de estilos única (paleta boletín)
├── america-latina.html   ← escala América Latina
├── mundo.html            ← escala Mundo (en formación)
├── puntos-reales.html    ← subsección Puntos reales
├── observatorio.html     ← observatorio de coyuntura (gráficos + mapa del drenaje)
├── boletines.html        ← página principal de los boletines
├── fuentes.html          ← directorio de fuentes con licencia constatada
├── nota-editorial.html   ← nota editorial y quiénes somos
├── README.md             ← este archivo
├── LICENSE               ← CC BY 4.0
├── datos/observatorio/   ← capa de datos del observatorio (CSV + metadatos.yml)
├── scripts/              ← build_observatorio.py (CSV → observatorio.html)
├── boletines/            ← ediciones y artículos HTML + PDF descargables
├── secciones/            ← las 4 páginas de principios del comunismo
└── imagenes/             ← logos, portadas y láminas de los boletines
```

**El observatorio es reproducible:** ninguna cifra de `observatorio.html` se escribe a mano; todas salen de `datos/observatorio/` (CSV con fuente, URL, fecha de descarga y estatus de medición en `metadatos.yml`), y la página se regenera con `python3 scripts/build_observatorio.py`. Cada figura declara su ficha del dato (definición, fuente, fecha de corte, estatus O/P/C/X, método y pendientes).

## 2. Licencia

**Todo este repositorio — código y contenido — está bajo Creative Commons BY 4.0** (ver `LICENSE`): reproducción libre, total o parcial, citando la fuente («El Correo Comunista · Ediciones ¡Que Acontezca!»). Es la fórmula agit-prop: las ideas circulan sin fricción y el nombre viaja con ellas.

**Contenido de terceros:** cada despacho enlaza a su publicación original y cita un extracto breve — el derecho de cita con fines informativos y críticos (art. 38, Ley 17.336). Los textos completos de terceros solo se reproducen cuando su licencia lo permite explícitamente (ver el registro por fuente en `fuentes.html`).
