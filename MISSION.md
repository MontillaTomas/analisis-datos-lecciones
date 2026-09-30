# Mission: Introducción al Análisis de Datos (curso público en español)

## Why
Crear una serie de lecciones cortas en español para la materia Introducción al Análisis de Datos (5to año, ISI), publicadas en GitHub Pages, usando un único dataset hilo conductor (`ToyotaCorolla.csv`) y figuras generadas con Python.

## Success looks like
- Un visitante puede recorrer el índice en Pages y abrir cada lección como HTML autocontenido.
- Cada lección deja un win tangible con ejemplo runnable sobre `ToyotaCorolla.csv` y al menos una figura generada con Python.
- Cualquier figura puede regenerarse con `python3 scripts/make_figures.py --only <slug>`.
- Los contenidos cubren las clases de `PLANIFICACION.md` (bloques A–H de la planificación del profesor) con tantas lecciones cortas como cada tema necesite.

## Constraints
- Español. Solo Python. Enfoque "aprender haciendo".
- Lecciones autocontenidas en `lessons/NNNN-slug.html`, estilo compartido en `assets/styles.css`.
- Sin backend: HTML + CSS + JS liviano + PNGs versionados en `assets/img/toyota/` (figuras Python) y `assets/img/catedra/` (slides de cátedra con `figcaption` Fuente UTN-FRT).

## Out of scope
- R (el programa lo menciona, pero este curso genera solo Python).
- Dashboards interactivos con servidor o notebooks como unidad de entrega (el notebook de ejemplo vive como referencia, no como lección).
