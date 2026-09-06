"""Baza -> DataFrame. Sve ostale analize krecu odavde."""

import pandas as pd


def load_jobs(session, *, bez_duplikata=True, samo_sa_platom=False) -> pd.DataFrame:
    """Ucita oglase sa firmom i lokacijom u jedan ravan DataFrame.

    Jedino mjesto gdje se definise sta je validan oglas (duplicate_of IS NULL).
    Ako se taj filter razbaca po notebooku, prva promjena pravila tiho pokvari
    pola analiza.
    """
    raise NotImplementedError


def extract_seniority(title) -> str | None:
    """Naslov -> 'junior' | 'mid' | 'senior'. None kad se ne moze utvrditi.

    Pazi: austrijski oglasi rijetko pisu 'Senior' u naslovu - ocekuj puno None.
    """
    raise NotImplementedError


def add_derived_columns(df) -> pd.DataFrame:
    """Doda kolone koje racuna vise analiza: seniority, mjesec, salary_mid.

    salary_mid je sredina raspona - jedan broj po oglasu, lakse za statistiku
    nego dvije kolone.
    """
    raise NotImplementedError


def load_skills_corpus(session) -> pd.DataFrame:
    """Samo id + description oglasa sa upotrebljivim tekstom.

    Adzuna sijece opis na 500 znakova, pa za vadjenje vjestina vrijedi
    uglavnom karriere.at (prosjek 4090 znakova).
    """
    raise NotImplementedError
