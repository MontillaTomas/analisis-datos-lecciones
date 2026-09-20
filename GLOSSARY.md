# Glosario de Introducción al Análisis de Datos

Lenguaje canónico del curso (español). Solo entra un término cuando ya se domina en una lección; no es un diccionario previo.

## Terms

- **Nivel operativo / táctico / estratégico (0002).** Operativo: decisiones diarias caso por caso; táctico: mediano plazo por segmentos; estratégico: largo plazo sobre el rumbo. _Avoid_: usarlos como sinónimos.
- **EDA / diagnóstico / predictivo / prescriptivo (0002).** Explorar cómo son los datos, explicar por qué pasó algo (ex post), predecir valores, recetar la mejor acción futura. _Avoid_: llamar “predictivo” a un conteo descriptivo.
- **Frequent-itemset y soporte (0002).** Ítems que co-ocurren (ej. ABS 81,3 %); soporte = % de casos que los tienen. Base de reglas de asociación (U9). _Avoid_: confundir soporte con confianza.
- **Serie de tiempo y estacionalidad (0002).** Datos ordenados en el tiempo; estacionalidad = ritmo que se repite (ej. mes de fabricación). _Avoid_: tratar meses como nominales sin orden.
- **TDSP y feature engineering (0002).** TDSP = metodología ágil e iterativa de Microsoft (2016) en 5 fases (negocio, datos, modelado, despliegue, aceptación); feature engineering = dar valor a las variables, su paso más complejo. _Avoid_: “TDSP es solo Scrum”.
- **Hipótesis nula H₀ / alternativa H₁ (0003).** H₀ dice “no hay efecto” y se intenta refutar; H₁ dice “sí hay efecto” y es lo que se cree. _Avoid_: “probar H₀” como confirmarla.
- **Regresión lineal y OLS (0003).** Recta Price = β₀ + β₁·KM + ε que describe los puntos; OLS elige los coeficientes minimizando los errores al cuadrado. _Avoid_: “correlación” como sinónimo (correlación mide fuerza, regresión da fórmula).
- **R², residuos/RSS, K-Fold (0003).** R² = % de variación explicada (acá 0,325); residuos = real − predicho y RSS su suma al cuadrado; K-Fold k=10 = validar en 10 cortes rotados (media 0,315 ± 0,042). _Avoid_: leer R² solo sin residuos ni validación.
