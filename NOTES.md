# NOTES.md — preferencias y notas de trabajo

- Idioma: español (todo el contenido para el estudiante hispanohablante).
- Stack: solo Python (pandas, matplotlib, seaborn, statsmodels, scikit-learn, numpy).
- Dataset único hilo conductor: `ToyotaCorolla.csv` en la raíz (no mover; las lecciones lo referencian como `../ToyotaCorolla.csv`).
- Figuras: siempre generadas con Python y versionadas en `assets/img/toyota/` con nombre `NNNN-slug-figN.png`. Nada de placeholders dibujados a mano. Títulos y ejes en español, ~1200 px de ancho, estilo consistente. Excepción: slides de cátedra (PDFs `utn_frt_ieyd_*`) renderizadas con `pdftoppm` a `assets/img/catedra/<bloque>/`, siempre con `figcaption` "Fuente: cátedra UTN-FRT".
- Regeneración: `python3 scripts/make_figures.py --only <slug>` (ver `requirements.txt`).
- Granularidad: lecciones cortas por clase de `PLANIFICACION.md` (bloques A–H; tantas como cada tema necesite, sin regla de N por bloque). Un win por lección + quiz con feedback inmediato.
- Referencia canónica de flujo OLS+diagnóstico: `reference/analisis-ejemplo-ols.html` (derivado del notebook de ejemplo). Las lecciones de regresión lo replican por partes.
- Particularidades conocidas del CSV (ver `reference/toyota-data-dictionary.html`): `Model` con `?` inicial (~147 filas), `KM=1` sospechosos, `Fuel_Type` desbalanceado (Petrol/Diesel/CNG), rarezas en `cc`/`Doors`/`Gears`. Sin celdas vacías: la missingness de 0015–0018 (Bloque C) se inyecta artificialmente y se documenta.
- Tono: explicar como a alguien sin conocimientos previos; explicaciones un poco más largas,
  cada concepto se presenta cuando aparece. Abreviaturas y términos clave siempre con
  `<abbr title="definición breve">` para ver el significado al pasar el cursor.
- Pages: deploy desde branch `main`, carpeta `/root`. `.nojekyll` presente.
