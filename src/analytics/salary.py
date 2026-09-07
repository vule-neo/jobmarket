"""Plate. Racuna se nad salary_*_yearly - sirove kolone nisu uporedive.

Svugdje medijan, ne prosjek: jedan oglas od 750.000 pomjeri prosjek grada.
"""

import re

import numpy as np
import pandas as pd


def test_df() -> pd.DataFrame:
    """Mali izmisljeni DataFrame za probu funkcija, bez baze.

        from src.analytics.salary import test_df
        df = test_df()

    Namjerno ima sve zamke iz stvarnih podataka: prazne plate, outlier od
    300k, grupu od jednog oglasa (da se vidi da li min_n radi), Adzunine
    predvidjene plate i karriere.at bez gornje granice.
    """
    return pd.DataFrame(
        {
            "id":           [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
            "source":       ["adzuna"] * 5 + ["karriere_at"] * 7,
            "city":         ["Wien", "Wien", "Wien", "Graz", "Graz",
                             "Wien", "Wien", "Wien", "Graz", "Linz", "Linz", "Villach"],
            "region":       ["Wien", "Wien", "Wien", "Steiermark", "Steiermark",
                             "Wien", "Wien", "Wien", "Steiermark", "Oberösterreich",
                             "Oberösterreich", "Kärnten"],
            "seniority":    ["senior", "mid", "junior", "senior", "mid",
                             "senior", "senior", "junior", "mid", "mid", "junior", "senior"],
            "employment_type_norm": ["full_time"] * 9 + ["part_time", "full_time", "full_time"],
            "salary_min_yearly":    [70000, 55000, np.nan, 65000, np.nan,
                                     85000, 300000, 42000, 60000, 48000, 45000, 52000],
            # karriere.at pise 'ab 55.000' - gornja granica najcesce fali
            "salary_max_yearly":    [90000, 62000, np.nan, 75000, np.nan,
                                     np.nan, np.nan, np.nan, 70000, np.nan, np.nan, np.nan],
            # u stvarnoj bazi je Adzuna sve oznacila kao False, ali ovdje
            # namjerno stoji i par True da predicted_vs_real ima sta porediti
            "salary_is_predicted":  [False, True, False, True, False] + [None] * 7,
            "title":        ["Senior Java Developer", "Java Developer", "Junior Developer",
                             "Senior Data Engineer", "Data Analyst", "Senior Python Developer",
                             "Head of Engineering", "Junior QA", "DevOps Engineer",
                             "Angular Developer", "Junior Data Analyst", "Senior Consultant"],
        }
    )


def salary_coverage(df) -> pd.DataFrame:
    """Koliko oglasa uopste navodi platu, po izvoru: n, sa_platom, udio.

    Ide prije svake druge analize plata. karriere.at ima ~90%, Adzuna ~38%,
    pa spojeni prosjek nije prosjek trzista nego prosjek karriere.at-a.
    """
    # size broji SVE redove u grupi, count broji samo NEPRAZNE.
    # Razlika izmedju ta dva je upravo ono sto trazimo.
    rezultat = (
        df.groupby("source")
        .agg(
            n=("id", "size"),
            sa_platom=("salary_min_yearly", "count"),
        )
        .reset_index()
    )

    rezultat["udio"] = rezultat["sa_platom"] / rezultat["n"]

    print(rezultat.head(10))
    return rezultat


def salary_stats(df, by="city", min_n=5) -> pd.DataFrame:
    """Statistika plata po nekoj koloni: n, median, p25, p75, mean.

    'by' moze biti city, region, seniority, source, employment_type_norm.
    Grupe ispod min_n se izbacuju - prosjek od tri oglasa nije nalaz.
    """
    rez = (
        df.groupby(by).agg(
            # count, ne size: statistika se racuna samo nad oglasima koji
            # imaju platu, pa n mora brojati njih. Sa size bi Wien imao
            # n=6 a medijan izracunat nad 5 vrijednosti.
            n=("salary_min_yearly", "count"),
            median=("salary_min_yearly", "median"),
            p25=("salary_min_yearly", lambda s: s.quantile(0.25)),
            p75=("salary_min_yearly", lambda s: s.quantile(0.75)),
            mean=("salary_min_yearly", "mean"),
        ).reset_index()
    )

    rez = rez[rez["n"] >= min_n]

    return rez.sort_values("n", ascending=False).reset_index(drop=True)


def salary_by_seniority(df, min_n=5) -> pd.DataFrame:
    """Junior / mid / senior.

    Specijalan slucaj salary_stats - nema smisla prepisivati istu agregaciju,
    samo se rezultat sortira logicnim redom umjesto po broju oglasa.
    """
    rezultat = salary_stats(df, by="seniority", min_n=min_n)

    red = {"junior": 0, "mid": 1, "senior": 2}
    return (
        rezultat.sort_values("seniority", key=lambda s: s.map(red))
        .reset_index(drop=True)
    )


def salary_by_skill(df, skills, min_n=5) -> pd.DataFrame:
    """Statistika plata za oglase koji spominju svaku vjestinu.

    Vraca skill, n, median, p25, p75, mean.

    Ovdje groupby NE moze: jedan oglas spominje i Javu i Spring i Docker,
    pa upada u vise grupa odjednom, a groupby svaki red stavlja u tacno
    jednu. Zato se za svaku vjestinu pravi maska i racuna nad podskupom.
    Zbir n je zato veci od broja oglasa - to nije greska.

    Nije uzrocnost - Kubernetes oglasi placaju vise i zato sto su seniorski,
    ne samo zbog Kubernetesa.
    """
    tekst = df["title"].fillna("")
    if "description" in df.columns:
        # naslov sam rijetko nabraja tehnologije, opis ih nabraja
        tekst = tekst + " " + df["description"].fillna("")

    redovi = []
    for vjestina in skills:
        # ista granica rijeci kao u market.title_keywords: \b ne radi uz
        # znakove kao u 'C++', a golo contains bi u 'java' uhvatilo 'JavaScript'
        sablon = r"(?<!\w)" + re.escape(vjestina) + r"(?!\w)"
        maska = tekst.str.contains(sablon, case=False, regex=True)

        plate = df.loc[maska, "salary_min_yearly"].dropna()

        redovi.append(
            {
                "skill": vjestina,
                "n": len(plate),
                "median": plate.median(),
                "p25": plate.quantile(0.25),
                "p75": plate.quantile(0.75),
                "mean": plate.mean(),
            }
        )

    rezultat = pd.DataFrame(redovi)
    rezultat = rezultat[rezultat["n"] >= min_n]

    return rezultat.sort_values("median", ascending=False).reset_index(drop=True)


def predicted_vs_real(df) -> pd.DataFrame:
    """Poredi plate koje je izvor pogodio sa onima koje je oglas stvarno naveo.

    Kolona izvori postoji zbog zamke: oznaka je vezana za izvor (samo Adzuna
    je uopste ima), pa ako se grupe razlikuju, ne zna se da li je razlika od
    predvidjanja ili od toga sto su to dva razlicita skupa oglasa. Bez te
    kolone bi se lako izveo pogresan zakljucak.

    Na trenutnim podacima nema nijedne predvidjene plate - Adzuna je svih
    144 oznacila kao stvarne. Funkcija tad vrati samo dva reda i to je
    tacan odgovor, nije greska.
    """
    sa_platom = df[df["salary_min_yearly"].notna()]

    vrsta = (
        sa_platom["salary_is_predicted"]
        .map({True: "predvidjena", False: "stvarna"})
        .fillna("izvor nema oznaku")
        .rename("vrsta")
    )

    rezultat = (
        sa_platom.groupby(vrsta)
        .agg(
            n=("salary_min_yearly", "count"),
            median=("salary_min_yearly", "median"),
            mean=("salary_min_yearly", "mean"),
            izvori=("source", lambda s: ", ".join(sorted(s.unique()))),
        )
        .reset_index()
    )

    return rezultat


def salary_distribution(df, bins=None) -> pd.DataFrame:
    """Histogram plata: raspon, n, udio.

    Pokazuje da li je raspodjela simetricna ili ima dugacak rep prema gore
    (skoro uvijek ima). To je razlog zasto se svugdje koristi medijan.
    """
    plate = df["salary_min_yearly"].dropna()

    if bins is None:
        # granice po austrijskim IT platama; np.inf hvata sve iznad 100k
        # u jednu kantu, da outlier od 300k ne razvuce tabelu
        bins = [0, 30000, 40000, 50000, 60000, 70000, 80000, 100000, np.inf]

    # cut svaku platu svrsta u kantu; sort_index drzi kante rastucim redom,
    # jer bi value_counts sortirao po velicini i raspored bi izgubio smisao
    kante = pd.cut(plate, bins=bins)

    rezultat = (
        kante.value_counts().sort_index().rename_axis("raspon").reset_index(name="n")
    )
    rezultat["udio"] = rezultat["n"] / len(plate)

    # Interval nije JSON tip - bez ovoga FastAPI ne moze vratiti rezultat
    rezultat["raspon"] = rezultat["raspon"].astype(str)

    return rezultat

if __name__=="__main__":
    salary_stats(df=test_df())