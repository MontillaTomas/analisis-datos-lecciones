# Introducción al Análisis de Datos — lecciones (ES, solo Python)

Curso público en GitHub Pages. Hilo conductor: `ToyotaCorolla.csv` (1436 filas, 37 columnas).
Toda lección incluye figura(s) generada(s) con Python + código runnable.

## Ver el sitio

- Local: abrir `index.html` en el navegador, o `python3 -m http.server` y visitar `http://localhost:8000`.
- GitHub Pages: repo público → Settings → Pages → Deploy from branch `main`, carpeta `/root`.
  El archivo `.nojekyll` ya está incluido. `index.html` + `lessons/` + `assets/` se sirven tal cual.

## Instalar dependencias de figuras

```bash
pip install -r requirements.txt
python scripts/make_figures.py --help
python scripts/make_figures.py --only <slug>
```

## Generar una lección (skill `teach`)

Las lecciones viven en `lessons/NNNN-slug.html` (numeración secuencial), autocontenidas,
enlazando `../assets/styles.css`. Prompt tipo:

> Usando la skill teach, genera `lessons/0001-xxx.html` en español, solo Python sobre
> `ToyotaCorolla.csv`, enlazando `../assets/styles.css`, con ≥1 figura PNG en
> `assets/img/toyota/` + snippet generador, quiz de 3–4 opciones del mismo largo con
> feedback inmediato, 1 fuente primaria de `RESOURCES.md`, nav prev/next + índice,
> sin CSS/JS reutilizable inline.

Reglas (ver `NOTES.md`): ~3 lecciones cortas por unidad como sugerencia (no hard limit),
ruta al dataset `../ToyotaCorolla.csv`, figuras ~1200 px con títulos/ejes en español,
U4 con missingness inyectada y documentada, U6 replicando por partes
`reference/analisis-ejemplo-ols.html`.

## Estructura

```
index.html  MISSION.md  RESOURCES.md  GLOSSARY.md  NOTES.md  PROGRAMA.md
ToyotaCorolla.csv  requirements.txt  .nojekyll
assets/styles.css  assets/img/toyota/
scripts/make_figures.py
lessons/  reference/  learning-records/
```
