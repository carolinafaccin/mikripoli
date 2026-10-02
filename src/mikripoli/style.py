"""Figure style: the brand (brand.py, synced from the lina-brand repository) plus this
repository's source line. Colors, palettes and helpers come from brand.py; edit them there."""
from . import brand
from .brand import *  # noqa: F401,F403  colors, data palettes, header, scalebar, halo, save...
from .config import ROOT

SOURCE = "Source: IBGE, Census 2010 (census tracts, universe results); OpenStreetMap; own calculations."
REPO = "github.com/carolinafaccin/mikripoli"


def setup():
    """Register the bundled fonts (OFL) and set the matplotlib defaults."""
    brand.setup(ROOT / "assets" / "fonts")


def footer(fig, note=SOURCE):
    brand.footer(fig, note, REPO)
