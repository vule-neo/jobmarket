"""Crtanje za notebook. Prima gotov DataFrame iz market.py / salary.py.

Odvojeno od racunanja namjerno: Angular kasnije crta iste brojeve sam,
preko API-ja, pa ovdje ostaje samo ono sto treba u Jupyteru.

Svaka funkcija vraca matplotlib Axes da se moze dalje doraditi.
"""

import matplotlib.pyplot as plt


def bar_counts(df, x, y="n", title="", ax=None):
    """Vodoravni bar chart za brojanja (gradovi, firme, tehnologije).

    Vodoravno jer su imena gradova i firmi duga i uspravno se preklapaju.
    """
    raise NotImplementedError


def salary_box(df, by="city", ax=None):
    """Boxplot plata po grupi - pokazuje raspon i outliere, ne samo sredinu."""
    raise NotImplementedError


def trend_line(df, ax=None):
    """Linija broja oglasa kroz vrijeme, jedna linija po izvoru."""
    raise NotImplementedError


def salary_hist(df, bins=30, ax=None):
    """Histogram plata."""
    raise NotImplementedError


def annotate_n(ax, counts):
    """Dopise (n=..) uz svaku grupu na grafiku.

    Bez ovoga grafik izgleda uvjerljivo i kad grupa ima tri oglasa.
    """
    raise NotImplementedError
