# AGENTS.md

Curso público de lecciones en español (GitHub Pages). HTML estático + Python para figuras. **No hay build, test, lint ni CI**: la verificación es regenerar figuras y abrir el HTML.

## Comandos

```bash
pip install -r requirements.txt
python scripts/make_figures.py --list          # qué figuras hay registradas
python scripts/make_figures.py --only <slug>   # regenerar figuras de una lección
python scripts/make_figures.py --all
python3 -m http.server                         # ver el sitio en http://localhost:8000
```

## Crear una lección (flujo completo — nada es automático)

1. Elegir el próximo número `NNNN` (secuencial; hoy hay 0001–0003) y slug en kebab-case.
2. Escribir `lessons/NNNN-<slug>.html`, autocontenido, enlazando `../assets/styles.css`.
3. Figuras: agregar una función generadora en `scripts/make_figures.py` **y** registrarla en `FIGURE_REGISTRY` (slug → PNG + función) y en `GENERATORS`. Sin registro, `--only <slug>` falla con "Slug sin figuras registradas".
4. Correr `python scripts/make_figures.py --only <slug>` y commitear los PNG (no hay placeholders; toda figura se versiona en `assets/img/toyota/NNNN-<slug>-figN.png`).
5. Agregar el `<li>` con el link de la lección en la unidad correspondiente de `index.html` (si la unidad está vacía, reemplazar el `<li class="meta">Aún no hay lecciones…</li>`).

## Convenciones que difieren de lo esperado

- **Dataset en la raíz**: `ToyotaCorolla.csv` no se mueve; las lecciones lo leen como `../ToyotaCorolla.csv` (rutas relativas a `lessons/`).
- **Sin CSS/JS reutilizable inline**: lo compartible va a `assets/styles.css`. Cada lección tiene su propio `<script>` sólo para su quiz.
- Figuras ~1200 px de ancho (`figsize=(12, …)` + `dpi=100`), títulos y ejes **en español**, estilo consistente con las existentes.
- Quiz: 3–4 opciones del mismo largo (mismo nº de palabras/caracteres, sin pistas por formato), feedback inmediato.
- `<abbr title="definición breve">` en toda abreviatura y término clave nuevo. Tono para principiantes: explicaciones largas, cada concepto se presenta cuando aparece.
- Nav prev/next + índice al final (`nav.lesson-nav`), y al menos una fuente primaria de `RESOURCES.md`.
- Inglés sólo en código/identificadores; todo el contenido del sitio es español.

## Reglas del contenido (de MISSION.md / NOTES.md)

- Solo Python (pandas, numpy, matplotlib, seaborn, statsmodels, scikit-learn). **R está fuera de alcance** aunque `PROGRAMA.md` lo mencione.
- ~3 lecciones cortas por unidad de `PROGRAMA.md` (sugerencia, no límite). Una win tangible + quiz por lección.
- U4 (missingness): el CSV no tiene celdas vacías — la missingness se **inyecta artificialmente** y debe documentarse.
- U6 debe replicar por partes `reference/analisis-ejemplo-ols.html` (referencia canónica de flujo OLS).
- Idiosincrasias del CSV (ver `reference/toyota-data-dictionary.html`): `Model` con `?` inicial (~147 filas), `KM=1` sospechosos, `Fuel_Type` desbalanceado (Petrol/Diesel/CNG), rarezas en `cc`/`Doors`/`Gears`.
- Notebooks y dashboards con servidor no son unidad de entrega.

## Otros

- Skill de contenido: `teach` en `.agents/skills/teach/` (fijada por `skills-lock.json`). Sus formatos (`MISSION-FORMAT.md`, `RESOURCES-FORMAT.md`, `LEARNING-RECORD-FORMAT.md`, `GLOSSARY-FORMAT.md`) gobiernan esos archivos.
- `GLOSSARY.md` es la referencia de términos: respetarla en todas las lecciones.
- Deploy: GitHub Pages desde branch `main`, carpeta `/root`; `.nojekyll` ya existe. `index.html` + `lessons/` + `assets/` se sirven tal cual (por eso los PNG van versionados).
