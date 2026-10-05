"""Census tracts of 2010 with their universe results, neighborhoods, streets and water."""
import geopandas as gpd
import pandas as pd
from shapely.geometry import box

from . import osm
from .config import BASICO, CRS, MIN_WAGE_2010, TOWNS, TRACTS, WATER

# Census 2010, Basico file: V002 residents in permanent private dwellings, V003 mean residents per
# dwelling, V005 mean monthly nominal income of the household heads (R$)
COLUMNS = {"V002": "residents", "V003": "residents_per_dwelling", "V005": "income_head"}


def load_tracts(sources_dir):
    codes = ", ".join(f"'{c}'" for c in TOWNS.values())
    t = gpd.read_file(sources_dir / TRACTS, where=f"CD_GEOCODM IN ({codes})").to_crs(CRS)
    t = t.rename(columns={"CD_GEOCODI": "tract", "CD_GEOCODM": "cd_mun", "NM_BAIRRO": "neighborhood", "TIPO": "situation"})
    t["town"] = t["cd_mun"].map({v: k for k, v in TOWNS.items()})
    b = pd.read_csv(sources_dir / BASICO, sep=";", encoding="latin-1", decimal=",", dtype={"Cod_setor": str},
                    usecols=["Cod_setor", "Cod_municipio", *COLUMNS], low_memory=False)
    b = b[b["Cod_municipio"].astype(str).isin(TOWNS.values())]
    for c in COLUMNS:
        b[c] = pd.to_numeric(b[c].astype(str).str.replace(",", "."), errors="coerce")
    t = t.merge(b.rename(columns=COLUMNS | {"Cod_setor": "tract"})[["tract", *COLUMNS.values()]], on="tract", how="left")
    t["income_mw"] = t["income_head"] / MIN_WAGE_2010
    return t[["tract", "cd_mun", "town", "situation", "neighborhood", *COLUMNS.values(), "income_mw", "geometry"]]


def neighborhoods(t):
    """Urban neighborhoods of each town's seat (IBGE 2010 neighborhood codes), dissolved from the tracts."""
    u = t[(t["situation"] == "URBANO") & t["neighborhood"].notna() & t["tract"].str[:9].eq(t["cd_mun"] + "05")]
    n = u.dissolve(["town", "neighborhood"], aggfunc={"residents": "sum"}).reset_index()
    return n


def town_view(t, town, pad=600):
    """Map extent: the urban tracts of the town's seat district (district code 05), padded."""
    u = t[(t["town"] == town) & (t["situation"] == "URBANO") & t["tract"].str[:9].eq(t["cd_mun"] + "05")]
    minx, miny, maxx, maxy = u.total_bounds
    return (minx - pad, miny - pad, maxx + pad, maxy + pad)


def load_water(sources_dir, t, outputs_dir):
    cache = outputs_dir / "cache" / "water.gpkg"
    if cache.exists():
        return gpd.read_file(cache)
    for rel in WATER:
        if (sources_dir / rel).exists():
            w = gpd.read_file(sources_dir / rel, bbox=tuple(t.buffer(3000).total_bounds)).to_crs(CRS)[["geometry"]]
            w.to_file(cache)
            return w
    return None


def load_streets(t, town, outputs_dir):
    """OpenStreetMap streets around the town (downloaded once, cached in outputs_dir/cache)."""
    w, s, e, n = gpd.GeoSeries([box(*town_view(t, town))], crs=CRS).to_crs(4326).total_bounds
    slug = town.lower().replace(" ", "_")
    return osm.roads((s - 0.01, w - 0.01, n + 0.01, e + 0.01), outputs_dir / "cache" / f"osm_{slug}.json", crs=CRS)
