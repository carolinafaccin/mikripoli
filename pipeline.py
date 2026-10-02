"""MIKRIPOLI pipeline: IBGE census tracts of 2010 -> tables and figures for Sobradinho, Rio Pardo and Encantado.

    python pipeline.py                       # everything
    python pipeline.py --only tables         # tables
    python pipeline.py --only figures docs   # redraw figures and copy the README ones

Inputs come from raw_dir and outputs go to data_dir, both set in config/config.local.json.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from mikripoli import config, data, figures, metrics, style  # noqa: E402

README_FIGURES = ["map_tracts", "map_neighborhoods"]


def run_tables(t, nb, data_dir):
    out = data_dir / "tables"
    t.drop(columns="geometry").round(3).to_csv(out / "tracts_2010.csv", index=False)
    metrics.by_town(t).round(2).to_csv(out / "towns_2010.csv", index=False)
    metrics.by_neighborhood(t, nb).round(2).to_csv(out / "neighborhoods_2010.csv", index=False)
    cmp = metrics.compare(t)
    cmp.to_csv(out / "comparison_with_paper.csv", index=False)
    for _, r in cmp.iterrows():
        print(f"  {r['item']}: published {r['published']}, computed {r['computed']}")


def run_figures(t, nb, raw_dir, data_dir):
    style.setup()
    f = data_dir / "figures"
    streets = {town: data.load_streets(t, town, data_dir) for town in config.TOWNS}
    water = data.load_water(raw_dir, t, data_dir)
    figures.map_tracts(t, streets, water, f / "map_tracts.png")
    figures.map_neighborhoods(nb, streets, water, f / "map_neighborhoods.png")
    print(f"figures written to {f}")


def run_docs(data_dir):
    dest = Path(__file__).parent / "docs" / "img"
    dest.mkdir(parents=True, exist_ok=True)
    for name in README_FIGURES:
        shutil.copy(data_dir / "figures" / f"{name}.png", dest / f"{name}.png")
    print(f"copied {len(README_FIGURES)} figures to {dest}")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--only", nargs="+", choices=["tables", "figures", "docs"])
    args = p.parse_args()
    steps = args.only or ["tables", "figures", "docs"]

    raw_dir, data_dir = config.load()
    t = data.load_tracts(raw_dir)
    nb = data.neighborhoods(t)
    print(f"{len(t)} census tracts, {len(nb)} urban neighborhoods in {', '.join(config.TOWNS)}")
    if "tables" in steps:
        run_tables(t, nb, data_dir)
    if "figures" in steps:
        run_figures(t, nb, raw_dir, data_dir)
    if "docs" in steps:
        run_docs(data_dir)


if __name__ == "__main__":
    main()
