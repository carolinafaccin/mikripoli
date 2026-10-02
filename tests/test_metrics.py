"""Unit tests on synthetic data."""
import geopandas as gpd
from shapely.geometry import box

from mikripoli import data, metrics


def _tracts():
    return gpd.GeoDataFrame({
        "tract": ["430680905000001", "430680905000002", "430680910000001"],
        "cd_mun": ["4306809"] * 3, "town": ["Encantado"] * 3,
        "situation": ["URBANO", "URBANO", "URBANO"], "neighborhood": ["Centro", "Centro", "Vila"],
        "residents": [100, 300, 50], "residents_per_dwelling": [2.0, 3.0, 4.0], "income_mw": [4.0, 2.0, 1.0],
    }, geometry=[box(0, 0, 1, 1), box(1, 0, 2, 1), box(9, 9, 10, 10)], crs=31982)


def test_neighborhoods_only_from_the_seat_district():
    nb = data.neighborhoods(_tracts())
    assert list(nb["neighborhood"]) == ["Centro"] and nb["residents"].iloc[0] == 400


def test_view_covers_the_seat_only():
    x0, y0, x1, y1 = data.town_view(_tracts(), "Encantado", pad=0)
    assert (x0, y0, x1, y1) == (0, 0, 2, 1)


def test_neighborhood_means_are_weighted_by_residents():
    t = _tracts()
    n = metrics.by_neighborhood(t, data.neighborhoods(t)).set_index("neighborhood")
    assert n.loc["Centro", "income_mw"] == 2.5 and n.loc["Centro", "residents_per_dwelling"] == 2.75
