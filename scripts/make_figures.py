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
    # Piloto U1 (plantilla; la lección 0001 lo usa y lo documenta):
    # "tipos-de-datos-toyota": [
    #     ("0001-tipos-de-datos-toyota-fig1.png", "fig_u1_boxplot_price_km",
    #      "Boxplots de Price y KM (réplica del EDA del notebook ejemplo)."),
    # ],
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


GENERATORS = {
    "fig_u1_boxplot_price_km": fig_u1_boxplot_price_km,
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
