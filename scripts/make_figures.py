#!/usr/bin/env python3
"""Regenera las figuras PNG del curso desde ToyotaCorolla.csv.

Toda figura que aparece en una lección DEBE generarse con este script
(o con un snippet equivalente incluido en la lección) y versionarse en
assets/img/toyota/ como NNNN-<slug>-figN.png.

Uso:
    python scripts/make_figures.py --help
    python scripts/make_figures.py --list
    python scripts/make_figures.py --only <slug>
    python scripts/make_figures.py --all

Requiere: pip install -r requirements.txt
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSV = ROOT / "ToyotaCorolla.csv"
IMGDIR = ROOT / "assets" / "img" / "toyota"

# Registro de figuras por slug de lección. Cada entrada: (nombre_png, función, descripción).
# Las lecciones futuras agregan aquí su slug + función generadora.
FIGURE_REGISTRY: dict[str, list[tuple[str, str, str]]] = {
    "tipos-de-datos-toyota": [
        ("0001-tipos-de-datos-toyota-fig1.png", "fig_u1_boxplot_price_km",
         "Boxplots de Price y KM (réplica Parte 1 del notebook ejemplo)."),
        ("0001-tipos-de-datos-toyota-fig2.png", "fig_u1_bias_variance_tradeoff",
         "Curvas de bias, varianza y error total vs complejidad (trade-off)."),
    ],
    "niveles-tipos-analisis-tdsp": [
        ("0002-niveles-tipos-analisis-tdsp-fig1.png", "fig_u1_niveles_decision",
         "Operativo/táctico/estratégico con Toyota: scatter, barras por edad y línea por año."),
        ("0002-niveles-tipos-analisis-tdsp-fig2.png", "fig_u1_itemset_estacionalidad",
         "Frequent-itemset (soporte de equipamiento) y estacionalidad por mes de fabricación."),
    ],
    "regresion-lineal-precio-km": [
        ("0003-regresion-lineal-precio-km-fig1.png", "fig_u6_scatter_recta",
         "Dispersión Price vs KM con recta OLS Price = 14508 - 0.055·KM."),
        ("0003-regresion-lineal-precio-km-fig2.png", "fig_u6_residuos",
         "Diagnóstico de residuos: residuos vs predichos + histograma."),
        ("0003-regresion-lineal-precio-km-fig3.png", "fig_u6_kfold",
         "K-Fold k=10: R² por fold para Price ~ KM (media ≈ 0.32)."),
    ],
    "limpieza-datos-toyota": [
        ("0004-limpieza-datos-toyota-fig1.png", "fig_u2_defectos_conteo",
         "Barras: filas afectadas por cada defecto conocido (Model ?, KM, cc, Doors, Gears)."),
        ("0004-limpieza-datos-toyota-fig2.png", "fig_u2_km1_cc_scatter",
         "Scatter Price vs KM con KM<=100 resaltados + histograma de cc con el 16000."),
    ],
    "wrangling-regex-model": [
        ("0005-wrangling-regex-model-fig1.png", "fig_u2_wrangling_validacion",
         "Precio medio por motor extraído del texto + % acuerdo texto vs columna."),
    ],
    "eda-sistematico-toyota": [
        ("0006-eda-sistematico-toyota-fig1.png", "fig_u2_eda_tramos_corr",
         "Precio medio por tramo de edad + correlaciones top con Price (trampa Id)."),
    ],
    "outliers-estadisticos-iqr-z": [
        ("0007-outliers-estadisticos-iqr-z-fig1.png", "fig_u2_outliers_iqr_z",
         "Boxplot de Price con vallas IQR + histograma con umbrales IQR y z."),
    ],
    "outliers-multivariados-lof-dbscan": [
        ("0008-outliers-multivariados-lof-dbscan-fig1.png", "fig_u2_outliers_multi",
         "Scatter KM-Price con outliers Isolation Forest + conteo por método."),
    ],
    "que-grafico-para-que-dato": [
        ("0009-que-grafico-para-que-dato-fig1.png", "fig_u3_catalogo",
         "Catálogo 2x2: barras Fuel_Type, histograma Price, scatter KM-Price, línea por año."),
    ],
    "color-con-criterio": [
        ("0010-color-con-criterio-fig1.png", "fig_u3_color",
         "3 paletas: scatter por Fuel_Type, heatmap edad×fuel, barras corr divergentes."),
    ],
    "eje-truncado-honestidad": [
        ("0011-eje-truncado-honestidad-fig1.png", "fig_u3_eje_truncado",
         "Mismas barras honestas (eje 0) vs truncadas (eje 9000)."),
    ],
    "multivariado-burbujas-heatmap": [
        ("0012-multivariado-burbujas-heatmap-fig1.png", "fig_u3_multivariado",
         "Burbujas KM-Price-Fuel-Edad + heatmap de correlaciones 6x6."),
    ],
    "redes-arboles-equipamiento": [
        ("0013-redes-arboles-equipamiento-fig1.png", "fig_u3_red_arbol",
         "Red de co-ocurrencia de extras + árbol stump caro/barato."),
    ],
    "mapas-texto-dos-visualizaciones": [
        ("0014-mapas-texto-dos-visualizaciones-fig1.png", "fig_u3_texto",
         "Top palabras en Model + histograma de largo del texto."),
    ],
    "faltantes-mecanismos-listwise": [
        ("0015-faltantes-mecanismos-listwise-fig1.png", "fig_u4_mecanismos",
         "HP perdido por tramo (MAR) + filas útiles listwise vs pairwise."),
    ],
    "relleno-simple-media-razon": [
        ("0016-relleno-simple-media-razon-fig1.png", "fig_u4_simple",
         "Histograma KM con pico en la media + corrección por reponderación."),
    ],
    "hot-deck-cold-deck-knn": [
        ("0017-hot-deck-cold-deck-knn-fig1.png", "fig_u4_donantes",
         "Histograma HP real vs KNN + barras RMSE por método."),
    ],
    "imputacion-con-modelos": [
        ("0018-imputacion-con-modelos-fig1.png", "fig_u4_modelos",
         "HP real vs imputado iterativo + ranking RMSE U4."),
    ],
    "por-que-seleccionar": [
        ("0019-por-que-seleccionar-fig1.png", "fig_u5_porque",
         "Train/CV con y sin ruido + inestabilidad por casi-duplicada."),
    ],
    "best-subset-stepwise": [
        ("0020-best-subset-stepwise-fig1.png", "fig_u5_subset",
         "AIC/BIC vs k + CV-R2 vs k con codo en 4."),
    ],
    "ridge-lasso-caminos": [
        ("0021-ridge-lasso-caminos-fig1.png", "fig_u5_caminos",
         "Caminos Lasso (mueren) y Ridge (achican) + selección n=80."),
    ],
    "scad-elastic-filtros": [
        ("0022-scad-elastic-filtros-fig1.png", "fig_u5_scad",
         "Ranking f_regression + curvas de penalización L1/L2/SCAD."),
    ],
    "correlacion-vs-regresion": [
        ("0023-correlacion-vs-regresion-fig1.png", "fig_u6_corr",
         "Scatter KM-Price por cuadrantes + barras r de 5 variables."),
    ],
    "regresion-multiple-ols": [
        ("0024-regresion-multiple-ols-fig1.png", "fig_u6_multiple",
         "Coeficientes estandarizados + real vs predicho (R2 0,741)."),
    ],
    "diagnostico-ols-qq-cook": [
        ("0025-diagnostico-ols-qq-cook-fig1.png", "fig_u6_diag1",
         "QQ-plot + residuos vs predichos del OLS múltiple."),
        ("0025-diagnostico-ols-qq-cook-fig2.png", "fig_u6_diag2",
         "Leverage vs residuos (Cook) + regresión parcial KM."),
    ],
    "regresion-polinomial": [
        ("0026-regresion-polinomial-fig1.png", "fig_u6_poli",
         "Curvas grado 1-2 en Edad + CV por grado Age/KM."),
    ],
    "glm-robusta-bayesiana": [
        ("0027-glm-robusta-bayesiana-fig1.png", "fig_u6_mas",
         "OLS vs RLM en KM-Price + pendientes comparadas."),
    ],
    "distancias-similaridad": [
        ("0028-distancias-similaridad-fig1.png", "fig_u7_dist",
         "Un desvío por variable + segmento distancia estandarizada."),
    ],
    "kmeans-segmentos": [
        ("0029-kmeans-segmentos-fig1.png", "fig_u7_kmeans",
         "Scatter KM-Price por cluster K-Means k=3 + centroides."),
    ],
    "jerarquico-dbscan": [
        ("0030-jerarquico-dbscan-fig1.png", "fig_u7_jer",
         "Dendrograma Ward + scatter DBSCAN con ruido."),
    ],
    "validar-grupos-codo-silueta": [
        ("0031-validar-grupos-codo-silueta-fig1.png", "fig_u7_val",
         "Codo de inercia + silueta por k (premia k=2)."),
    ],
    "pca-biplot-pcr": [
        ("0032-pca-biplot-pcr-fig1.png", "fig_u7_pca",
         "Scree 8 vars + biplot PC1-PC2 con clusters."),
    ],
    "clasificacion-knn": [
        ("0033-clasificacion-knn-fig1.png", "fig_u8_knn",
         "Accuracy vs k (con/sin escala) + matriz de confusión k=25."),
    ],
    "regresion-logistica-roc": [
        ("0034-regresion-logistica-roc-fig1.png", "fig_u8_log",
         "Curva ROC (AUC 0,947) + coeficientes logísticos."),
    ],
    "naive-bayes-arboles": [
        ("0035-naive-bayes-arboles-fig1.png", "fig_u8_nbtree",
         "Train vs CV por profundidad + árbol depth=2 dibujado."),
    ],
    "random-forest-boosting": [
        ("0036-random-forest-boosting-fig1.png", "fig_u8_rf",
         "Barras CV: NB/árbol/RF/HGB + importancias RF."),
    ],
    "svm-comparacion": [
        ("0037-svm-comparacion-fig1.png", "fig_u8_svm",
         "Frontera SVM 2D (lineal vs RBF) + torneo de 7 algoritmos."),
    ],
    "muestreo-sesgo": [
        ("0038-muestreo-sesgo-fig1.png", "fig_u1_muestreo",
         "Distribución de medias n=30/100/500 + muestra sesgada."),
    ],
    "soporte-itemsets": [
        ("0039-soporte-itemsets-fig1.png", "fig_u9_sop",
         "Soportes 16 extras + cadena de monotonicidad."),
    ],
    "reglas-confianza-lift": [
        ("0040-reglas-confianza-lift-fig1.png", "fig_u9_reglas",
         "Barras confianza vs lift: el ranking se da vuelta."),
    ],
    "algoritmo-apriori": [
        ("0041-algoritmo-apriori-fig1.png", "fig_u9_apriori",
         "Candidatos vs frecuentes por nivel + total vs min_sop."),
    ],
    "inferencia-pvalor-t": [
        ("0042-inferencia-pvalor-t-fig1.png", "fig_u6_inf",
         "Distribución t con zonas de rechazo + barras t por variable."),
    ],
    "metricas-split-80-20": [
        ("0043-metricas-split-80-20-fig1.png", "fig_u6_met",
         "RMSE/MAE simple vs múltiple en test + MAPE/R²."),
    ],
    "anova-comparar-medias": [
        ("0044-anova-comparar-medias-fig1.png", "fig_u6_anova",
         "Violín Price×Fuel + distribución F con F=3,12."),
    ],
    "violin-densidad-torta": [
        ("0045-violin-densidad-torta-fig1.png", "fig_u3_viol",
         "Violín×edad + hist-vs-KDE + torta ilegible."),
    ],
    "transformaciones-log-discretizar": [
        ("0046-transformaciones-log-discretizar-fig1.png", "fig_u2_trans",
         "Price crudo vs log (skew) + edad discretizada."),
    ],
}


def _need_deps():
    try:
        import pandas  # noqa: F401
        import matplotlib  # noqa: F401
        import seaborn  # noqa: F401
    except ImportError as exc:
        print(f"Faltan dependencias: {exc}\nInstalá con: pip install -r requirements.txt",
              file=sys.stderr)
        sys.exit(2)


def check_csv() -> None:
    if not CSV.exists():
        print(f"No se encontró {CSV}. El dataset debe vivir en la raíz.", file=sys.stderr)
        sys.exit(1)


def fig_u1_boxplot_price_km(out: Path) -> Path:
    """Boxplots de Price y KM. Plantilla del EDA del notebook ejemplo."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV).dropna(subset=["KM", "Price"])
    fig, axes = plt.subplots(1, 2, figsize=(12, 4))
    sns.boxplot(y=df["KM"], ax=axes[0], color="skyblue")
    axes[0].set_title("Boxplot de KM")
    sns.boxplot(y=df["Price"], ax=axes[1], color="lightgreen")
    axes[1].set_title("Boxplot de Price")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u1_bias_variance_tradeoff(out: Path) -> Path:
    """Trade-off sesgo-varianza: error vs complejidad (figura didáctica sintética)."""
    _need_deps()
    import numpy as np
    import matplotlib.pyplot as plt

    x = np.linspace(0, 10, 200)
    bias2 = 8 * np.exp(-0.7 * x) + 0.2          # sesgo^2: cae con la complejidad
    variance = 0.08 * x**2 + 0.05 * x           # varianza: crece con la complejidad
    irreducible = np.full_like(x, 1.0)          # error irreducible (ruido)
    total = bias2 + variance + irreducible      # error total en forma de U
    k_opt = float(x[int(np.argmin(total))])

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.plot(x, bias2, label="Sesgo² (bias²): cae", linewidth=2, color="#1f77b4")
    ax.plot(x, variance, label="Varianza: crece", linewidth=2, color="#ff7f0e")
    ax.plot(x, total, label="Error total (test): forma de U", linewidth=2.5, color="#2ca02c")
    ax.axhline(1.0, linestyle="--", label="Error irreducible (ruido)", color="#7f7f7f")
    ax.axvline(k_opt, linestyle=":", linewidth=1.5, color="#333333")
    ax.text(k_opt + 0.15, float(total.min()) + 0.15, "óptimo\n(no sobre ni sub)",
            fontsize=9)
    ax.set_xlabel("Complejidad del modelo → (underfit a la izquierda, overfit a la derecha)")
    ax.set_ylabel("Error")
    ax.set_title("Bias–variance tradeoff: el error total es mínimo en el medio")
    ax.legend(loc="upper center", fontsize=9)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u1_niveles_decision(out: Path) -> Path:
    """Operativo / táctico / estratégico con Toyota (3 paneles reales)."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))

    # Operativo: cada auto (KM vs Price, muestra)
    s = df.sample(n=min(600, len(df)), random_state=42)
    axes[0].scatter(s["KM"], s["Price"], s=10, alpha=0.45, color="#0b5cad")
    axes[0].set_title("Operativo: cada auto (KM vs precio)")
    axes[0].set_xlabel("Kilómetros (KM)")
    axes[0].set_ylabel("Precio (€)")

    # Táctico: precio medio por tramo de antigüedad
    tramos = pd.qcut(df["Age_08_04"], 3, labels=["joven", "media", "vieja"])
    med = df.assign(tramo=tramos).groupby("tramo", observed=True)["Price"].mean()
    sns.barplot(x=med.index.tolist(), y=med.values.tolist(), ax=axes[1], color="#2ca02c")
    axes[1].set_title("Táctico: precio medio por antigüedad")
    axes[1].set_xlabel("Tramo de edad del auto")
    axes[1].set_ylabel("Precio medio (€)")
    for i, v in enumerate(med.values):
        axes[1].text(i, v + 120, f"{v:,.0f}".replace(",", "."), ha="center", fontsize=8)

    # Estratégico: precio medio por año de fabricación
    evo = df.groupby("Mfg_Year")["Price"].mean()
    axes[2].plot(evo.index.tolist(), evo.values.tolist(), marker="o", color="#ff7f0e", linewidth=2)
    axes[2].set_title("Estratégico: precio medio por año fab.")
    axes[2].set_xlabel("Año de fabricación")
    axes[2].set_ylabel("Precio medio (€)")
    axes[2].tick_params(axis="x", rotation=30)

    fig.suptitle("Del operativo al estratégico con el mismo CSV", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u1_itemset_estacionalidad(out: Path) -> Path:
    """Frequent-itemset (soporte de equipamiento) + estacionalidad mensual."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    cols = ["Airco", "ABS", "CD_Player", "Central_Lock", "Powered_Windows",
            "Automatic_airco", "Boardcomputer", "Radio"]
    cols = [c for c in cols if c in df.columns]
    soporte = (df[cols].mean().sort_values(ascending=False) * 100).round(1)
    por_mes = df.groupby("Mfg_Month").size()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=soporte.values.tolist(), y=soporte.index.tolist(), ax=axes[0],
                color="#0b5cad")
    axes[0].set_title("Frequent-itemset: % de autos con cada extra")
    axes[0].set_xlabel("Soporte (% de los 1436 autos)")
    for i, v in enumerate(soporte.values):
        axes[0].text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=8)

    axes[1].bar(por_mes.index.tolist(), por_mes.values.tolist(), color="#2ca02c")
    axes[1].set_title("Serie mensual: autos por mes de fabricación")
    axes[1].set_xlabel("Mes de fabricación (1–12)")
    axes[1].set_ylabel("Cantidad de autos")
    axes[1].set_xticks(range(1, 13))

    fig.suptitle("Patrones: qué extras co-ocurren y cuándo se fabricó", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_scatter_recta(out: Path) -> Path:
    """Dispersión Price vs KM con recta OLS."""
    _need_deps()
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    df = pd.read_csv(CSV).dropna(subset=["KM", "Price"])
    X = df[["KM"]].values
    y = df["Price"].values
    m = LinearRegression().fit(X, y)
    xs = np.linspace(float(df["KM"].min()), float(df["KM"].max()), 200)
    ys = m.predict(xs.reshape(-1, 1))
    r2 = float(m.score(X, y))

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.scatter(df["KM"], df["Price"], s=12, alpha=0.4, color="#0b5cad",
               label="Autos observados (1436)")
    ax.plot(xs, ys, color="#d62728", linewidth=2.2,
            label=f"Recta OLS: precio = {m.intercept_:,.0f} {m.coef_[0]:+.4f}·KM".replace(",", "."))
    ax.set_title(f"Regresión lineal: a más KM, menor precio (R² = {r2:.3f}, r = -0.57)")
    ax.set_xlabel("Kilómetros (KM)")
    ax.set_ylabel("Precio (€)")
    ax.legend(fontsize=9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_residuos(out: Path) -> Path:
    """Residuos vs predichos + histograma de residuos."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression

    df = pd.read_csv(CSV).dropna(subset=["KM", "Price"])
    X = df[["KM"]].values
    y = df["Price"].values
    m = LinearRegression().fit(X, y)
    pred = m.predict(X)
    resid = y - pred

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(pred, resid, s=12, alpha=0.4, color="#ff7f0e")
    axes[0].axhline(0, color="#333333", linestyle="--", linewidth=1.2)
    axes[0].set_title("Residuos vs predicciones (¿nube pareja en 0?)")
    axes[0].set_xlabel("Precio predicho (€)")
    axes[0].set_ylabel("Residuo = real − predicho (€)")

    axes[1].hist(resid, bins=30, color="#0b5cad", alpha=0.8)
    axes[1].axvline(0, color="#333333", linestyle="--", linewidth=1.2)
    axes[1].set_title("Histograma de residuos (¿campana en 0?)")
    axes[1].set_xlabel("Residuo (€)")
    axes[1].set_ylabel("Cantidad de autos")

    fig.suptitle("Diagnóstico: los errores cuentan lo que le falta al modelo", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_kfold(out: Path) -> Path:
    """K-Fold k=10: R² por fold."""
    _need_deps()
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    from sklearn.model_selection import KFold, cross_val_score
    from sklearn.linear_model import LinearRegression

    df = pd.read_csv(CSV).dropna(subset=["KM", "Price"])
    X = df[["KM"]].values
    y = df["Price"].values
    kf = KFold(n_splits=10, shuffle=True, random_state=42)
    r2 = cross_val_score(LinearRegression(), X, y, cv=kf, scoring="r2")

    fig, ax = plt.subplots(figsize=(12, 4.2))
    xs = np.arange(1, 11)
    ax.bar(xs.tolist(), r2.tolist(), color="#2ca02c")
    ax.axhline(float(r2.mean()), color="#333333", linestyle="--", linewidth=1.5,
               label=f"Media R² = {r2.mean():.3f} ± {r2.std():.3f}")
    ax.set_title("Validación cruzada K-Fold (k=10): R² estable ≈ 0.32, no depende de un corte")
    ax.set_xlabel("Fold (cada barra = 10% de autos como test)")
    ax.set_ylabel("R² en test")
    ax.set_xticks(xs.tolist())
    ax.set_ylim(0, max(0.6, float(r2.max()) + 0.1))
    ax.legend(fontsize=9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_defectos_conteo(out: Path) -> Path:
    """Barras horizontales: filas afectadas por cada defecto conocido."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    defectos = {
        "Model con '?' inicial": int(df["Model"].str.startswith("?", na=False).sum()),
        "Gears distinto de 5": int((df["Gears"] != 5).sum()),
        "KM ≤ 100 (sospechoso)": int((df["KM"] <= 100).sum()),
        "Doors = 2 (raro)": int((df["Doors"] == 2).sum()),
        "cc = 16000 (10x típico)": int((df["cc"] > 5000).sum()),
    }
    etiquetas = list(defectos.keys())
    valores = list(defectos.values())

    fig, ax = plt.subplots(figsize=(12, 4.2))
    sns.barplot(x=valores, y=etiquetas, ax=ax, color="#0b5cad")
    ax.set_title("Limpieza Toyota: filas afectadas por cada defecto conocido (de 1436)")
    ax.set_xlabel("Cantidad de filas")
    for i, v in enumerate(valores):
        ax.text(v + 1.5, i, str(v), va="center", fontsize=10)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_km1_cc_scatter(out: Path) -> Path:
    """Scatter Price vs KM con KM<=100 resaltados + histograma de cc."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(CSV)
    raro_km = df["KM"] <= 100

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(df.loc[~raro_km, "KM"], df.loc[~raro_km, "Price"],
                    s=10, alpha=0.35, color="#0b5cad", label="Resto (1427 autos)")
    axes[0].scatter(df.loc[raro_km, "KM"], df.loc[raro_km, "Price"],
                    s=70, alpha=0.95, color="#d62728", label="KM ≤ 100 (9 autos)")
    axes[0].set_title("Price vs KM: 9 autos con KM ≤ 100 en rojo")
    axes[0].set_xlabel("Kilómetros (KM)")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=9)

    cc_tipico = df.loc[df["cc"] <= 5000, "cc"]
    axes[1].hist(cc_tipico, bins=12, color="#2ca02c", alpha=0.85)
    axes[1].set_xlim(1200, 2700)
    tope = axes[1].get_ylim()[1]
    axes[1].text(2050, tope * 0.82, "↑ 1 fila en cc = 16.000\n(fuera de escala)",
                 fontsize=9, color="#d62728")
    axes[1].set_title("Cilindrada (cc): todo ≤ 2000 salvo 1 fila")
    axes[1].set_xlabel("Cilindrada (cc)")
    axes[1].set_ylabel("Cantidad de autos")

    fig.suptitle("Dos defectos con lupa: KM sospechosos y cc imposible", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_wrangling_validacion(out: Path) -> Path:
    """Precio medio por motor extraído con regex + validación texto vs columna."""
    _need_deps()
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    m = df["Model"].str.lstrip("?")
    motor = m.str.extract(r"(\d\.\d)")[0]
    precio = df.assign(motor=motor).groupby("motor")["Price"].mean().sort_index()
    n_motor = df.assign(motor=motor).groupby("motor").size()
    acuerdo_cc = float(((motor.astype(float) * 1000).round(0) == df["cc"]).mean() * 100)
    puertas = pd.Series(np.select(
        [m.str.contains("2/3-Doors", regex=False),
         m.str.contains("4/5-Doors", regex=False),
         m.str.contains("5DR", regex=False)],
        [3, 5, 5], default=np.nan), index=df.index)
    acuerdo_doors = float((puertas == df["Doors"])[puertas.notna()].mean() * 100)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=precio.index.tolist(), y=precio.values.tolist(), ax=axes[0],
                color="#0b5cad")
    axes[0].set_title("Premio del wrangling: precio medio por motor extraído")
    axes[0].set_xlabel("Motor extraído del texto (litros)")
    axes[0].set_ylabel("Precio medio (€)")
    for i, (v, n) in enumerate(zip(precio.values, n_motor.values)):
        axes[0].text(i, v + 200, f"{v:,.0f}€\n(n={n})".replace(",", "."),
                     ha="center", fontsize=8)

    sns.barplot(x=["Motor vs cc", "Puertas vs Doors"],
                y=[acuerdo_cc, acuerdo_doors], ax=axes[1], color="#2ca02c")
    axes[1].set_title("Validación: ¿el texto dice lo mismo que la columna?")
    axes[1].set_xlabel("Comparación")
    axes[1].set_ylabel("% de acuerdo")
    axes[1].set_ylim(0, 100)
    for i, v in enumerate([acuerdo_cc, acuerdo_doors]):
        axes[1].text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=10)

    fig.suptitle("Regex sobre Model: columnas nuevas que sí sirven (y se validan)", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out



def fig_u2_eda_tramos_corr(out: Path) -> Path:
    """Precio medio por tramo de edad + correlaciones top con Price."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    tramos = pd.cut(df["Age_08_04"], [0, 30, 60, 81],
                    labels=["joven ≤30m", "medio 31–60m", "viejo 61+m"])
    med = df.assign(tramo=tramos).groupby("tramo", observed=True)["Price"].mean()
    cnt = df.assign(tramo=tramos).groupby("tramo", observed=True).size()
    corr = df.select_dtypes("number").corr(numeric_only=True)["Price"].drop("Price")
    top = corr.reindex(["Mfg_Year", "Age_08_04", "Id", "Boardcomputer",
                        "Automatic_airco", "Weight", "KM", "CD_Player"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=med.index.tolist(), y=med.values.tolist(), ax=axes[0],
                color="#0b5cad")
    axes[0].set_title("groupby: precio medio por tramo de edad")
    axes[0].set_xlabel("Antigüedad del auto")
    axes[0].set_ylabel("Precio medio (€)")
    for i, (v, n) in enumerate(zip(med.values, cnt.values)):
        axes[0].text(i, v + 250, f"{v:,.0f}€\n(n={n})".replace(",", "."),
                     ha="center", fontsize=8)

    colores = ["#d62728" if c == "Id" else "#2ca02c" for c in top.index]
    axes[1].barh(top.index.tolist()[::-1], top.values.tolist()[::-1], color=colores[::-1])
    axes[1].axvline(0, color="#333333", linewidth=1)
    axes[1].set_title("corr(): qué se mueve junto al precio (Id = trampa)")
    axes[1].set_xlabel("Correlación con Price")
    for i, (c, v) in enumerate(zip(top.index.tolist()[::-1], top.values.tolist()[::-1])):
        axes[1].text(v + (0.03 if v >= 0 else -0.03), i, f"{v:.2f}",
                     va="center", ha="left" if v >= 0 else "right", fontsize=8)

    fig.suptitle("EDA en dos paneles: agrupar revela, correlacionar sugiere (y a veces miente)",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_outliers_iqr_z(out: Path) -> Path:
    """Boxplot de Price con vallas IQR + histograma con umbrales IQR y z."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    x = df["Price"]
    q1, q3 = x.quantile(0.25), x.quantile(0.75)
    iqr = q3 - q1
    lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
    m_iqr = (x < lo) | (x > hi)
    z = (x - x.mean()) / x.std()
    m_z = z.abs() > 3
    umbral_z = x.mean() + 3 * x.std()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.boxplot(y=x, ax=axes[0], color="skyblue")
    axes[0].axhline(hi, color="#d62728", linestyle="--", linewidth=1.5)
    axes[0].text(0.05, hi + 300, f"valla alta: {hi:,.0f} €".replace(",", "."),
                 fontsize=9, color="#d62728")
    axes[0].set_title(f"Boxplot de Price: {int(m_iqr.sum())} outliers IQR (puntos)")
    axes[0].set_ylabel("Precio (€)")

    axes[1].hist(x, bins=40, color="#0b5cad", alpha=0.8)
    axes[1].axvline(hi, color="#d62728", linestyle="--", linewidth=1.8,
                    label=f"IQR > {hi:,.0f}: {int(m_iqr.sum())} autos".replace(",", "."))
    axes[1].axvline(umbral_z, color="#ff7f0e", linestyle="-", linewidth=1.8,
                    label=f"z > 3 (>{umbral_z:,.0f}): {int(m_z.sum())} autos".replace(",", "."))
    axes[1].set_title("Histograma: z es más estricto que IQR (26 ⊂ 110)")
    axes[1].set_xlabel("Precio (€)")
    axes[1].set_ylabel("Cantidad de autos")
    axes[1].legend(fontsize=9)

    fig.suptitle("Dos reglas estadísticas: IQR caza 110, z-score solo 26", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_outliers_multi(out: Path) -> Path:
    """Scatter KM-Price con outliers Isolation Forest + conteo por método."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.neighbors import LocalOutlierFactor
    from sklearn.cluster import DBSCAN
    from sklearn.ensemble import IsolationForest
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(CSV)
    cols = ["KM", "Price", "Age_08_04"]
    X = StandardScaler().fit_transform(df[cols])
    lof = LocalOutlierFactor(n_neighbors=20).fit_predict(X) == -1
    db = DBSCAN(eps=0.35, min_samples=10).fit(X).labels_ == -1
    iso = IsolationForest(contamination=0.05, random_state=42).fit_predict(X) == -1

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(df.loc[~iso, "KM"], df.loc[~iso, "Price"], s=10, alpha=0.35,
                    color="#0b5cad", label=f"Normal ({int((~iso).sum())})")
    axes[0].scatter(df.loc[iso, "KM"], df.loc[iso, "Price"], s=28, alpha=0.9,
                    color="#d62728", label=f"Isolation Forest ({int(iso.sum())})")
    ejemplo = df[iso & lof].iloc[0]
    axes[0].annotate(f"fila {ejemplo.name}: {int(ejemplo['Age_08_04'])} meses,\n"
                     f"{int(ejemplo['KM'])} km, {int(ejemplo['Price'])} €",
                     xy=(ejemplo["KM"], ejemplo["Price"]), fontsize=8,
                     xytext=(40000, 26000), arrowprops=dict(arrowstyle="->", color="#333"))
    axes[0].set_title("Isolation Forest: 72 raros en KM+Price+Edad")
    axes[0].set_xlabel("Kilómetros (KM)")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=9)

    sns.barplot(x=["LOF (vecinos)", "DBSCAN (ruido)", "IForest (5%)"],
                y=[int(lof.sum()), int(db.sum()), int(iso.sum())], ax=axes[1],
                color="#2ca02c")
    axes[1].set_title("Cada método sospecha de distinta cantidad")
    axes[1].set_xlabel("Método")
    axes[1].set_ylabel("Autos marcados")
    for i, v in enumerate([int(lof.sum()), int(db.sum()), int(iso.sum())]):
        axes[1].text(i, v + 2, str(v), ha="center", fontsize=10)

    fig.suptitle("Outliers multivariados: raros en combinación, normales por separado",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_catalogo(out: Path) -> Path:
    """Catálogo 2x2: barras, histograma, scatter y línea con Toyota."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    fig, axes = plt.subplots(2, 2, figsize=(12, 7))

    vc = df["Fuel_Type"].value_counts()
    sns.barplot(x=vc.index.tolist(), y=vc.values.tolist(), ax=axes[0, 0],
                color="#0b5cad")
    axes[0, 0].set_title("Nominal → barras (conteo Fuel_Type)")
    axes[0, 0].set_xlabel("Combustible")
    axes[0, 0].set_ylabel("Autos")
    for i, v in enumerate(vc.values):
        axes[0, 0].text(i, v + 15, str(v), ha="center", fontsize=9)

    axes[0, 1].hist(df["Price"], bins=30, color="#2ca02c", alpha=0.85)
    axes[0, 1].axvline(df["Price"].median(), color="#333333", linestyle="--",
                       label=f"Mediana {df['Price'].median():,.0f} €".replace(",", "."))
    axes[0, 1].set_title("Continua → histograma (Price)")
    axes[0, 1].set_xlabel("Precio (€)")
    axes[0, 1].set_ylabel("Autos")
    axes[0, 1].legend(fontsize=9)

    s = df.sample(n=600, random_state=42)
    axes[1, 0].scatter(s["KM"], s["Price"], s=12, alpha=0.45, color="#0b5cad")
    axes[1, 0].set_title("2 continuas → scatter (KM vs Price, n=600)")
    axes[1, 0].set_xlabel("Kilómetros (KM)")
    axes[1, 0].set_ylabel("Precio (€)")

    evo = df.groupby("Mfg_Year")["Price"].mean()
    axes[1, 1].plot(evo.index.tolist(), evo.values.tolist(), marker="o",
                    color="#ff7f0e", linewidth=2)
    axes[1, 1].set_title("Ordenada → línea (precio medio por año fab.)")
    axes[1, 1].set_xlabel("Año de fabricación")
    axes[1, 1].set_ylabel("Precio medio (€)")

    fig.suptitle("El tipo de dato elige el gráfico (no al revés)", fontsize=12)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_color(out: Path) -> Path:
    """3 paletas con criterio: categórica, secuencial y divergente."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))

    s = df.sample(n=600, random_state=42)
    sns.scatterplot(data=s, x="KM", y="Price", hue="Fuel_Type", ax=axes[0],
                    palette="Set2", s=14, alpha=0.7)
    axes[0].set_title("Categórica: color = etiqueta")
    axes[0].set_xlabel("Kilómetros (KM)")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=8, title="Fuel", title_fontsize=8)

    tramos = pd.cut(df["Age_08_04"], [0, 30, 60, 81],
                    labels=["joven", "medio", "viejo"])
    piv = df.assign(t=tramos).groupby(["t", "Fuel_Type"], observed=True)["Price"].mean()
    piv = piv.unstack().reindex(["joven", "medio", "viejo"]).reindex(
        columns=["Petrol", "Diesel", "CNG"])
    sns.heatmap(piv, annot=True, fmt=".0f", cmap="YlGnBu", ax=axes[1],
                cbar_kws={"label": "Precio medio (€)"})
    axes[1].set_title("Secuencial: oscuro = más caro")
    axes[1].set_xlabel("Combustible")
    axes[1].set_ylabel("Tramo de edad")

    corr = df.select_dtypes("number").corr(numeric_only=True)["Price"].drop("Price")
    top = corr.reindex(["Mfg_Year", "Boardcomputer", "Weight", "KM", "Id",
                        "Age_08_04"]).dropna()
    colores = ["#2166ac" if v >= 0 else "#b2182b" for v in top.values]
    axes[2].barh(top.index.tolist()[::-1], top.values.tolist()[::-1],
                 color=colores[::-1])
    axes[2].axvline(0, color="#333333", linewidth=1)
    axes[2].set_title("Divergente: azul +, rojo −")
    axes[2].set_xlabel("Correlación con Price")

    fig.suptitle("Color con criterio: distinguir, ordenar, comparar contra cero",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_eje_truncado(out: Path) -> Path:
    """Mismas barras de precio medio: eje honesto vs truncado."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    med = df.groupby("Fuel_Type")["Price"].mean().reindex(["CNG", "Petrol", "Diesel"])

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=med.index.tolist(), y=med.values.tolist(), ax=axes[0],
                color="#2ca02c")
    axes[0].set_ylim(0, 13000)
    axes[0].set_title("Honesto: eje en 0 (Diesel +20% que CNG)")
    axes[0].set_xlabel("Combustible")
    axes[0].set_ylabel("Precio medio (€)")
    for i, v in enumerate(med.values):
        axes[0].text(i, v + 200, f"{v:,.0f}".replace(",", "."), ha="center",
                     fontsize=9)

    sns.barplot(x=med.index.tolist(), y=med.values.tolist(), ax=axes[1],
                color="#d62728")
    axes[1].set_ylim(9000, 12000)
    axes[1].set_title("Truncado: eje en 9000 (¡parece ×5, es la misma data!)")
    axes[1].set_xlabel("Combustible")
    axes[1].set_ylabel("Precio medio (€)")
    axes[1].tick_params(axis="x", rotation=0)

    fig.suptitle("El mismo promedio, dos historias: el eje truncado exagera",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_multivariado(out: Path) -> Path:
    """Burbujas KM-Price-Fuel-Edad + heatmap de correlaciones."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))

    s = df.sample(n=500, random_state=42)
    sns.scatterplot(data=s, x="KM", y="Price", hue="Fuel_Type", size="Age_08_04",
                    palette="Set2", sizes=(8, 110), alpha=0.65, ax=axes[0])
    axes[0].set_title("Burbujas: KM + Price + Fuel + Edad")
    axes[0].set_xlabel("Kilómetros (KM)")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=7, title="Fuel / Edad", title_fontsize=8)

    cols = ["Price", "KM", "Age_08_04", "Mfg_Year", "Weight", "HP"]
    sns.heatmap(df[cols].corr(numeric_only=True), annot=True, fmt=".2f",
                cmap="coolwarm", center=0, ax=axes[1],
                cbar_kws={"label": "Correlación"})
    axes[1].set_title("Heatmap: todas contra todas (Age↔Year −0,98)")

    fig.suptitle("Multivariado: más variables por gráfico, más historia por pixel",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_red_arbol(out: Path) -> Path:
    """Red de co-ocurrencia de equipamiento + árbol stump."""
    _need_deps()
    import itertools
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.tree import DecisionTreeClassifier, plot_tree

    df = pd.read_csv(CSV)
    cols = ["ABS", "Airco", "CD_Player", "Central_Lock", "Powered_Windows",
            "Boardcomputer", "Automatic_airco", "Radio"]
    soporte = df[cols].mean() * 100
    pares = [((df[a] & df[b]).mean() * 100, a, b)
             for a, b in itertools.combinations(cols, 2)]
    fuertes = [(v, a, b) for v, a, b in pares if v >= 40]

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    ax = axes[0]
    ang = {c: 2 * np.pi * i / len(cols) for i, c in enumerate(cols)}
    pos = {c: (np.cos(a), np.sin(a)) for c, a in ang.items()}
    for v, a, b in fuertes:
        xa, ya = pos[a]
        xb, yb = pos[b]
        ax.plot([xa, xb], [ya, yb], color="#0b5cad", alpha=0.55,
                linewidth=1 + v / 12)
        ax.text((xa + xb) / 2, (ya + yb) / 2, f"{v:.0f}%", fontsize=7,
                ha="center", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1))
    for c in cols:
        x, y = pos[c]
        ax.scatter([x], [y], s=soporte[c] * 9, color="#2ca02c", alpha=0.85,
                   edgecolors="#333333", zorder=3)
        ax.text(x * 1.18, y * 1.18, f"{c}\n{soporte[c]:.0f}%", fontsize=7,
                ha="center", va="center")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("Red: extras que vienen juntos (≥40%)")

    X = df[["KM", "Age_08_04", "HP"]]
    y = (df["Price"] > df["Price"].median()).astype(int)
    t = DecisionTreeClassifier(max_depth=2, random_state=42).fit(X, y)
    plot_tree(t, feature_names=["KM", "Edad", "HP"],
              class_names=["barato", "caro"], filled=True, ax=axes[1],
              fontsize=8, impurity=False)
    axes[1].set_title(f"Árbol (prof. 2): ¿caro? acierta {t.score(X, y):.1%}")

    fig.suptitle("Grafos y árboles: relaciones y reglas, dibujadas", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_texto(out: Path) -> Path:
    """Top palabras en Model + histograma de largo del texto."""
    _need_deps()
    from collections import Counter
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    c: Counter = Counter()
    for m in df["Model"].str.lstrip("?").str.split():
        c.update(t for t in m if t not in ("TOYOTA", "Corolla"))
    top = c.most_common(10)
    largo = df["Model"].str.lstrip("?").str.split().str.len()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=[v for _, v in top], y=[t for t, _ in top], ax=axes[0],
                color="#0b5cad")
    axes[0].set_title("Texto contado: top-10 palabras en Model")
    axes[0].set_xlabel("Apariciones (sin TOYOTA/Corolla)")
    for i, v in enumerate([v for _, v in top]):
        axes[0].text(v + 12, i, str(v), va="center", fontsize=8)

    axes[1].hist(largo, bins=range(1, 14), color="#2ca02c", alpha=0.85,
                 align="left")
    axes[1].axvline(largo.mean(), color="#333333", linestyle="--",
                    label=f"Media {largo.mean():.1f} palabras")
    axes[1].set_title("Largo del texto: 2–11 palabras por auto")
    axes[1].set_xlabel("Palabras por Model")
    axes[1].set_ylabel("Autos")
    axes[1].legend(fontsize=9)

    fig.suptitle("No estructurado → estructurado: el texto también se cuenta",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def _inyectar_faltantes(df):
    """Inyección documentada U4 (semilla 42): KM 10% MCAR, HP MAR por edad."""
    import numpy as np
    import pandas as pd
    rng = np.random.default_rng(42)
    n = len(df)
    m_km = rng.random(n) < 0.10
    tr = pd.cut(df["Age_08_04"], [0, 30, 60, 81],
                labels=["joven", "medio", "viejo"])
    p = tr.map({"joven": 0.05, "medio": 0.12, "viejo": 0.20}).to_numpy(dtype=float)
    m_hp = rng.random(n) < p
    return m_km, m_hp, tr


def fig_u4_mecanismos(out: Path) -> Path:
    """HP perdido por tramo (MAR) + filas útiles listwise vs pairwise."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    m_km, m_hp, tr = _inyectar_faltantes(df)
    por_tramo = pd.Series(m_hp).groupby(tr, observed=True).mean() * 100
    n_list = int((~(m_km | m_hp)).sum())
    n_km, n_hp = int((~m_km).sum()), int((~m_hp).sum())

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=por_tramo.index.tolist(), y=por_tramo.values.tolist(),
                ax=axes[0], color="#d62728")
    axes[0].set_title("MAR: HP se pierde más en viejos")
    axes[0].set_xlabel("Tramo de edad")
    axes[0].set_ylabel("% HP perdido (inyectado)")
    for i, v in enumerate(por_tramo.values):
        axes[0].text(i, v + 0.3, f"{v:.1f}%", ha="center", fontsize=10)

    sns.barplot(x=["Listwise\n(ambas)", "Pairwise\n(solo KM)", "Pairwise\n(solo HP)"],
                y=[n_list, n_km, n_hp], ax=axes[1], color="#0b5cad")
    axes[1].set_title("Filas útiles: listwise pierde 327")
    axes[1].set_xlabel("Estrategia")
    axes[1].set_ylabel("Filas aprovechables (de 1436)")
    for i, v in enumerate([n_list, n_km, n_hp]):
        axes[1].text(i, v + 12, str(v), ha="center", fontsize=10)

    fig.suptitle("Faltantes inyectados (semilla 42): el mecanismo importa",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u4_simple(out: Path) -> Path:
    """Histograma KM con pico en la media + corrección por reponderación."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    m_km, m_hp, tr = _inyectar_faltantes(df)
    km_imp = df["KM"].astype(float).copy()
    km_imp[m_km] = df.loc[~m_km, "KM"].mean()
    resp = 1 - pd.Series(m_hp).groupby(tr, observed=True).mean()
    w = 1.0 / tr.map(resp).to_numpy(dtype=float)
    sub = df.loc[~m_hp, "Price"].to_numpy(dtype=float)
    pond = float((sub * w[~m_hp]).sum() / w[~m_hp].sum())

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].hist(df["KM"], bins=40, color="#0b5cad", alpha=0.6, label="Real")
    axes[0].hist(km_imp, bins=40, color="#d62728", alpha=0.5,
                 label="Con media (pico)")
    axes[0].axvline(float(km_imp.mean()), color="#d62728", linestyle="--")
    axes[0].set_title("Rellenar con la media: pico falso en 68.567")
    axes[0].set_xlabel("KM")
    axes[0].set_ylabel("Autos")
    axes[0].legend(fontsize=9)

    real = float(df["Price"].mean())
    sesgos = [0.0, float(sub.mean()) - real, pond - real]
    sns.barplot(x=["Real (ref.)", "Solo HP-ok", "Ponderado"],
                y=sesgos, ax=axes[1], color="#2ca02c")
    axes[1].axhline(0, color="#333333", linewidth=1)
    axes[1].set_title("Sesgo: +205 € se corrige a −1 €")
    axes[1].set_xlabel("Estimación de la media de Price")
    axes[1].set_ylabel("Sesgo vs media real (€)")
    for i, v in enumerate(sesgos):
        axes[1].text(i, v + (8 if v >= 0 else -18), f"{v:+,.0f} €".replace(",", "."),
                     ha="center", fontsize=10)

    fig.suptitle("Relleno simple aplana; reponderar corrige sin rellenar",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u4_donantes(out: Path) -> Path:
    """Histograma HP real vs KNN + barras RMSE por método."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.impute import KNNImputer

    df = pd.read_csv(CSV)
    m_km, m_hp, tr = _inyectar_faltantes(df)
    cols = ["KM", "HP", "Age_08_04", "Weight", "Price"]
    X = df[cols].astype(float).copy()
    X.loc[m_km, "KM"] = np.nan
    X.loc[m_hp, "HP"] = np.nan
    mu = X.mean(skipna=True)
    sd = X.std(skipna=True)
    with warnings.catch_warnings():
        # Warning interno benigno de nan_euclidean (17 filas pierden KM y HP);
        # la salida se verifica sin NaN.
        warnings.simplefilter("ignore", RuntimeWarning)
        imp = KNNImputer(n_neighbors=5).fit_transform((X - mu) / sd)
    assert not np.isnan(imp).any()
    hp_knn = df["HP"].astype(float).copy()
    hp_knn[m_hp] = imp[:, 1] * sd["HP"] + mu["HP"]

    tru = df.loc[m_hp, "HP"].to_numpy(dtype=float)
    rmse_media = float((((tru - df.loc[~m_hp, "HP"].mean()) ** 2).mean()) ** 0.5)
    rd = np.random.default_rng(7)
    hd = np.array([rd.choice(df.loc[~m_hp & (tr == t), "HP"].to_numpy())
                   for t in tr[m_hp]])
    rmse_hd = float((((tru - hd) ** 2).mean()) ** 0.5)
    rmse_knn = float((((tru - hp_knn[m_hp].to_numpy()) ** 2).mean()) ** 0.5)
    motor = df["Model"].str.lstrip("?").str.extract(r"(\d\.\d)")[0]
    tabla = df.loc[~m_hp].groupby(motor)["HP"].median()
    cd = motor[m_hp].map(tabla).fillna(df.loc[~m_hp, "HP"].median()
                                       ).to_numpy(dtype=float)
    rmse_cd = float((((tru - cd) ** 2).mean()) ** 0.5)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].hist(df["HP"], bins=range(60, 200, 5), color="#0b5cad", alpha=0.6,
                 label="Real")
    axes[0].hist(hp_knn, bins=range(60, 200, 5), color="#2ca02c", alpha=0.5,
                 label="Con KNN (conserva forma)")
    axes[0].set_title("KNN rellena sin pico falso")
    axes[0].set_xlabel("HP")
    axes[0].set_ylabel("Autos")
    axes[0].legend(fontsize=9)

    metodos = ["Media", "Hot deck", "KNN-5", "Cold deck"]
    rmses = [rmse_media, rmse_hd, rmse_knn, rmse_cd]
    sns.barplot(x=metodos, y=rmses, ax=axes[1], color="#ff7f0e")
    axes[1].set_title("RMSE vs verdad tapada (HP)")
    axes[1].set_xlabel("Método")
    axes[1].set_ylabel("RMSE (HP)")
    for i, v in enumerate(rmses):
        axes[1].text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=10)

    fig.suptitle("Donantes y vecinos: copiar realidades, no promedios", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u4_modelos(out: Path) -> Path:
    """HP real vs imputado iterativo + ranking RMSE U4."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.impute import KNNImputer
    from sklearn.experimental import enable_iterative_imputer  # noqa: F401
    from sklearn.impute import IterativeImputer

    df = pd.read_csv(CSV)
    m_km, m_hp, tr = _inyectar_faltantes(df)
    cols = ["KM", "HP", "Age_08_04", "Weight", "Price"]
    X = df[cols].astype(float).copy()
    X.loc[m_km, "KM"] = np.nan
    X.loc[m_hp, "HP"] = np.nan
    imp = IterativeImputer(random_state=42).fit_transform(X)
    tru = df.loc[m_hp, "HP"].to_numpy(dtype=float)
    hat = imp[m_hp, 1]
    rmse_iter = float((((tru - hat) ** 2).mean()) ** 0.5)
    rmse_media = float((((tru - df.loc[~m_hp, "HP"].mean()) ** 2).mean()) ** 0.5)
    rd = np.random.default_rng(7)
    hd = np.array([rd.choice(df.loc[~m_hp & (tr == t), "HP"].to_numpy())
                   for t in tr[m_hp]])
    rmse_hd = float((((tru - hd) ** 2).mean()) ** 0.5)
    mu, sd = X.mean(skipna=True), X.std(skipna=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)
        kimp = KNNImputer(n_neighbors=5).fit_transform((X - mu) / sd)
    rmse_knn = float((((tru - (kimp[m_hp, 1] * sd["HP"] + mu["HP"])) ** 2
                       ).mean()) ** 0.5)
    motor = df["Model"].str.lstrip("?").str.extract(r"(\d\.\d)")[0]
    tabla = df.loc[~m_hp].groupby(motor)["HP"].median()
    cd = motor[m_hp].map(tabla).fillna(df.loc[~m_hp, "HP"].median()
                                       ).to_numpy(dtype=float)
    rmse_cd = float((((tru - cd) ** 2).mean()) ** 0.5)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(tru, hat, s=14, alpha=0.5, color="#0b5cad")
    lo, hi = float(tru.min()), float(tru.max())
    axes[0].plot([lo, hi], [lo, hi], color="#d62728", linestyle="--",
                 label="Ideal (y = x)")
    axes[0].set_title(f"Iterativo: real vs imputado (RMSE {rmse_iter:.1f})")
    axes[0].set_xlabel("HP real (tapado)")
    axes[0].set_ylabel("HP imputado")
    axes[0].legend(fontsize=9)

    mets = ["Cold deck", "KNN-5", "Iterativo", "Media", "Hot deck"]
    rms = [rmse_cd, rmse_knn, rmse_iter, rmse_media, rmse_hd]
    sns.barplot(x=mets, y=rms, ax=axes[1], color="#2ca02c")
    axes[1].set_title("Veredicto U4: ranking RMSE en HP")
    axes[1].set_xlabel("Método")
    axes[1].set_ylabel("RMSE (HP)")
    for i, v in enumerate(rms):
        axes[1].text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=10)

    fig.suptitle("Modelos imputan; la verdad tapada decide", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u5_porque(out: Path) -> Path:
    """Train/CV con y sin ruido + inestabilidad por casi-duplicada."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import KFold

    df = pd.read_csv(CSV)
    sub = df.sample(n=80, random_state=1)
    y = sub["Price"].to_numpy()
    rng = np.random.default_rng(0)
    Xb = sub[["KM", "Age_08_04", "HP", "Weight"]].to_numpy()
    Xn = np.column_stack([Xb, rng.normal(size=(80, 15))])
    Xc = np.column_stack(
        [Xb, sub["Age_08_04"].to_numpy() + rng.normal(scale=0.05, size=80)])
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        res = {}
        for nomb, X in [("base", Xb), ("ruido", Xn)]:
            tr = LinearRegression().fit(X, y).score(X, y)
            cv = np.mean([LinearRegression().fit(X[a], y[a]).score(X[b], y[b])
                          for a, b in kf.split(X)])
            res[nomb] = (tr, cv)
        sb = np.array([LinearRegression().fit(Xb[a], y[a]).coef_[1]
                       for a, b in kf.split(Xb)]).std()
        sc = np.array([LinearRegression().fit(Xc[a], y[a]).coef_[1]
                       for a, b in kf.split(Xc)]).std()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    xs = np.arange(2)
    axes[0].bar(xs - 0.2, [res["base"][0], res["ruido"][0]], width=0.4,
                color="#0b5cad", label="Train (n=80)")
    axes[0].bar(xs + 0.2, [res["base"][1], res["ruido"][1]], width=0.4,
                color="#2ca02c", label="CV-5")
    axes[0].set_xticks([0, 1])
    axes[0].set_xticklabels(["4 útiles", "4 útiles + 15 ruidos"])
    axes[0].set_title("Basura: train sube, CV baja")
    axes[0].set_ylabel("R²")
    axes[0].set_ylim(0.6, 1.0)
    axes[0].legend(fontsize=9)
    for i, (t, c) in enumerate([(res["base"][0], res["base"][1]),
                                (res["ruido"][0], res["ruido"][1])]):
        axes[0].text(i - 0.2, t + 0.005, f"{t:.3f}", ha="center", fontsize=8)
        axes[0].text(i + 0.2, c + 0.005, f"{c:.3f}", ha="center", fontsize=8)

    axes[1].bar(["sin dup", "con casi-dup"], [sb, sc], color="#d62728")
    axes[1].set_yscale("log")
    axes[1].set_title("Duplicada: coef Edad lotería (×900)")
    axes[1].set_ylabel("Desvío del coef entre folds (log)")
    for i, v in enumerate([sb, sc]):
        axes[1].text(i, v * 1.4, f"{v:,.1f}".replace(",", "."), ha="center",
                     fontsize=10)

    fig.suptitle("Por qué seleccionar: basura sobreajusta, duplicadas loterizan",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u5_subset(out: Path) -> Path:
    """AIC/BIC vs k + CV-R2 vs k con codo en 4."""
    _need_deps()
    import itertools
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import statsmodels.api as sm
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import KFold, cross_val_score

    df = pd.read_csv(CSV)
    pool = ["KM", "Age_08_04", "HP", "Weight", "cc", "Quarterly_Tax",
            "Mfg_Year", "Guarantee_Period"]
    y = df["Price"].to_numpy()
    kf = KFold(n_splits=5, shuffle=True, random_state=42)
    ks, aics, bics, cvs = [], [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k in range(1, 9):
            best = None
            for combo in itertools.combinations(pool, k):
                m = sm.OLS(y, sm.add_constant(df[list(combo)])).fit()
                if best is None or m.aic < best[0]:
                    best = (m.aic, m.bic, combo)
            aic, bic, combo = best
            cv = cross_val_score(LinearRegression(),
                                 df[list(combo)].to_numpy(), y, cv=kf,
                                 scoring="r2").mean()
            ks.append(k)
            aics.append(aic)
            bics.append(bic)
            cvs.append(cv)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].plot(ks, aics, marker="o", label="AIC (min k=7)", color="#0b5cad")
    axes[0].plot(ks, bics, marker="s", label="BIC (min k=5)", color="#ff7f0e")
    axes[0].set_title("AIC/BIC: menos es mejor (castigan k)")
    axes[0].set_xlabel("Cantidad de variables (k)")
    axes[0].set_ylabel("Criterio")
    axes[0].set_xticks(ks)
    axes[0].legend(fontsize=9)

    axes[1].plot(ks, cvs, marker="o", color="#2ca02c", linewidth=2)
    axes[1].axvline(4, color="#333333", linestyle=":", linewidth=1.5)
    axes[1].text(4.05, 0.82, "codo k=4\n(CV 0,867)", fontsize=9)
    axes[1].annotate("k=8: un fold\nse desploma", xy=(8, cvs[-1]), fontsize=8,
                     xytext=(6.4, 0.81),
                     arrowprops=dict(arrowstyle="->", color="#333"))
    axes[1].set_title("CV-R²: de k=4 en más, ameseta")
    axes[1].set_xlabel("Cantidad de variables (k)")
    axes[1].set_ylabel("R² en CV-5")
    axes[1].set_xticks(ks)
    axes[1].set_ylim(0.75, 0.89)

    fig.suptitle("Best subset (256 modelos): 4 variables casi bastan", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u5_caminos(out: Path) -> Path:
    """Caminos Lasso (mueren) y Ridge (achican) + selección n=80."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import Lasso, LassoCV, Ridge
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(CSV)
    pool = ["KM", "Age_08_04", "HP", "Weight", "cc", "Quarterly_Tax",
            "Mfg_Year", "Guarantee_Period"]
    Xs = StandardScaler().fit_transform(df[pool].to_numpy(dtype=float))
    y = df["Price"].to_numpy()
    alphas = np.logspace(4, -1, 60)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        cl = np.array([Lasso(alpha=a, max_iter=5000).fit(Xs, y).coef_
                       for a in alphas])
        cr = np.array([Ridge(alpha=a).fit(Xs, y).coef_ for a in alphas])
        sub = df.sample(n=80, random_state=1)
        rng = np.random.default_rng(0)
        Xn = np.column_stack(
            [sub[pool].to_numpy(dtype=float), rng.normal(size=(80, 6))])
        Xsn = StandardScaler().fit_transform(Xn)
        lz = LassoCV(cv=5, random_state=42, n_alphas=100
                     ).fit(Xsn, sub["Price"].to_numpy())
        vivos = (np.abs(lz.coef_) > 1e-9).astype(int)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for j, c in enumerate(pool):
        axes[0].plot(alphas, cl[:, j], label=c, linewidth=1.6)
    axes[0].set_xscale("log")
    axes[0].invert_xaxis()
    axes[0].set_title("Lasso: al subir α, mueren (→0)")
    axes[0].set_xlabel("α (izq = más castigo)")
    axes[0].set_ylabel("Coeficiente")
    axes[0].legend(fontsize=7, loc="upper left")

    for j, c in enumerate(pool):
        axes[1].plot(alphas, cr[:, j], label=c, linewidth=1.6)
    axes[1].set_xscale("log")
    axes[1].invert_xaxis()
    axes[1].set_title("Ridge: achica sin matar (nunca 0)")
    axes[1].set_xlabel("α (izq = más castigo)")
    axes[1].legend(fontsize=7, loc="upper left")

    nomb = pool + ["R1", "R2", "R3", "R4", "R5", "R6"]
    colores = ["#2ca02c" if v else "#d3d3d3" for v in vivos]
    axes[2].barh(nomb[::-1], vivos[::-1], color=colores[::-1])
    axes[2].set_title("Lasso n=80: 6/6 ruidos muertos")
    axes[2].set_xlabel("Vive (1) / muere (0)")
    axes[2].set_xlim(0, 1.3)
    for i, v in enumerate(vivos[::-1]):
        axes[2].text(v + 0.05, i, "vive" if v else "muere", va="center",
                     fontsize=8)

    fig.suptitle("Regularizar: Lasso elige, Ridge reparte", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u5_scad(out: Path) -> Path:
    """Ranking f_regression + curvas de penalización L1/L2/SCAD."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.feature_selection import SelectKBest, f_regression

    df = pd.read_csv(CSV)
    pool = ["KM", "Age_08_04", "HP", "Weight", "cc", "Quarterly_Tax",
            "Mfg_Year", "Guarantee_Period"]
    with warnings.catch_warnings():
        # Ruido numérico benigno del BLAS viejo (scores verificados sanos).
        warnings.simplefilter("ignore", RuntimeWarning)
        sk = SelectKBest(f_regression, k=8).fit(df[pool].to_numpy(dtype=float),
                                                df["Price"].to_numpy())
    assert np.isfinite(sk.scores_).all()
    orden = np.argsort(sk.scores_)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=sk.scores_[orden].tolist(),
                y=[pool[i] for i in orden], ax=axes[0], color="#0b5cad")
    axes[0].set_title("Filtro f_regression: Year y Age top-2")
    axes[0].set_xlabel("Score F (más = más asociada)")
    axes[0].set_xscale("log")

    b = np.linspace(0, 5, 200)
    lam, a_scad = 1.0, 3.7
    l1 = lam * b
    l2 = lam * b ** 2 / 2
    scad = np.where(b <= lam, lam * b,
                    np.where(b <= a_scad * lam,
                             (2 * a_scad * lam * b - b ** 2 - lam ** 2)
                             / (2 * (a_scad - 1)),
                             lam ** 2 * (a_scad + 1) / 2))
    axes[1].plot(b, l1, label="Lasso |β| (siempre castiga)", linewidth=2)
    axes[1].plot(b, l2, label="Ridge β² (castiga más)", linewidth=2)
    axes[1].plot(b, scad, label="SCAD (perdona grandes)", linewidth=2.5,
                 color="#2ca02c", linestyle="--")
    axes[1].set_title("Esquema: SCAD se aplana con β grande")
    axes[1].set_xlabel("|coeficiente|")
    axes[1].set_ylabel("Castigo")
    axes[1].legend(fontsize=9)

    fig.suptitle("Filtros rankean barato; SCAD perdona a los fuertes (esquema)",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_corr(out: Path) -> Path:
    """Scatter KM-Price por cuadrantes + barras r de 5 variables."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    s = df.sample(n=600, random_state=42)
    cx, cy = df["KM"].mean(), df["Price"].mean()
    pos = ((s["KM"] - cx) * (s["Price"] - cy)) >= 0

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(s.loc[pos, "KM"], s.loc[pos, "Price"], s=12, alpha=0.5,
                    color="#2166ac", label="Aporta + (I y III)")
    axes[0].scatter(s.loc[~pos, "KM"], s.loc[~pos, "Price"], s=12, alpha=0.5,
                    color="#b2182b", label="Aporta − (II y IV)")
    axes[0].axvline(cx, color="#333333", linewidth=1)
    axes[0].axhline(cy, color="#333333", linewidth=1)
    axes[0].set_title("Covarianza: gana el rojo (−77M €·km)")
    axes[0].set_xlabel("KM (línea = media)")
    axes[0].set_ylabel("Precio (línea = media)")
    axes[0].legend(fontsize=8)

    vars5 = ["Mfg_Year", "Weight", "HP", "KM", "Age_08_04"]
    rs = [df[c].corr(df["Price"]) for c in vars5]
    colores = ["#2166ac" if v >= 0 else "#b2182b" for v in rs]
    axes[1].barh(vars5[::-1], rs[::-1], color=colores[::-1])
    axes[1].axvline(0, color="#333333", linewidth=1)
    axes[1].set_title("Pearson r: misma escala −1…+1 (r²=R²)")
    axes[1].set_xlabel("Correlación con Price")
    for i, v in enumerate(rs[::-1]):
        axes[1].text(v + (0.03 if v >= 0 else -0.03), i, f"{v:.2f}",
                     va="center", ha="left" if v >= 0 else "right", fontsize=9)

    fig.suptitle("Covarianza (unidades locas) vs correlación (−1…+1)",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def _ols_referencia():
    """Réplica exacta Parte 2: 9 variables, OLS statsmodels."""
    import numpy as np
    import pandas as pd
    import statsmodels.api as sm
    df = pd.read_csv(CSV)
    cols_numericas = df.select_dtypes(include=[np.number]).columns
    df_limpio = df[cols_numericas].copy()
    columnas_basura = ["Id", "Met_Color", "Airbag_1", "Airbag_2", "Gears",
                        "Mistlamps", "Radio_cassette", "Power_Steering",
                        "Backseat_Divider", "Central_Lock", "Radio", "cc",
                        "Doors", "Cilynders", "CD_Player", "Airco", "Automatic",
                        "Tow_Bar", "Boardcomputer", "Metallic_Rim", "Mfg_Year",
                        "Mfr_Guarantee", "Cylinders", "ABS", "Sport_Model",
                        "Age_08_04"]
    df_limpio = df_limpio.drop(
        columns=[c for c in columnas_basura if c in df_limpio.columns])
    df_limpio = df_limpio.fillna(df_limpio.mean())
    y = df_limpio["Price"]
    X = df_limpio.drop(columns=["Price"])
    modelo = sm.OLS(y, sm.add_constant(X)).fit()
    return df, y, X, modelo


def fig_u6_multiple(out: Path) -> Path:
    """Coeficientes estandarizados + real vs predicho (R2 0,741)."""
    _need_deps()
    import numpy as np
    import matplotlib.pyplot as plt

    df, y, X, modelo = _ols_referencia()
    beta = modelo.params.drop("const") * X.std() / y.std()
    orden = np.argsort(beta.values)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    bs = beta.iloc[orden]
    colores = ["#b2182b" if v < 0 else "#2166ac" for v in bs.values]
    axes[0].barh(bs.index.tolist(), bs.values.tolist(), color=colores)
    axes[0].axvline(0, color="#333333", linewidth=1)
    axes[0].set_title("Pesos comparables (β estandarizados)")
    axes[0].set_xlabel("Efecto en desvíos de Price")
    axes[0].tick_params(axis="y", labelsize=8)

    pred = modelo.fittedvalues
    axes[1].scatter(y, pred, s=10, alpha=0.4, color="#0b5cad")
    lo, hi = float(y.min()), float(y.max())
    axes[1].plot([lo, hi], [lo, hi], color="#d62728", linestyle="--",
                 label=f"Ideal (R² = {modelo.rsquared:.3f})")
    axes[1].set_title("Real vs predicho: 0,741 (vs 0,325 simple)")
    axes[1].set_xlabel("Precio real (€)")
    axes[1].set_ylabel("Precio predicho (€)")
    axes[1].legend(fontsize=9)

    fig.suptitle("OLS múltiple (réplica Parte 2): 9 variables, 74 % explicado",
                 fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_diag1(out: Path) -> Path:
    """QQ-plot + residuos vs predichos del OLS múltiple."""
    _need_deps()
    import numpy as np
    import matplotlib.pyplot as plt
    import statsmodels.api as sm

    df, y, X, modelo = _ols_referencia()
    resid = modelo.resid
    pred = modelo.fittedvalues

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sm.graphics.qqplot(resid, line="45", ax=axes[0], ms=4, alpha=0.6)
    axes[0].set_title("QQ: casi recta (colas apenas pesadas)")
    axes[0].set_xlabel("Cuantiles teóricos normales")
    axes[0].set_ylabel("Residuos ordenados (€)")

    axes[1].scatter(pred, resid, s=10, alpha=0.4, color="#ff7f0e")
    axes[1].axhline(0, color="#333333", linestyle="--", linewidth=1.2)
    axes[1].set_title("Residuos vs predichos (nube en 0)")
    axes[1].set_xlabel("Precio predicho (€)")
    axes[1].set_ylabel("Residuo = real − predicho (€)")

    fig.suptitle("Diagnóstico 1: ¿parecen ruido sin patrón?", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_diag2(out: Path) -> Path:
    """Leverage vs residuos (Cook) + regresión parcial KM."""
    _need_deps()
    import numpy as np
    import matplotlib.pyplot as plt
    import statsmodels.api as sm

    df, y, X, modelo = _ols_referencia()
    Xc = sm.add_constant(X)
    inf = modelo.get_influence()
    cooks = inf.cooks_distance[0]
    lev = inf.hat_matrix_diag
    stu = inf.resid_studentized_external

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].scatter(lev, stu, s=np.sqrt(cooks) * 220, alpha=0.5,
                    color="#0b5cad")
    top = np.argsort(cooks)[-3:][::-1]
    for i in top:
        axes[0].annotate(f"fila {i}\nCook {cooks[i]:.2f}", fontsize=8,
                         xy=(lev[i], stu[i]), xytext=(8, 8),
                         textcoords="offset points",
                         arrowprops=dict(arrowstyle="->", color="#333"))
    axes[0].axhline(0, color="#333333", linewidth=1)
    axes[0].set_title("Leverage vs residuos (burbuja = Cook)")
    axes[0].set_xlabel("Leverage (cuánto tira)")
    axes[0].set_ylabel("Residuo studentizado")

    otras = [c for c in X.columns if c != "KM"]
    sm.graphics.plot_partregress(
        endog=y, exog_i=Xc["KM"], exog_others=Xc[otras], obs_labels=False,
        ax=axes[1])
    axes[1].set_title("Parcial KM: baja igual (−0,0456)")
    axes[1].set_xlabel("KM residualizado")
    axes[1].set_ylabel("Price residualizado")

    fig.suptitle("Diagnóstico 2: ¿quién deforma? ¿KM es genuino?", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_poli(out: Path) -> Path:
    """Curvas grado 1-2 en Edad + CV por grado Age/KM."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import KFold, cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import PolynomialFeatures, StandardScaler

    warnings.simplefilter("ignore", RuntimeWarning)
    df = pd.read_csv(CSV)
    y = df["Price"].to_numpy()
    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    s = df.sample(n=600, random_state=42)
    axes[0].scatter(s["Age_08_04"], s["Price"], s=10, alpha=0.35,
                    color="#0b5cad")
    xs = np.linspace(float(df["Age_08_04"].min()),
                     float(df["Age_08_04"].max()), 200).reshape(-1, 1)
    Xa = df[["Age_08_04"]].to_numpy(dtype=float)
    for d, c, est in [(1, "#d62728", "--"), (2, "#2ca02c", "-")]:
        m = make_pipeline(PolynomialFeatures(d, include_bias=False),
                          StandardScaler(), LinearRegression())
        m.fit(Xa, y)
        axes[0].plot(xs.ravel(), m.predict(xs), color=c, linestyle=est,
                     linewidth=2, label=f"Grado {d}")
    axes[0].set_title("Edad: la curva (d2) abraza la nube")
    axes[0].set_xlabel("Edad (meses)")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=9)

    cvs = {}
    for col in ["Age_08_04", "KM"]:
        Xc = df[[col]].to_numpy(dtype=float)
        cvs[col] = []
        for d in (1, 2, 3, 4):
            m = make_pipeline(PolynomialFeatures(d, include_bias=False),
                              StandardScaler(), LinearRegression())
            cvs[col].append(cross_val_score(m, Xc, y, cv=kf,
                                            scoring="r2").mean())
    xs4 = np.arange(1, 5)
    axes[1].bar(xs4 - 0.2, cvs["Age_08_04"], width=0.4, color="#2ca02c",
                label="Edad (codo d2)")
    axes[1].bar(xs4 + 0.2, cvs["KM"], width=0.4, color="#0b5cad",
                label="KM (sube lento)")
    axes[1].set_title("CV-R² por grado: Edad ameseta, KM trepa")
    axes[1].set_xlabel("Grado del polinomio")
    axes[1].set_ylabel("R² en CV-5")
    axes[1].set_xticks([1, 2, 3, 4])
    axes[1].set_ylim(0.25, 0.9)
    axes[1].legend(fontsize=9)

    warnings.simplefilter("default", RuntimeWarning)
    fig.suptitle("Polinomial: curvas donde aportan, grado por CV", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_mas(out: Path) -> Path:
    """OLS vs RLM en KM-Price + pendientes comparadas."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import statsmodels.api as sm
    from sklearn.linear_model import BayesianRidge
    from statsmodels.robust.robust_linear_model import RLM

    warnings.simplefilter("ignore", RuntimeWarning)
    df = pd.read_csv(CSV)
    Xs = sm.add_constant(df[["KM"]])
    y = df["Price"]
    ols = sm.OLS(y, Xs).fit()
    rlm = RLM(y, Xs).fit()
    br = BayesianRidge().fit(df[["KM"]].to_numpy(dtype=float),
                             y.to_numpy(dtype=float))
    se_bayes = float(np.sqrt(br.sigma_[0, 0]))
    warnings.simplefilter("default", RuntimeWarning)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    s = df.sample(n=600, random_state=42)
    axes[0].scatter(s["KM"], s["Price"], s=10, alpha=0.35, color="#0b5cad")
    grid = np.linspace(0, float(df["KM"].max()), 200)
    Xg = pd.DataFrame({"const": 1.0, "KM": grid})
    axes[0].plot(grid, ols.predict(Xg), color="#d62728", linewidth=2,
                 label=f"OLS ({ols.params['KM']:.4f})")
    axes[0].plot(grid, rlm.predict(Xg), color="#2ca02c", linewidth=2,
                 label=f"Robusta ({rlm.params['KM']:.4f})")
    axes[0].set_title("Robusta cede menos ante extremos")
    axes[0].set_xlabel("KM")
    axes[0].set_ylabel("Precio (€)")
    axes[0].legend(fontsize=9)

    mets = ["OLS", "Robusta", "Bayes"]
    vals = [ols.params["KM"], rlm.params["KM"], br.coef_[0]]
    errs = [0.0, 0.0, 1.96 * se_bayes]
    axes[1].bar(mets, vals, color=["#d62728", "#2ca02c", "#0b5cad"],
                yerr=errs, capsize=6, error_kw={"color": "#333333"})
    axes[1].axhline(0, color="#333333", linewidth=1)
    axes[1].set_title("Pendiente KM: tres regresiones")
    axes[1].set_ylabel("€ por km")
    for i, v in enumerate(vals):
        axes[1].text(i, v - 0.0015, f"{v:.4f}", ha="center", fontsize=9)

    fig.suptitle("Más allá de OLS: robusta pesa, Bayes intervala", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u7_dist(out: Path) -> Path:
    """Un desvío por variable + segmento distancia estandarizada."""
    _need_deps()
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV)
    cols = ["KM", "Price", "Age_08_04"]
    sds = df[cols].std()
    X = df[cols].to_numpy(dtype=float)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    d01 = float(np.sqrt(((Xs[0] - Xs[1]) ** 2).sum()))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    sns.barplot(x=sds.index.tolist(), y=sds.values.tolist(), ax=axes[0],
                color="#d62728")
    axes[0].set_yscale("log")
    axes[0].set_title("1 desvío: 37 mil km = 3,6 mil € = 19 meses")
    axes[0].set_xlabel("Variable (unidades crudas incomparables)")
    axes[0].set_ylabel("Un desvío estándar (log)")
    for i, v in enumerate(sds.values):
        axes[0].text(i, v * 1.3, f"{v:,.0f}".replace(",", "."), ha="center",
                     fontsize=10)

    s = df.sample(n=400, random_state=42)
    mus, sds2 = X.mean(axis=0), X.std(axis=0)
    axes[1].scatter((s["KM"] - mus[0]) / sds2[0],
                    (s["Price"] - mus[1]) / sds2[1],
                    s=10, alpha=0.35, color="#0b5cad")
    axes[1].plot([Xs[0, 0], Xs[1, 0]], [Xs[0, 1], Xs[1, 1]], color="#d62728",
                 linewidth=2.5)
    axes[1].scatter([Xs[0, 0], Xs[1, 0]], [Xs[0, 1], Xs[1, 1]], s=60,
                    color="#d62728", zorder=3)
    axes[1].annotate(f"filas 0–1\nd = {d01:.2f}", fontsize=9,
                     xy=((Xs[0, 0] + Xs[1, 0]) / 2,
                         (Xs[0, 1] + Xs[1, 1]) / 2),
                     xytext=(15, 15), textcoords="offset points",
                     arrowprops=dict(arrowstyle="->", color="#333"))
    axes[1].set_title("Estandarizado: cada variable vota")
    axes[1].set_xlabel("KM (desvíos)")
    axes[1].set_ylabel("Precio (desvíos)")

    fig.suptitle("Distancias: sin estandarizar, KM habla solo", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u7_kmeans(out: Path) -> Path:
    """Scatter KM-Price por cluster K-Means k=3 + centroides."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    df = pd.read_csv(CSV)
    cols = ["KM", "Price", "Age_08_04"]
    X = df[cols].to_numpy(dtype=float)
    mu, sd = X.mean(axis=0), X.std(axis=0)
    Xs = (X - mu) / sd
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        km = KMeans(n_clusters=3, n_init=10, random_state=42).fit(Xs)
    g = km.labels_
    cent = km.cluster_centers_ * sd + mu
    # Nombres por precio del centroide (etiquetas K-Means son arbitrarias).
    por_precio = np.argsort(cent[:, 1])
    nombres = {int(por_precio[0]): "veteranos",
               int(por_precio[1]): "medios", int(por_precio[2]): "nuevitos"}
    colores = {int(por_precio[0]): "#ff7f0e", int(por_precio[1]): "#0b5cad",
               int(por_precio[2]): "#2ca02c"}

    fig, ax = plt.subplots(figsize=(12, 4.6))
    for i in range(3):
        m = g == i
        ax.scatter(df.loc[m, "KM"], df.loc[m, "Price"], s=10, alpha=0.45,
                   color=colores[i],
                   label=f"{nombres[i]} (n={int(m.sum())})")
    ax.scatter(cent[:, 0], cent[:, 1], s=220, marker="X", color="#d62728",
               edgecolors="#333333", linewidths=1.2, zorder=3,
               label="Centroides")
    for i in range(3):
        ax.annotate(nombres[i], fontsize=10, fontweight="bold",
                    xy=(cent[i, 0], cent[i, 1]), xytext=(10, -12),
                    textcoords="offset points")
    ax.set_title("K-Means k=3: nuevitos, medios y veteranos")
    ax.set_xlabel("KM")
    ax.set_ylabel("Precio (€)")
    ax.legend(fontsize=9)

    fig.suptitle("Clustering: grupos que el negocio entiende", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u7_jer(out: Path) -> Path:
    """Dendrograma Ward + scatter DBSCAN con ruido."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from scipy.cluster.hierarchy import dendrogram, linkage
    from sklearn.cluster import DBSCAN

    df = pd.read_csv(CSV)
    X = df[["KM", "Price", "Age_08_04"]].to_numpy(dtype=float)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        Z = linkage(Xs, method="ward")
        db = DBSCAN(eps=0.35, min_samples=10).fit(Xs).labels_

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    corte3 = float((Z[-3, 2] + Z[-2, 2]) / 2)  # garantiza 3 grupos
    dendrogram(Z, truncate_mode="lastp", p=12, ax=axes[0],
               color_threshold=corte3)
    axes[0].axhline(corte3, color="#d62728", linestyle="--", linewidth=1.2)
    axes[0].set_title("Dendrograma Ward (corte → 3 grupos)")
    axes[0].set_xlabel("Autos (últimas 12 juntadas)")
    axes[0].set_ylabel("Distancia de juntada")

    cols3 = ["#0b5cad", "#ff7f0e", "#2ca02c"]
    for i, c in enumerate(sorted(set(db) - {-1})):
        m = db == c
        axes[1].scatter(df.loc[m, "KM"], df.loc[m, "Price"], s=10, alpha=0.45,
                        color=cols3[i % 3], label=f"Grupo {c} (n={int(m.sum())})")
    axes[1].scatter(df.loc[db == -1, "KM"], df.loc[db == -1, "Price"], s=14,
                    alpha=0.8, color="black", label="Ruido (167)")
    axes[1].set_title("DBSCAN: 3 grupos + ruido negro")
    axes[1].set_xlabel("KM")
    axes[1].set_ylabel("Precio (€)")
    axes[1].legend(fontsize=8)

    fig.suptitle("Jerárquico anida; DBSCAN densifica y marca ruido", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u7_val(out: Path) -> Path:
    """Codo de inercia + silueta por k (premia k=2)."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.cluster import KMeans
    from sklearn.metrics import silhouette_score

    df = pd.read_csv(CSV)
    X = df[["KM", "Price", "Age_08_04"]].to_numpy(dtype=float)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    ks = list(range(2, 9))
    iner, sil = [], []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for k in ks:
            m = KMeans(n_clusters=k, n_init=10, random_state=42).fit(Xs)
            iner.append(m.inertia_)
            sil.append(silhouette_score(Xs, m.labels_))

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    axes[0].plot(ks, iner, marker="o", color="#0b5cad", linewidth=2)
    axes[0].axvline(3, color="#333333", linestyle=":", linewidth=1.5)
    axes[0].text(3.1, 1200, "codo 3–4", fontsize=10)
    axes[0].set_title("Codo: inercia cae, frena en 3–4")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inercia (suma dist²)")
    axes[0].set_xticks(ks)

    cols = ["#2ca02c" if k == 2 else "#0b5cad" for k in ks]
    axes[1].bar([str(k) for k in ks], sil, color=cols)
    axes[1].set_title("Silueta: máxima en k=2 (0,49)")
    axes[1].set_xlabel("k")
    axes[1].set_ylabel("Silueta media (−1…+1)")
    for i, v in enumerate(sil):
        axes[1].text(i, v + 0.01, f"{v:.2f}", ha="center", fontsize=8)

    fig.suptitle("Validar: métricas guían, negocio decide (k=3)", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u7_pca(out: Path) -> Path:
    """Scree 8 vars + biplot PC1-PC2 con clusters."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA

    df = pd.read_csv(CSV)
    cols = ["KM", "Price", "Age_08_04", "HP", "Weight", "cc",
            "Quarterly_Tax", "Mfg_Year"]
    X = df[cols].to_numpy(dtype=float)
    Xs = (X - X.mean(axis=0)) / X.std(axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        p = PCA().fit(Xs)
        g = KMeans(n_clusters=3, n_init=10, random_state=42).fit(Xs).labels_
        Z = p.transform(Xs)
    vr = p.explained_variance_ratio_

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].bar(range(1, 9), vr, color="#0b5cad", alpha=0.85)
    axes[0].plot(range(1, 9), np.cumsum(vr), color="#d62728", marker="o",
                 label=f"Acumulada (2D = {vr[:2].sum():.0%})")
    axes[0].set_title("Scree: PC1 46 %, PC1+2 70 %")
    axes[0].set_xlabel("Componente")
    axes[0].set_ylabel("Varianza explicada")
    axes[0].set_xticks(range(1, 9))
    axes[0].legend(fontsize=9)

    colores = ["#0b5cad", "#ff7f0e", "#2ca02c"]
    for i in range(3):
        axes[1].scatter(Z[g == i, 0], Z[g == i, 1], s=10, alpha=0.45,
                        color=colores[i])
    esc = 6.0
    for j, c in enumerate(cols):
        axes[1].arrow(0, 0, p.components_[0, j] * esc,
                      p.components_[1, j] * esc, color="#d62728",
                      head_width=0.15, length_includes_head=True)
        axes[1].text(p.components_[0, j] * esc * 1.08,
                     p.components_[1, j] * esc * 1.08, c, fontsize=7,
                     color="#333333")
    axes[1].axhline(0, color="#999999", linewidth=0.8)
    axes[1].axvline(0, color="#999999", linewidth=0.8)
    axes[1].set_title("Biplot: nuevo↔viejo (PC1), clusters encima")
    axes[1].set_xlabel(f"PC1 ({vr[0]:.0%})")
    axes[1].set_ylabel(f"PC2 ({vr[1]:.0%})")

    fig.suptitle("PCA: 8 dimensiones resumidas en 2 (70 %)", fontsize=11)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u8_knn(out: Path) -> Path:
    """k-NN caro/barato: accuracy vs k con/sin escala + matriz de confusión."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score, cross_val_predict
    from sklearn.metrics import confusion_matrix

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    df = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    y = (df["Price"] > 9900).astype(int).values
    Xs = StandardScaler().fit_transform(df[cols].values)
    Xr = df[cols].values
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    ks = [1, 3, 5, 9, 15, 25, 51, 101]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        acc_s = [cross_val_score(KNeighborsClassifier(k), Xs, y, cv=cv).mean() for k in ks]
        acc_r = [cross_val_score(KNeighborsClassifier(k), Xr, y, cv=cv).mean() for k in ks]
        yp = cross_val_predict(KNeighborsClassifier(25), Xs, y, cv=cv)
    cm = confusion_matrix(y, yp)
    assert abs(max(acc_s) - 0.8698) < 0.005, acc_s
    assert cm.tolist() == [[656, 73], [114, 593]], cm.tolist()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(ks, acc_s, "o-", label="Estandarizado")
    axes[0].plot(ks, acc_r, "s--", label="Sin escalar")
    axes[0].axhline(0.5, color="gray", ls=":", label="Azar (50 %)")
    axes[0].annotate("k=25: 87,0 %", xy=(25, 0.8698), xytext=(45, 0.90),
                     arrowprops=dict(arrowstyle="->"), fontsize=10)
    axes[0].set_xscale("log")
    axes[0].set_xlabel("k (vecinos, escala log)")
    axes[0].set_ylabel("Accuracy (CV 5-fold)")
    axes[0].set_title("k-NN caro/barato: accuracy vs k")
    axes[0].set_ylim(0.45, 0.95)
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", ax=axes[1],
                xticklabels=["Pred. barato", "Pred. caro"],
                yticklabels=["Real barato", "Real caro"])
    axes[1].set_title("Matriz de confusión (k=25, CV)")
    axes[1].set_xlabel("Predicho")
    axes[1].set_ylabel("Real")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u8_log(out: Path) -> Path:
    """Logística caro/barato: curva ROC + barras de coeficientes."""
    _need_deps()
    import warnings
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import StandardScaler
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import StratifiedKFold, cross_val_predict
    from sklearn.metrics import roc_auc_score, roc_curve

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    df = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    X = StandardScaler().fit_transform(df[cols].values)
    y = (df["Price"] > 9900).astype(int).values
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        proba = cross_val_predict(LogisticRegression(max_iter=2000), X, y,
                                  cv=cv, method="predict_proba")[:, 1]
        m = LogisticRegression(max_iter=2000).fit(X, y)
    auc = roc_auc_score(y, proba)
    fpr, tpr, _ = roc_curve(y, proba)
    coefs = pd.Series(m.coef_[0], index=cols).sort_values()
    assert abs(auc - 0.9473) < 0.005, auc
    assert coefs.index[0] == "Age_08_04" and coefs.iloc[0] < -3.0, coefs.to_dict()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    axes[0].plot(fpr, tpr, label="Logística (AUC = %.3f)" % auc)
    axes[0].plot([0, 1], [0, 1], "k--", label="Azar (AUC = 0,5)")
    axes[0].set_xlabel("Tasa de falsas alarmas (FPR)")
    axes[0].set_ylabel("Tasa de aciertos (TPR)")
    axes[0].set_title("Curva ROC: caro vs barato")
    axes[0].legend(loc="lower right")
    axes[0].grid(True, alpha=0.3)
    colors = ["#dc2626" if v < 0 else "#16a34a" for v in coefs.values]
    axes[1].barh(coefs.index, coefs.values, color=colors)
    axes[1].axvline(0, color="black", linewidth=0.8)
    axes[1].set_xlabel("Coeficiente (variables estandarizadas)")
    axes[1].set_title("Qué empuja hacia 'caro' (+/-)")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u8_nbtree(out: Path) -> Path:
    """Árbol caro/barato: train vs CV por profundidad + árbol depth=2."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.naive_bayes import GaussianNB
    from sklearn.tree import DecisionTreeClassifier, plot_tree
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    df = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    X = df[cols].values
    y = (df["Price"] > 9900).astype(int).values
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        nb = cross_val_score(GaussianNB(), X, y, cv=cv).mean()
        depths = [1, 2, 3, 4, 5, 8, 12]
        tr, te = [], []
        for d in depths:
            tr.append(DecisionTreeClassifier(max_depth=d, random_state=42).fit(X, y).score(X, y))
            te.append(cross_val_score(DecisionTreeClassifier(max_depth=d, random_state=42),
                                      X, y, cv=cv).mean())
        tree2 = DecisionTreeClassifier(max_depth=2, random_state=42).fit(X, y)
    assert abs(nb - 0.8349) < 0.005, nb
    assert abs(max(te) - 0.8725) < 0.005 and depths[int(np.argmax(te))] == 5, te

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    axes[0].plot(depths, tr, "o-", label="Train (memoriza)")
    axes[0].plot(depths, te, "o-", label="CV 5-fold (generaliza)")
    axes[0].axhline(nb, color="gray", ls=":", label="Naive Bayes CV (0,835)")
    axes[0].annotate("d=5: CV 87,3 %", xy=(5, 0.8725), xytext=(7.5, 0.90),
                     arrowprops=dict(arrowstyle="->"), fontsize=10)
    axes[0].set_xlabel("Profundidad máxima")
    axes[0].set_ylabel("Accuracy")
    axes[0].set_title("Árbol: train vs CV por profundidad")
    axes[0].set_ylim(0.78, 1.0)
    axes[0].legend(fontsize=9)
    axes[0].grid(True, alpha=0.3)
    plot_tree(tree2, feature_names=cols, class_names=["barato", "caro"],
              filled=True, rounded=True, fontsize=8, ax=axes[1])
    axes[1].set_title("Árbol depth=2 (raíz: edad ≤ 57,5)")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u8_rf(out: Path) -> Path:
    """Ensambles caro/barato: barras CV NB/árbol/RF/HGB + importancias."""
    _need_deps()
    import warnings
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.naive_bayes import GaussianNB
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    df = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    X = df[cols].values
    y = (df["Price"] > 9900).astype(int).values
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    models = {
        "Naive Bayes": GaussianNB(),
        "Árbol d=5": DecisionTreeClassifier(max_depth=5, random_state=42),
        "RF n=10": RandomForestClassifier(10, random_state=42),
        "RF n=200": RandomForestClassifier(200, random_state=42),
        "Boosting (HGB)": HistGradientBoostingClassifier(random_state=42),
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        acc = {k: cross_val_score(m, X, y, cv=cv).mean() for k, m in models.items()}
        rf = RandomForestClassifier(200, random_state=42).fit(X, y)
    imp = pd.Series(rf.feature_importances_, index=cols).sort_values()
    assert abs(acc["Árbol d=5"] - 0.8725) < 0.005, acc
    assert abs(acc["RF n=200"] - 0.8656) < 0.005, acc
    assert imp.index[-1] == "Age_08_04" and imp.iloc[-1] > 0.5, imp.to_dict()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    names = list(acc.keys())
    vals = [acc[k] for k in names]
    bars = axes[0].bar(names, vals, color=["#94a3b8", "#16a34a", "#f59e0b", "#f59e0b", "#8b5cf6"])
    axes[0].axhline(0.5, color="gray", ls=":", label="Azar")
    for b, v in zip(bars, vals):
        axes[0].text(b.get_x() + b.get_width() / 2, v + 0.004, "%.1f %%" % (v * 100),
                     ha="center", fontsize=9)
    axes[0].set_ylabel("Accuracy (CV 5-fold)")
    axes[0].set_title("Ensambles vs simples: nadie rompe el 87 %")
    axes[0].set_ylim(0.45, 1.0)
    axes[0].tick_params(axis="x", rotation=15)
    axes[1].barh(imp.index, imp.values, color="#0ea5e9")
    axes[1].set_xlabel("Importancia (fracción de uso ponderado)")
    axes[1].set_title("RF: edad (52 %) + KM (31 %) mandan")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u8_svm(out: Path) -> Path:
    """SVM caro/barato: fronteras 2D lineal vs RBF + torneo de 7."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.preprocessing import StandardScaler
    from sklearn.svm import SVC
    from sklearn.naive_bayes import GaussianNB
    from sklearn.tree import DecisionTreeClassifier
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.model_selection import StratifiedKFold, cross_val_score

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    df = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    Xs = StandardScaler().fit_transform(df[cols].values)
    y = (df["Price"] > 9900).astype(int).values
    cv = StratifiedKFold(5, shuffle=True, random_state=42)
    Xn = df[cols].values
    models = {
        "Naive Bayes": (GaussianNB(), Xn),
        "Boosting": (HistGradientBoostingClassifier(random_state=42), Xn),
        "RF n=200": (RandomForestClassifier(200, random_state=42), Xn),
        "k-NN k=25": (KNeighborsClassifier(25), Xs),
        "Logística": (LogisticRegression(max_iter=2000), Xs),
        "Árbol d=5": (DecisionTreeClassifier(max_depth=5, random_state=42), Xn),
        "SVM RBF": (SVC(kernel="rbf", C=5.0), Xs),
    }
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        acc = {k: cross_val_score(m, X, y, cv=cv).mean() for k, (m, X) in models.items()}
    assert abs(acc["SVM RBF"] - 0.8767) < 0.005, acc
    assert max(acc, key=acc.get) == "SVM RBF", acc

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    X2 = Xs[:, :2]
    xx, yy = np.meshgrid(np.linspace(-2.5, 3.5, 200), np.linspace(-2.5, 3.5, 200))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        zl = SVC(kernel="linear").fit(X2, y).decision_function(np.c_[xx.ravel(), yy.ravel()])
        zr = SVC(kernel="rbf", C=5.0).fit(X2, y).decision_function(np.c_[xx.ravel(), yy.ravel()])
    axes[0].contourf(xx, yy, zr.reshape(xx.shape), levels=1, colors=["#dbeafe", "#ffedd5"], alpha=0.7)
    axes[0].contour(xx, yy, zl.reshape(xx.shape), levels=[0], colors="blue", linestyles="--",
                    linewidths=2)
    axes[0].contour(xx, yy, zr.reshape(xx.shape), levels=[0], colors="red", linewidths=2)
    axes[0].scatter(X2[y == 0, 0], X2[y == 0, 1], c="#1d4ed8", s=6, alpha=0.5, label="Barato")
    axes[0].scatter(X2[y == 1, 0], X2[y == 1, 1], c="#c2410c", s=6, alpha=0.5, label="Caro")
    axes[0].plot([], [], "b--", label="Frontera lineal")
    axes[0].plot([], [], "r-", label="Frontera RBF")
    axes[0].set_xlabel("Edad (estandarizada)")
    axes[0].set_ylabel("KM (estandarizados)")
    axes[0].set_title("Fronteras 2D (solo edad+KM, ilustrativo)")
    axes[0].legend(fontsize=8, markerscale=4)
    order = ["Naive Bayes", "Boosting", "RF n=200", "k-NN k=25", "Logística", "Árbol d=5", "SVM RBF"]
    vals = [acc[k] for k in order]
    colors = ["#16a34a" if k == "SVM RBF" else "#94a3b8" for k in order]
    bars = axes[1].barh(order, vals, color=colors)
    for b, v in zip(bars, vals):
        axes[1].text(v + 0.001, b.get_y() + b.get_height() / 2, "%.1f %%" % (v * 100),
                     va="center", fontsize=9)
    axes[1].set_xlim(0.80, 0.90)
    axes[1].set_xlabel("Accuracy (CV 5-fold, mismos folds)")
    axes[1].set_title("Torneo U8: SVM gana por nariz (87,7 %)")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u1_muestreo(out: Path) -> Path:
    """Muestreo: distribución de medias por n + muestra sesgada marcada."""
    _need_deps()
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(CSV).dropna(subset=["Price", "Age_08_04"])
    p = df["Price"].values
    mu = p.mean()
    sesgo = df.loc[df["Age_08_04"] > 60, "Price"].mean()
    assert abs(mu - 10730.8) < 1.0, mu
    assert abs(sesgo - 8542.9) < 1.0, sesgo
    rng = np.random.default_rng(42)
    ns = [30, 100, 500]
    sims = {n: np.array([rng.choice(p, n, replace=False).mean() for _ in range(2000)])
            for n in ns}
    assert abs(sims[30].std() - 660.3) < 15.0, sims[30].std()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.6))
    for n, c in zip(ns, ["#f59e0b", "#0ea5e9", "#16a34a"]):
        axes[0].hist(sims[n], bins=40, alpha=0.55, label="n=%d (sd %.0f)" % (n, sims[n].std()),
                     color=c, density=True)
    axes[0].axvline(mu, color="black", linewidth=2, label="Media real 10.731")
    axes[0].axvline(sesgo, color="red", linestyle="--", linewidth=2,
                    label="Solo viejos: 8.543 (sesgo)")
    axes[0].set_xlabel("Media muestral del precio (€)")
    axes[0].set_ylabel("Densidad")
    axes[0].set_title("2000 muestras por tamaño: más n, más puntería")
    axes[0].legend(fontsize=9)
    means = [sims[n].mean() for n in ns]
    sds = [sims[n].std() for n in ns]
    axes[1].errorbar(ns, means, yerr=[s * 1.96 for s in sds], fmt="o-", capsize=5,
                     color="#0ea5e9", label="Media ± 1,96·sd (95 %)")
    axes[1].axhline(mu, color="black", linewidth=1.5, label="Media real")
    axes[1].axhline(sesgo, color="red", linestyle="--", label="Sesgo viejos")
    axes[1].set_xscale("log")
    axes[1].set_xticks(ns)
    axes[1].set_xticklabels([str(n) for n in ns])
    axes[1].set_xlabel("Tamaño de muestra (escala log)")
    axes[1].set_ylabel("Precio medio estimado (€)")
    axes[1].set_title("El intervalo se achica; el sesgo no")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


EQUIPO_U9 = ["ABS", "Airbag_1", "Airbag_2", "Airco", "Backseat_Divider",
              "BOVAG_Guarantee", "Boardcomputer", "CD_Player", "Central_Lock",
              "Met_Color", "Mfr_Guarantee", "Mistlamps", "Power_Steering",
              "Powered_Windows", "Sport_Model", "Tow_Bar"]


def fig_u9_sop(out: Path) -> Path:
    """Soporte: 16 extras ordenados + cadena de monotonicidad."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt

    B = pd.read_csv(CSV)[EQUIPO_U9]
    sop1 = B.mean().sort_values()
    assert abs(sop1["Power_Steering"] - 0.9784) < 0.002, sop1.to_dict()
    assert abs(sop1["CD_Player"] - 0.2188) < 0.002, sop1.to_dict()
    chain_labels = ["Airbag_1", "+ Power_Steering", "+ BOVAG_Guar.", "+ ABS"]
    chain_cols = [["Airbag_1"], ["Airbag_1", "Power_Steering"],
                  ["Airbag_1", "Power_Steering", "BOVAG_Guarantee"],
                  ["Airbag_1", "Power_Steering", "BOVAG_Guarantee", "ABS"]]
    chain = [B[c].all(axis=1).mean() for c in chain_cols]
    assert abs(chain[0] - 0.9708) < 0.002 and abs(chain[-1] - 0.7409) < 0.002, chain
    assert all(a >= b for a, b in zip(chain, chain[1:])), chain

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2))
    colors = ["#16a34a" if v >= 0.5 else "#94a3b8" for v in sop1.values]
    axes[0].barh(sop1.index, sop1.values, color=colors)
    axes[0].axvline(0.5, color="black", linestyle="--", linewidth=1,
                    label="min_sop = 0,5 (10 frecuentes)")
    axes[0].set_xlabel("Soporte (fracción de autos)")
    axes[0].set_title("Soporte de cada extra (16 columnas)")
    axes[0].legend(fontsize=9)
    bars = axes[1].bar(chain_labels, chain, color=["#0ea5e9", "#0ea5e9", "#0ea5e9", "#f59e0b"])
    for b, v in zip(bars, chain):
        axes[1].text(b.get_x() + b.get_width() / 2, v + 0.01, "%.3f" % v,
                     ha="center", fontsize=10)
    axes[1].set_ylabel("Soporte")
    axes[1].set_ylim(0, 1.05)
    axes[1].set_title("Monotonicidad: agregar ítems nunca suma")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


REGLAS_U9 = [
    ("Mfr_Guar. → BOVAG", "Mfr_Guarantee", "BOVAG_Guarantee"),
    ("Airbag_2 → ABS", "Airbag_2", "ABS"),
    ("Vidrios → Cierre", "Powered_Windows", "Central_Lock"),
    ("Cierre → Vidrios", "Central_Lock", "Powered_Windows"),
    ("Airco → Airbag_2", "Airco", "Airbag_2"),
    ("Tow_Bar → Metálico", "Tow_Bar", "Met_Color"),
    ("CD → Boardcomp.", "CD_Player", "Boardcomputer"),
]


def fig_u9_reglas(out: Path) -> Path:
    """Reglas: confianza ordena por obviedad, lift por hallazgo."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt

    B = pd.read_csv(CSV)[EQUIPO_U9]
    rows = []
    for nombre, a, b in REGLAS_U9:
        sop = (B[a] & B[b]).mean()
        conf = sop / B[a].mean()
        lift = conf / B[b].mean()
        rows.append((nombre, sop, conf, lift))
    d = {r[0]: r for r in rows}
    assert abs(d["CD → Boardcomp."][3] - 2.43) < 0.03, d
    assert abs(d["Mfr_Guar. → BOVAG"][2] - 0.981) < 0.005, d
    assert abs(d["Mfr_Guar. → BOVAG"][3] - 1.10) < 0.03, d

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.0))
    por_conf = sorted(rows, key=lambda r: r[2])
    axes[0].barh([r[0] for r in por_conf], [r[2] for r in por_conf], color="#0ea5e9")
    axes[0].set_xlabel("Confianza P(B|A)")
    axes[0].set_xlim(0, 1.05)
    axes[0].set_title("Por confianza gana lo obvio (98 %)")
    por_lift = sorted(rows, key=lambda r: r[3])
    colors = ["#16a34a" if r[3] >= 1.5 else "#94a3b8" for r in por_lift]
    axes[1].barh([r[0] for r in por_lift], [r[3] for r in por_lift], color=colors)
    axes[1].axvline(1.0, color="red", linestyle="--", linewidth=1.5,
                    label="lift = 1 (azar)")
    axes[1].set_xlabel("Lift (veces sobre el azar)")
    axes[1].set_title("Por lift gana el hallazgo (×2,43)")
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def _apriori_levels(B, items, min_sop):
    """Mini-Apriori: [(candidatos, frecuentes)] por nivel L1, L2, ..."""
    import itertools
    lvl1 = [(a,) for a in items]
    cur = {frozenset([a]) for a in items if B[a].mean() >= min_sop}
    levels = [(len(lvl1), len(cur))]
    k = 2
    while cur:
        cands = set()
        lst = sorted(cur, key=sorted)
        for i in range(len(lst)):
            for j in range(i + 1, len(lst)):
                u = lst[i] | lst[j]
                if len(u) == k and all(frozenset(s) in cur
                                       for s in itertools.combinations(u, k - 1)):
                    cands.add(u)
        if not cands:
            break
        nxt = {c for c in cands if B[list(c)].all(axis=1).mean() >= min_sop}
        levels.append((len(cands), len(nxt)))
        cur, k = nxt, k + 1
    return levels


def fig_u9_apriori(out: Path) -> Path:
    """Apriori: candidatos vs frecuentes por nivel + total vs min_sop."""
    _need_deps()
    import pandas as pd
    import matplotlib.pyplot as plt
    import numpy as np

    B = pd.read_csv(CSV)[EQUIPO_U9]
    lv04 = _apriori_levels(B, EQUIPO_U9, 0.4)
    assert [f for _, f in lv04] == [11, 47, 88, 84, 40, 9, 1], lv04
    assert sum(f for _, f in lv04) == 280, lv04
    msops = [0.3, 0.4, 0.5, 0.6]
    totals = [sum(f for _, f in _apriori_levels(B, EQUIPO_U9, ms)) for ms in msops]
    assert totals == [787, 280, 108, 70], totals

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    lab = ["L%d" % (i + 1) for i in range(len(lv04))]
    cand = [c for c, _ in lv04]
    fre = [f for _, f in lv04]
    x = np.arange(len(lv04))
    axes[0].bar(x - 0.2, cand, 0.4, label="Candidatos", color="#0ea5e9")
    axes[0].bar(x + 0.2, fre, 0.4, label="Frecuentes", color="#16a34a")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(lab)
    axes[0].set_ylabel("Cantidad de itemsets")
    axes[0].set_title("Apriori min_sop=0,4: poda nivel por nivel")
    axes[0].legend()
    axes[0].annotate("L3: 115, no 165\n50 podados sin contar", xy=(2, 115), xytext=(3.8, 130),
                     arrowprops=dict(arrowstyle="->"), fontsize=9)
    axes[1].plot(msops, totals, "o-", color="#8b5cf6", linewidth=2)
    for ms, t in zip(msops, totals):
        axes[1].text(ms, t + 18, str(t), ha="center", fontsize=10)
    axes[1].axhline(2 ** 16 - 1, color="red", linestyle="--",
                    label="Fuerza bruta: 65.535")
    axes[1].set_xlabel("Soporte mínimo")
    axes[1].set_ylabel("Itemsets frecuentes totales")
    axes[1].set_title("Menos umbral, explosión contenida")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


BASURA_REF_U6 = ["Id", "Met_Color", "Airbag_1", "Airbag_2", "Gears", "Mistlamps",
                "Radio_cassette", "Power_Steering", "Backseat_Divider", "Central_Lock",
                "Radio", "cc", "Doors", "Cilynders", "CD_Player", "Airco", "Automatic",
                "Tow_Bar", "Boardcomputer", "Metallic_Rim", "Mfg_Year", "Mfr_Guarantee",
                "Cylinders", "ABS", "Sport_Model", "Age_08_04"]


def _ols_reference():
    """Replica el OLS de 9 vars del reference; devuelve (modelo, X, y)."""
    import pandas as pd
    import numpy as np
    import statsmodels.api as sm
    df = pd.read_csv(CSV)
    dl = df[df.select_dtypes(include=[np.number]).columns].copy()
    dl = dl.drop(columns=[c for c in BASURA_REF_U6 if c in dl.columns])
    dl = dl.fillna(dl.mean())
    y = dl["Price"]
    X = dl.drop(columns=["Price"])
    return sm.OLS(y, sm.add_constant(X)).fit(), X, y


def fig_u6_inf(out: Path) -> Path:
    """Inferencia OLS: distribución t con rechazo + barras t por variable."""
    _need_deps()
    import warnings
    import numpy as np
    import matplotlib.pyplot as plt
    from scipy import stats as st

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        m, X, y = _ols_reference()
    tvals = m.tvalues.drop("const")
    pvals = m.pvalues.drop("const")
    assert abs(tvals["KM"] - (-30.9033)) < 0.01, tvals.to_dict()
    assert abs(pvals["Mfg_Month"] - 0.0872) < 0.002, pvals.to_dict()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    t = np.linspace(-5, 5, 400)
    d = st.t(df=len(y) - len(X.columns) - 1).pdf(t)
    axes[0].plot(t, d, color="black")
    axes[0].fill_between(t, d, where=(np.abs(t) > 1.96), color="#fecaca",
                         label="Rechazo H0 (|t| > 1,96)")
    axes[0].axvline(-1.71, color="#0ea5e9", linewidth=2.5, label="Mfg_Month t=−1,71 (dudoso)")
    axes[0].annotate("KM t=−30,9\n(lejísimos → p≈0)", xy=(-4.9, 0.01), fontsize=9,
                     arrowprops=dict(arrowstyle="->"), xytext=(-3.4, 0.12))
    axes[0].set_xlabel("t-value (coeficiente / error estándar)")
    axes[0].set_ylabel("Densidad bajo H0: β = 0")
    axes[0].set_title("Si H0 fuera cierta, t caería acá")
    axes[0].legend(fontsize=9)
    order = tvals.sort_values()
    colors = ["#16a34a" if abs(v) > 1.96 else "#f59e0b" for v in order.values]
    bars = axes[1].barh(order.index, order.values, color=colors)
    axes[1].axvline(1.96, color="red", linestyle="--")
    axes[1].axvline(-1.96, color="red", linestyle="--", label="±1,96 (p = 0,05)")
    km_bar = bars[list(order.index).index("KM")]
    axes[1].text(km_bar.get_width() + 0.5, km_bar.get_y() + km_bar.get_height() / 2,
                 "t = −30,9", va="center", fontsize=9)
    axes[1].set_xlabel("t-value por variable (OLS 9 vars)")
    axes[1].set_title("Todo sólido salvo Mfg_Month (p = 0,087)")
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_met(out: Path) -> Path:
    """Métricas en test 80/20: RMSE/MAE (€) + MAPE/R² simple vs múltiple."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_squared_error, mean_absolute_error

    cols = ["Age_08_04", "KM", "HP", "cc", "Weight"]
    d = pd.read_csv(CSV).dropna(subset=cols + ["Price"])
    res = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for nom, cn in [("Simple\n(solo KM)", ["KM"]), ("Múltiple\n(5 vars)", cols)]:
            Xtr, Xte, ytr, yte = train_test_split(d[cn], d["Price"], test_size=0.2,
                                                  random_state=42)
            m = LinearRegression().fit(Xtr, ytr)
            yp = m.predict(Xte)
            res[nom] = {
                "rmse": mean_squared_error(yte, yp) ** 0.5,
                "mae": mean_absolute_error(yte, yp),
                "mape": float(np.mean(np.abs(yte - yp) / yte) * 100),
                "r2": m.score(Xte, yte),
            }
    s, q = res["Simple\n(solo KM)"], res["Múltiple\n(5 vars)"]
    assert abs(s["rmse"] - 2988.3) < 2.0, res
    assert abs(s["mape"] - 20.46) < 0.05, res
    assert abs(q["rmse"] - 1412.8) < 2.0, res
    assert abs(q["mape"] - 10.02) < 0.05, res

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    x = np.arange(2)
    w = 0.35
    names = list(res.keys())
    rmses = [res[k]["rmse"] for k in names]
    maes = [res[k]["mae"] for k in names]
    b1 = axes[0].bar(x - w / 2, rmses, w, label="RMSE", color="#0ea5e9")
    b2 = axes[0].bar(x + w / 2, maes, w, label="MAE", color="#16a34a")
    for b in list(b1) + list(b2):
        axes[0].text(b.get_x() + b.get_width() / 2, b.get_height() + 40,
                     "%.0f €" % b.get_height(), ha="center", fontsize=10)
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names)
    axes[0].set_ylabel("Error en test (€)")
    axes[0].set_title("Error en euros: la múltiple lo parte a la mitad")
    axes[0].legend()
    mapes = [res[k]["mape"] for k in names]
    r2s = [res[k]["r2"] for k in names]
    b3 = axes[1].bar(x - w / 2, mapes, w, label="MAPE (%)", color="#f59e0b")
    axes[1].set_ylabel("MAPE en test (%)", color="#b45309")
    ax2 = axes[1].twinx()
    b4 = ax2.bar(x + w / 2, r2s, w, label="R²", color="#8b5cf6")
    ax2.set_ylabel("R² en test", color="#6d28d9")
    ax2.set_ylim(0, 1.05)
    for b in b3:
        axes[1].text(b.get_x() + b.get_width() / 2, b.get_height() + 0.3,
                     "%.1f %%" % b.get_height(), ha="center", fontsize=10)
    for b in b4:
        ax2.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.02,
                 "%.3f" % b.get_height(), ha="center", fontsize=10)
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names)
    axes[1].set_title("MAPE 20→10 % · R² 0,33→0,85")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u6_anova(out: Path) -> Path:
    """ANOVA Price ~ Fuel_Type: violines por grupo + distribución F."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns
    from scipy import stats as st

    df = pd.read_csv(CSV).dropna(subset=["Price", "Fuel_Type"])
    order = ["Petrol", "Diesel", "CNG"]
    groups = [df.loc[df["Fuel_Type"] == f, "Price"].values for f in order]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        F, p = st.f_oneway(*groups)
    assert abs(F - 3.12) < 0.02, F
    assert abs(p - 0.0446) < 0.002, p
    fcrit = st.f.ppf(0.95, 2, len(df) - 3)

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    sns.violinplot(data=df, x="Fuel_Type", y="Price", order=order, ax=axes[0],
                   inner="box", hue="Fuel_Type", legend=False,
                   palette=["#0ea5e9", "#f59e0b", "#94a3b8"])
    means = [g.mean() for g in groups]
    axes[0].scatter(range(3), means, color="red", s=60, zorder=5, label="Media")
    for i, (m, g) in enumerate(zip(means, groups)):
        axes[0].text(i, m + 500, "%.0f\n(n=%d)" % (m, len(g)), ha="center",
                     fontsize=9, color="red")
    axes[0].set_xlabel("Combustible")
    axes[0].set_ylabel("Precio (€)")
    axes[0].set_title("¿Los tres violines cantan distinto?")
    axes[0].legend(fontsize=9)
    x = np.linspace(0, 6, 400)
    d = st.f(2, len(df) - 3).pdf(x)
    axes[1].plot(x, d, color="black")
    axes[1].fill_between(x, d, where=(x > fcrit), color="#fecaca",
                         label="Rechazo (F > %.2f)" % fcrit)
    axes[1].axvline(F, color="#16a34a", linewidth=2.5,
                    label="F observado = %.2f (p = %.3f)" % (F, p))
    axes[1].set_xlabel("F (variación entre / dentro)")
    axes[1].set_ylabel("Densidad bajo H0: medias iguales")
    axes[1].set_title("Cruza el umbral… por 12 centésimas")
    axes[1].legend(fontsize=9)
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u3_viol(out: Path) -> Path:
    """Violín Price×edad + histograma-vs-KDE + torta de modelos ilegible."""
    _need_deps()
    import warnings
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    df = pd.read_csv(CSV).dropna(subset=["Price", "Age_08_04", "Model"])
    df["Tramo"] = pd.qcut(df["Age_08_04"], 3, labels=["Joven", "Medio", "Veterano"])
    assert df["Tramo"].value_counts().min() > 400, df["Tramo"].value_counts().to_dict()
    top = df["Model"].value_counts().head(7)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.6))
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sns.violinplot(data=df, x="Tramo", y="Price", order=["Joven", "Medio", "Veterano"],
                       ax=axes[0], inner="box", hue="Tramo", legend=False,
                       palette=["#16a34a", "#0ea5e9", "#f59e0b"])
    axes[0].set_xlabel("Tramo de edad")
    axes[0].set_ylabel("Precio (€)")
    axes[0].set_title("Violín: forma + caja en uno")
    axes[1].hist(df["Price"], bins=3, color="#cbd5e1", edgecolor="black",
                 label="Hist. 3 bins (esconde)", density=True)
    axes[1].hist(df["Price"], bins=60, color="#93c5fd", alpha=0.6,
                 label="Hist. 60 bins (ruido)", density=True)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        sns.kdeplot(data=df, x="Price", ax=axes[1], color="#dc2626", linewidth=2.5,
                    label="KDE (estable)")
    axes[1].set_xlabel("Precio (€)")
    axes[1].set_title("KDE: la forma sin pelear bins")
    axes[1].legend(fontsize=8)
    resto = len(df) - top.sum()
    vals = list(top.values) + [resto]
    labs = [("…" + t[-12:]) if len(t) > 13 else t for t in top.index] + ["Otros"]
    axes[2].pie(vals, labels=labs, textprops={"fontsize": 7},
                colors=plt.cm.tab10.colors[:8])
    axes[2].set_title("Torta de 8 porciones: ilegible")

    fig.suptitle("Violín supera al boxplot · KDE supera al histograma · Torta: evitar",
                 fontsize=11, fontweight="bold")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


def fig_u2_trans(out: Path) -> Path:
    """Transformaciones: Price crudo vs log + edad en cuartiles."""
    _need_deps()
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_csv(CSV).dropna(subset=["Price", "Age_08_04"])
    sk_raw = df["Price"].skew()
    sk_log = np.log1p(df["Price"]).skew()
    assert abs(sk_raw - 1.704) < 0.01, sk_raw
    assert abs(sk_log - 0.734) < 0.01, sk_log
    df["Tramo"] = pd.qcut(df["Age_08_04"], 4, labels=["Q1 joven", "Q2", "Q3", "Q4 veterano"])
    med = df.groupby("Tramo", observed=True)["Price"].mean()
    cnt = df["Tramo"].value_counts()
    assert abs(med.iloc[0] - 15266) < 2.0, med.to_dict()
    assert abs(med.iloc[-1] - 7904) < 2.0, med.to_dict()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
    z_raw = (df["Price"] - df["Price"].mean()) / df["Price"].std()
    lp = np.log1p(df["Price"])
    z_log = (lp - lp.mean()) / lp.std()
    axes[0].hist(z_raw, bins=40, alpha=0.55, label="Crudo (skew 1,70)", color="#f59e0b",
                 density=True)
    axes[0].hist(z_log, bins=40, alpha=0.55, label="log1p (skew 0,73)", color="#0ea5e9",
                 density=True)
    axes[0].set_xlabel("Precio estandarizado (forma comparable)")
    axes[0].set_ylabel("Densidad")
    axes[0].set_title("Log achica la cola derecha")
    axes[0].legend()
    bars = axes[1].bar(med.index.astype(str), med.values,
                       color=["#16a34a", "#0ea5e9", "#f59e0b", "#dc2626"])
    for b, c in zip(bars, [cnt[i] for i in med.index]):
        axes[1].text(b.get_x() + b.get_width() / 2, b.get_height() + 150,
                     "%.0f €\n(n=%d)" % (b.get_height(), c), ha="center", fontsize=9)
    axes[1].set_ylabel("Precio medio (€)")
    axes[1].set_xlabel("Edad discretizada en cuartiles")
    axes[1].set_title("Discretizar: número → tramo con sentido")
    fig.tight_layout()
    out.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out, dpi=100)
    plt.close(fig)
    return out


GENERATORS = {
    "fig_u1_boxplot_price_km": fig_u1_boxplot_price_km,
    "fig_u1_bias_variance_tradeoff": fig_u1_bias_variance_tradeoff,
    "fig_u1_niveles_decision": fig_u1_niveles_decision,
    "fig_u1_itemset_estacionalidad": fig_u1_itemset_estacionalidad,
    "fig_u6_scatter_recta": fig_u6_scatter_recta,
    "fig_u6_residuos": fig_u6_residuos,
    "fig_u6_kfold": fig_u6_kfold,
    "fig_u2_defectos_conteo": fig_u2_defectos_conteo,
    "fig_u2_km1_cc_scatter": fig_u2_km1_cc_scatter,
    "fig_u2_wrangling_validacion": fig_u2_wrangling_validacion,
    "fig_u2_eda_tramos_corr": fig_u2_eda_tramos_corr,
    "fig_u2_outliers_iqr_z": fig_u2_outliers_iqr_z,
    "fig_u2_outliers_multi": fig_u2_outliers_multi,
    "fig_u3_catalogo": fig_u3_catalogo,
    "fig_u3_color": fig_u3_color,
    "fig_u3_eje_truncado": fig_u3_eje_truncado,
    "fig_u3_multivariado": fig_u3_multivariado,
    "fig_u3_red_arbol": fig_u3_red_arbol,
    "fig_u3_texto": fig_u3_texto,
    "fig_u4_mecanismos": fig_u4_mecanismos,
    "fig_u4_simple": fig_u4_simple,
    "fig_u4_donantes": fig_u4_donantes,
    "fig_u4_modelos": fig_u4_modelos,
    "fig_u5_porque": fig_u5_porque,
    "fig_u5_subset": fig_u5_subset,
    "fig_u5_caminos": fig_u5_caminos,
    "fig_u5_scad": fig_u5_scad,
    "fig_u6_corr": fig_u6_corr,
    "fig_u6_multiple": fig_u6_multiple,
    "fig_u6_diag1": fig_u6_diag1,
    "fig_u6_diag2": fig_u6_diag2,
    "fig_u6_poli": fig_u6_poli,
    "fig_u6_mas": fig_u6_mas,
    "fig_u7_dist": fig_u7_dist,
    "fig_u7_kmeans": fig_u7_kmeans,
    "fig_u7_jer": fig_u7_jer,
    "fig_u7_val": fig_u7_val,
    "fig_u7_pca": fig_u7_pca,
    "fig_u8_knn": fig_u8_knn,
    "fig_u8_log": fig_u8_log,
    "fig_u8_nbtree": fig_u8_nbtree,
    "fig_u8_rf": fig_u8_rf,
    "fig_u8_svm": fig_u8_svm,
    "fig_u1_muestreo": fig_u1_muestreo,
    "fig_u9_sop": fig_u9_sop,
    "fig_u9_reglas": fig_u9_reglas,
    "fig_u9_apriori": fig_u9_apriori,
    "fig_u6_inf": fig_u6_inf,
    "fig_u6_met": fig_u6_met,
    "fig_u6_anova": fig_u6_anova,
    "fig_u3_viol": fig_u3_viol,
    "fig_u2_trans": fig_u2_trans,
}


def cmd_list() -> int:
    if not FIGURE_REGISTRY:
        print("Registro vacío: aún no hay lecciones con figuras.")
        print("Plantilla disponible: fig_u1_boxplot_price_km (ver código).")
        return 0
    for slug, figs in FIGURE_REGISTRY.items():
        print(f"{slug}:")
        for png, fn, desc in figs:
            print(f"  - {png}  [{fn}]  {desc}")
    return 0


def cmd_run(slug: str) -> int:
    check_csv()
    if slug not in FIGURE_REGISTRY:
        print(f"Slug '{slug}' sin figuras registradas.", file=sys.stderr)
        return 1
    for png, fn, desc in FIGURE_REGISTRY[slug]:
        out = IMGDIR / png
        GENERATORS[fn](out)
        print(f"OK {out} — {desc}")
    return 0


def cmd_all() -> int:
    check_csv()
    rc = 0
    for slug in FIGURE_REGISTRY:
        rc |= cmd_run(slug)
    if not FIGURE_REGISTRY:
        print("Nada para generar (registro vacío).")
    return rc


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Regenera figuras del curso desde ToyotaCorolla.csv")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true")
    g.add_argument("--only", metavar="SLUG")
    g.add_argument("--all", action="store_true")
    a = p.parse_args(argv)
    if a.list:
        return cmd_list()
    if a.only:
        return cmd_run(a.only)
    return cmd_all()


if __name__ == "__main__":
    raise SystemExit(main())
