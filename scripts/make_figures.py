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


GENERATORS = {
    "fig_u1_boxplot_price_km": fig_u1_boxplot_price_km,
    "fig_u1_bias_variance_tradeoff": fig_u1_bias_variance_tradeoff,
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
