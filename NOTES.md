# NOTES.md — preferencias y notas de trabajo

- Idioma: español (todo el contenido面向 estudiante hispanohablante).
- Stack: solo Python (pandas, matplotlib, seaborn, statsmodels, scikit-learn, numpy).
- Dataset único hilo conductor: `ToyotaCorolla.csv` en la raíz (no mover; las lecciones lo referencian como `../ToyotaCorolla.csv`).
- Figuras: siempre generadas con Python y versionadas en `assets/img/toyota/` con nombre `NNNN-slug-figN.png`. Nada de placeholders dibujados a mano. Títulos y ejes en español, ~1200 px de ancho, estilo consistente.
- Regeneración: `python scripts/make_figures.py --only <slug>` (ver `requirements.txt`).
- Granularidad: varias lecciones cortas por unidad (~3 como sugerencia, no hard limit). Un win por lección + quiz con feedback inmediato.
- Referencia canónica de flujo OLS+diagnóstico: `reference/analisis-ejemplo-ols.html` (derivado del notebook de ejemplo). Las lecciones de regresión lo replican por partes.
- Particularidades conocidas del CSV (ver `reference/toyota-data-dictionary.html`): `Model` con `?` inicial (~147 filas), `KM=1` sospechosos, `Fuel_Type` desbalanceado (Petrol/Diesel/CNG), rarezas en `cc`/`Doors`/`Gears`. Sin celdas vacías: la missingness de U4 se inyecta artificialmente y se documenta.
- Pages: deploy desde branch `main`, carpeta `/root`. `.nojekyll` presente.
