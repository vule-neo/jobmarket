"""Baza -> DataFrame. Sve ostale analize krecu odavde."""

import re

import pandas as pd
from sqlalchemy import func, select

from src.db.models import Company, Job, Location


def load_jobs(session, *, bez_duplikata=True, samo_sa_platom=False) -> pd.DataFrame:
    """Ucita oglase sa firmom i lokacijom u jedan ravan DataFrame.

    Jedino mjesto gdje se definise sta je validan oglas (duplicate_of IS NULL).
    Ako se taj filter razbaca po notebooku, prva promjena pravila tiho pokvari
    pola analiza.
    """
    stmt = (
        select(
            Job.id,
            Job.source,
            Job.title,
            Job.description,
            Company.name.label("company_name"),
            Location.city,
            Location.region,
            Location.display_name.label("location_raw"),
            Job.salary_min_yearly,
            Job.salary_max_yearly,
            Job.salary_currency,
            Job.salary_is_predicted,
            Job.employment_type_norm,
            Job.remote_option,
            Job.posted_at,
        )
        # outerjoin, ne join: 24 oglasa nema firmu, a obican join bi ih
        # tiho izbacio iz svake analize
        .outerjoin(Company, Job.company_id == Company.id)
        .outerjoin(Location, Job.location_id == Location.id)
    )

    if bez_duplikata:
        stmt = stmt.where(Job.duplicate_of.is_(None))

    if samo_sa_platom:
        stmt = stmt.where(Job.salary_min_yearly.is_not(None))

    # session.connection() daje vezu koju pandas zna citati
    df = pd.read_sql(stmt, session.connection())

    # Numeric iz Postgresa stize kao Decimal - statistika nad Decimalom puca
    for kolona in ("salary_min_yearly", "salary_max_yearly"):
        df[kolona] = pd.to_numeric(df[kolona], errors="coerce")

    return add_derived_columns(df)


# 'Senior' u 'Senior Consultant', ali ne u 'seniority'.
# (?<!\w) i (?!\w) umjesto \b, isto kao u market.title_keywords.
seniority_sabloni = {
    "senior": r"(?<!\w)(?:senior|sr\.|lead|principal|head\sof|architekt)(?!\w)",
    "junior": r"(?<!\w)(?:junior|jr\.|praktikant|praktikum|intern|trainee|lehrling)(?!\w)",
    "mid":    r"(?<!\w)(?:mid[\s-]?level|regular)(?!\w)",
}


def extract_seniority(title) -> str | None:
    """Naslov -> 'junior' | 'mid' | 'senior'. None kad se ne moze utvrditi.

    Vraca None umjesto da pretpostavi 'mid': oglas bez oznake nije nuzno
    medior, samo mu firma nije napisala nivo. groupby ionako izbacuje None,
    pa se statistika racuna samo nad oglasima koji su nivo stvarno naveli.

    Redoslijed provjere je bitan - 'Senior Java (Junior welcome)' je senior.
    """
    if not title:
        return None

    for nivo in ("senior", "junior", "mid"):
        if re.search(seniority_sabloni[nivo], title, re.IGNORECASE):
            return nivo

    return None


def add_derived_columns(df) -> pd.DataFrame:
    """Doda kolone koje racuna vise analiza: seniority, mjesec, salary_mid.

    Radi nad kopijom - originalni df ostaje netaknut.
    """
    df = df.copy()

    df["seniority"] = df["title"].map(extract_seniority)

    if "posted_at" in df.columns:
        datumi = pd.to_datetime(df["posted_at"], utc=True, errors="coerce")
        df["mjesec"] = datumi.dt.tz_localize(None).dt.to_period("M").dt.start_time

    # sredina raspona kad postoje obje granice. Kad gornja fali (karriere.at
    # pise 'ab 55.000' u 87% slucajeva) ostaje donja - zato je ova kolona
    # pristrasna nanize i za ozbiljnu statistiku se koristi salary_min_yearly.
    df["salary_mid"] = df[["salary_min_yearly", "salary_max_yearly"]].mean(axis=1)

    return df


# Adzuna sijece opis na 500 znakova; sve ispod ovog praga je odsjecen tekst
MIN_DUZINA_OPISA = 800


def load_skills_corpus(session, min_duzina=MIN_DUZINA_OPISA) -> pd.DataFrame:
    """Samo oglasi sa opisom dovoljno dugim za vadjenje vjestina.

    Adzuna sijece opis na 500 znakova, pa za Fazu 4 vrijedi uglavnom
    karriere.at (prosjek 4090 znakova). Filtrira se po duzini teksta,
    ne po imenu izvora - ako Adzuna jednom posalje pun opis, uci ce sam.
    """
    stmt = (
        select(Job.id, Job.source, Job.title, Job.description)
        .where(
            Job.duplicate_of.is_(None),
            Job.description.is_not(None),
            func.length(Job.description) >= min_duzina,
        )
    )

    return pd.read_sql(stmt, session.connection())
