# El Correo Comunista — Sitio

Sitio estático listo para publicar en el repositorio **`queacontezca/elcorreocomunista`** (GitHub Pages, gratis).

**Idea clave:** el repositorio *es* la página. No hay que «subir» el sitio a otro lugar: GitHub Pages publica tal cual los archivos del repo, y cada vez que el repo se actualiza, la página se actualiza sola al minuto.

---

## 1. Publicar por primera vez (5 minutos)

### Camino A — GitHub Desktop (recomendado para el día a día)

1. Instalar **GitHub Desktop** (desktop.github.com) e iniciar sesión con la cuenta `queacontezca`.
2. Menú **File → Clone repository…** → elegir `queacontezca/elcorreocomunista` → elegir una carpeta local (sugerencia: dentro de `02 Que Acontezca/El Correo Comunista/`).
3. Copiar **el contenido** de esta carpeta `Sitio/` (index.html, styles.css, README.md) dentro de la carpeta clonada.
4. En GitHub Desktop: escribir un resumen («Sitio inicial») → **Commit to main** → **Push origin**.
5. En github.com, entrar al repo → **Settings → Pages** → en *Build and deployment* elegir **Deploy from a branch** → rama `main`, carpeta `/ (root)` → **Save**.
6. Esperar ~1 minuto: la página queda en **https://queacontezca.github.io/elcorreocomunista/**

### Camino B — Solo navegador (sin instalar nada)

1. Entrar a github.com/queacontezca/elcorreocomunista → botón **Add file → Upload files**.
2. Arrastrar `index.html`, `styles.css` y `README.md` → **Commit changes**.
3. Activar Pages igual que en el paso 5 del Camino A.

### Camino C — Terminal (git)

```bash
git clone https://github.com/queacontezca/elcorreocomunista.git
cp index.html styles.css README.md elcorreocomunista/
cd elcorreocomunista
git add -A && git commit -m "Sitio inicial" && git push
# luego activar Pages en Settings → Pages
```

---

## 2. Actualizar el Correo (el día a día)

- **Agregar un despacho:** abrir `index.html`, copiar un bloque `<article class="despacho">…</article>` completo dentro de su sección, cambiar organización, fecha, título, extracto y enlace. Guardar, commit y push (GitHub Desktop lo hace con dos clics).
- **Cambiar la fecha:** editar el matasellos (`<text …>15 AGO 2026</text>`) y la línea `fecha-larga`.
- **Actualizar «La discusión»:** reemplazar los párrafos dentro de `<section id="discusion">`.
- **Agregar imagen a un despacho:** subir la imagen a una carpeta `imagenes/` del repo y, en la tarjeta, cambiar la clase a `con-imagen` y poner `<img src="imagenes/archivo.jpg">` dentro de `<figure class="miniatura">`.
- La automatización por RSS (GitHub Actions) viene en la fase 2; hasta entonces la actualización es manual (10-20 min diarios).

## 3. Estructura

```
elcorreocomunista/          ← el repositorio ES la página
├── index.html              portada del día (secciones = cuatro principios + puntos reales)
├── styles.css              estética postal, paleta de los boletines
├── imagenes/               portadas e imágenes de despachos
├── boletines/              PDF de los Boletines ¡Que Acontezca! (versión ligera para web)
└── README.md               este archivo
```

## 4. Licencia

**Todo este repositorio — código y contenido — está bajo Creative Commons BY 4.0** (ver `LICENSE`): reproducción libre, total o parcial, citando la fuente («El Correo Comunista · Ediciones ¡Que Acontezca!»). Es la fórmula agit-prop: las ideas circulan sin fricción y el nombre viaja con ellas.

**Material de terceros** (los despachos): sigue siendo de sus autoras y autores; se cita con enlace al original (cita legítima, art. 38 Ley 17.336), nunca republicación íntegra sin permiso.

## 5. Notas

- Espejo político en Codeberg y dominio propio: postergados, sin costo.

## 6. Marco legal y política de archivo (decidido 15-08-2026)

**El Correo opera en dos modos, según la licencia de cada fuente:**

1. **Enlace + extracto breve (modo por defecto).** Toda fuente puede despacharse así: título, fecha, medio, extracto corto entre comillas y enlace al original. Amparo: art. 38 de la Ley 17.336 (cita con fines informativos/críticos, indicando fuente y autor). No exige permiso ni licencia abierta.
2. **Espejo de texto completo («repositorio de la discusión pública»).** SOLO para fuentes que lo permiten explícitamente: licencias Creative Commons (respetando sus condiciones: atribución, no-comercial si aplica, compartir igual) o declaraciones del propio medio («se permite la reproducción citando la fuente»). En esos casos el artículo completo puede guardarse en `archivo/` con su ficha (fuente, fecha, URL original, licencia) y presentarse con la estética del Correo, declarando siempre procedencia y licencia.

**Registro de licencias:** cada fuente incorporada queda en el directorio `fuentes.html` con su licencia constatada (y la evidencia: pie de página o declaración del medio). Lo que no tenga licencia abierta constatada se considera «todos los derechos reservados» y opera solo en modo 1.

**Fase 1:** al conversar con las organizaciones, pedir autorización escrita de extractos (y de espejo, si la quieren dar): deja el modo 2 disponible para ellas aunque no usen CC.
