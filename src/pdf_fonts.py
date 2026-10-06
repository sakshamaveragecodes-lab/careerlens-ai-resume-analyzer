"""Bundled fonts keep PDF rendering consistent across machines."""
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.config import ROOT


def register_fonts():
    for name, filename in (("CareerSans", "DejaVuSans.ttf"), ("CareerSans-Bold", "DejaVuSans-Bold.ttf")):
        if name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(name, str(ROOT / "assets/fonts" / filename)))
    pdfmetrics.registerFontFamily("CareerSans", normal="CareerSans", bold="CareerSans-Bold", italic="CareerSans", boldItalic="CareerSans-Bold")
