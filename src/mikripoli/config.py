"""Paths: read from config/config.local.json (gitignored), like the other repositories.

- raw_dir   shared raw-data catalog (read only)
- data_dir  this project's outputs (tables, figures, cache/ for OpenStreetMap downloads)
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
    """Return (raw_dir, data_dir) as Paths; create data_dir subfolders."""
    cfg_path = ROOT / "config" / "config.local.json"
    if not cfg_path.exists():
        raise SystemExit(f"Missing {cfg_path.name}: copy config/config.local.json.example and set raw_dir and data_dir.")
    cfg = json.loads(cfg_path.read_text())
    raw_dir, data_dir = Path(cfg["raw_dir"]), Path(cfg["data_dir"])
    if not raw_dir.exists():
        raise SystemExit(f"raw_dir not found: {raw_dir}")
    for sub in ("tables", "figures", "cache"):
        (data_dir / sub).mkdir(parents=True, exist_ok=True)
    return raw_dir, data_dir
