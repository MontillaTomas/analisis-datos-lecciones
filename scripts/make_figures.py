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


GENERATORS = {
    "fig_u1_boxplot_price_km": fig_u1_boxplot_price_km,
    "fig_u1_bias_variance_tradeoff": fig_u1_bias_variance_tradeoff,
    "fig_u1_niveles_decision": fig_u1_niveles_decision,
    "fig_u1_itemset_estacionalidad": fig_u1_itemset_estacionalidad,
    "fig_u6_scatter_recta": fig_u6_scatter_recta,
    "fig_u6_residuos": fig_u6_residuos,
    "fig_u6_kfold": fig_u6_kfold,
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
