"""Plate. Racuna se nad salary_*_yearly - sirove kolone nisu uporedive.

Svugdje medijan, ne prosjek: jedan oglas od 750.000 pomjeri prosjek grada.
"""

import pandas as pd


def salary_coverage(df) -> pd.DataFrame:
    """Koliko oglasa uopste navodi platu, po izvoru: n, sa_platom, udio.

    Ide prije svake druge analize plata. karriere.at ima ~90%, Adzuna ~38%,
    pa spojeni prosjek nije prosjek trzista nego prosjek karriere.at-a.
    """
    raise NotImplementedError


def salary_stats(df, by="city", min_n=5) -> pd.DataFrame:
    """Statistika plata po nekoj koloni: n, median, p25, p75, mean.

    'by' moze biti city, region, seniority, source, employment_type_norm.
    Grupe ispod min_n se izbacuju - prosjek od tri oglasa nije nalaz.
    """
    raise NotImplementedError


def salary_by_seniority(df, min_n=5) -> pd.DataFrame:
    """Junior / mid / senior. Ocekuj malo uzorka - naslovi rijetko kazu seniority."""
    raise NotImplementedError


def salary_by_skill(df, skills, min_n=5) -> pd.DataFrame:
    """Medijan plate za oglase koji spominju svaku vjestinu: skill, n, median.

    Nije uzrocnost - Kubernetes oglasi placaju vise i zato sto su seniorski,
    ne samo zbog Kubernetesa.
    """
    raise NotImplementedError


def predicted_vs_real(df) -> pd.DataFrame:
    """Poredi plate koje je Adzuna pogodila (salary_is_predicted) sa stvarnima.

    Ako se razlikuju, pogodjene se izbacuju iz ostalih analiza - inace mjeris
    njihov model umjesto trzista.
    """
    raise NotImplementedError


def salary_distribution(df, bins=None) -> pd.DataFrame:
    """Histogram plata: raspon, n. Za provjeru da li je raspodjela normalna
    ili ima dugacak rep prema gore (skoro uvijek ima)."""
    raise NotImplementedError
