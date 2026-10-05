"""Paths: read from config/config.local.json (gitignored), like the other repositories.

- sources_dir   shared raw-data catalog (read only)
- outputs_dir  this project's outputs (tables, figures, cache/ for OpenStreetMap downloads)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CRS = 31982  # SIRGAS 2000 / UTM 22S

# The three case-study towns of Silveira, Faccin, Detoni & Silva (2024)
TOWNS = {"Sobradinho": "4320701", "Rio Pardo": "4315701", "Encantado": "4306809"}

TRACTS = "ibge/censo/2010/setores_censitarios_rs/t0/43SEE250GC_SIR.shp"     # 2010 census tracts, RS
BASICO = "ibge/censo/2010/universo_rs/t0/CSV/Basico_RS.csv"                 # 2010 universe results by tract
WATER = ("_projetos/rio_pardo_enchentes_2024/shp/rs_hid_trecho_massa_dagua_a_ibge.shp",   # IBGE water bodies, RS
         "_archive/projetos/rio_pardo_enchentes_2024/shp/rs_hid_trecho_massa_dagua_a_ibge.shp")
MIN_WAGE_2010 = 510.0


def load():
    """Return (sources_dir, outputs_dir) as Paths; create outputs_dir subfolders."""
    cfg_path = ROOT / "config" / "config.local.json"
    if not cfg_path.exists():
        raise SystemExit(f"Missing {cfg_path.name}: copy config/config.local.json.example and set sources_dir and outputs_dir.")
    cfg = json.loads(cfg_path.read_text())
    sources_dir, outputs_dir = Path(cfg["sources_dir"]), Path(cfg["outputs_dir"])
    if not sources_dir.exists():
        raise SystemExit(f"sources_dir not found: {sources_dir}")
    for sub in ("tables", "figures", "cache"):
        (outputs_dir / sub).mkdir(parents=True, exist_ok=True)
    return sources_dir, outputs_dir
