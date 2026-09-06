"""Traznja: ko trazi, gdje, koliko i kako se to mijenja kroz vrijeme."""

import pandas as pd


def source_comparison(df) -> pd.DataFrame:
    """Popunjenost svakog polja po izvoru: kolona, adzuna %, karriere_at %.

    Pokreni ovo prvo. Bez ovoga ne znas koje tvrdnje podaci uopste podnose -
    npr. remote_option postoji samo kod karriere.at.
    """
    raise NotImplementedError


def jobs_by_city(df, min_n=5) -> pd.DataFrame:
    """Broj oglasa po gradu: city, n, udio. Grupe ispod min_n se izbacuju."""
    raise NotImplementedError


def jobs_by_region(df) -> pd.DataFrame:
    """Broj oglasa po pokrajini.

    235 oglasa nema pokrajinu - prikazi ih kao 'nepoznato', nemoj ih tiho
    izbaciti, jer onda udjeli ne daju 100%.
    """
    raise NotImplementedError


def top_companies(df, n=15) -> pd.DataFrame:
    """Firme sa najvise oglasa: company_name, n, broj_gradova."""
    raise NotImplementedError


def jobs_over_time(df, freq="W") -> pd.DataFrame:
    """Broj oglasa kroz vrijeme, razdvojen po izvoru.

    Razdvajanje je obavezno: skok u avgustu je mozda samo dan kad si
    povukao podatke, a ne stvarni skok traznje.
    """
    raise NotImplementedError


def remote_breakdown(df) -> pd.DataFrame:
    """Onsite / hybrid / remote.

    Samo nad karriere.at - Adzuna nema to polje, pa njenih 563 praznih
    znaci 'ne znamo', a ne 'nije remote'.
    """
    raise NotImplementedError


def employment_breakdown(df) -> pd.DataFrame:
    """Full-time / part-time / internship / apprenticeship, sa udjelima."""
    raise NotImplementedError


def title_keywords(df, keywords, min_n=5) -> pd.DataFrame:
    """Koliko oglasa spominje koju tehnologiju u naslovu.

    Trazi po \\b granicama rijeci - 'java' ne smije uhvatiti 'JavaScript'.
    """
    raise NotImplementedError
