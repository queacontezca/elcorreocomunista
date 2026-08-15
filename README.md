# El Correo Comunista — Sitio

Sitio público de **El Correo Comunista · ¡Centralización de la discusión!**, proyecto de Ediciones ¡Que Acontezca! (Organización Acontecimiento), de fines públicos.

**Idea clave:** este repositorio *es* la página. GitHub Pages publica tal cual estos archivos en <https://queacontezca.github.io/elcorreocomunista/> — cada cambio subido al repo actualiza el sitio solo, al minuto.

---

## 1. Estado actual

- Sitio **ya publicado** y en circulación (15-08-2026).
- Estructura permanente: la portada no cambia de número; solo avanza el debate. La cabecera muestra siempre la **última fecha de actualización** (ritmo: cada dos semanas).
- Licencia de todo el repo: **CC BY 4.0** (ver `LICENSE`).

## 2. Actualizar el sitio (flujo web, sin instalar nada)

En github.com/queacontezca/elcorreocomunista:

1. **Add file ▾ → Upload files**
2. Arrastrar los archivos modificados (subir un archivo con el mismo nombre **lo sobrescribe**: eso es «actualizar»)
3. **Commit changes** → esperar ~1 minuto → recargar con ⌘⇧R

> Si se prefiere trabajar local: la carpeta `elcorreocomunista/` en el Mac es un clon del repo; se puede editar ahí y subir con GitHub Desktop (commit + Push origin). Ambos flujos conviven; el web basta para todo.

## 3. Tareas frecuentes

- **Agregar un despacho:** en `index.html`, copiar un bloque `<article class="despacho">…</article>` dentro de su sección y cambiar medio, lugar `(País)` o `(Chile · Región)`, fecha, título, extracto y URL del original. Actualizar el contador de la caja de fecha y la **fecha de última actualización** (banda superior + caja + aviso al pie).
- **Actualizar «La discusión»:** reemplazar los párrafos de cada panel dentro de `<section id="discusion">`; citar siempre con enlaces `→ #dN` al despacho correspondiente (verificabilidad).
- **Nuevo boletín** (p. ej. N°4 en octubre): subir el PDF a `boletines/` (comprimirlo antes para web, ~150 dpi), crear su página de edición copiando una existente (`boletines/n3-tiempos-de-libertad.html`), crear las páginas de sus artículos, y agregarlo al lateral «Boletines» de `index.html` quitando la marca «en preparación».
- **Nueva fuente:** agregarla en `fuentes.html` con su licencia constatada (ver §5).
- **Imagen en un despacho:** subir la imagen a `imagenes/`, poner al artículo la clase `con-imagen` y un `<figure class="miniatura"><img src="imagenes/archivo.jpg">`.

## 4. Estructura

```
elcorreocomunista/          ← el repositorio ES la página
├── index.html              portada (manifiesto, La discusión + Boletines, secciones, puntos reales)
├── styles.css              estética estafeta grabada, paleta de los boletines
├── fuentes.html            directorio de fuentes con licencia constatada
├── boletines/              ediciones HTML (n1, n2, n3…), páginas por artículo y los PDF
├── imagenes/               portadas e imágenes de despachos
├── LICENSE                 CC BY 4.0 (todo el repo: código y contenido)
└── README.md               este archivo
```

## 5. Licencia y marco legal

**Todo este repositorio — código y contenido — está bajo Creative Commons BY 4.0**: reproducción libre, total o parcial, citando la fuente («El Correo Comunista · Ediciones ¡Que Acontezca!»). Es la fórmula agit-prop: las ideas circulan sin fricción y el nombre viaja con ellas.

**Material de terceros** (los despachos): sigue siendo de sus autoras y autores. Dos modos según la licencia constatada en `fuentes.html`:

1. **Enlace + extracto breve** (todas las fuentes): cita legítima, art. 38 Ley 17.336.
2. **Espejo de texto completo** (solo fuentes con licencia abierta o autorización — hoy: Horizonte, Carcaj, Rebelión, Desinformémonos): respetando sus condiciones (atribución; no-comercial donde aplique; sin modificar donde sea ND).

## 6. Pendientes del proyecto

- Página «Qué es» (estatuto) y «Archivo» por fecha.
- Automatización RSS (GitHub Actions) para las fuentes con feed.
- Observatorio de datos (`datos/chile/`): series del análisis de coyuntura, públicas para las luchas.
- Espejo en Codeberg y dominio propio: postergados, sin costo.
