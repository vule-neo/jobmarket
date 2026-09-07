"""Traznja: ko trazi, gdje, koliko i kako se to mijenja kroz vrijeme."""

import re

import pandas as pd


def source_comparison(df) -> pd.DataFrame:
    """Popunjenost svakog polja po izvoru: kolona, adzuna %, karriere_at %.

    Pokreni ovo prvo. Bez ovoga ne znas koje tvrdnje podaci uopste podnose -
    npr. remote_option postoji samo kod karriere.at.

    Vraca udio 0-1, ne procenat - formatiranje je posao prikaza, ne racuna.
    Prvi red je n_oglasa, da se udio nikad ne cita bez velicine uzorka.
    """
    # notna() je tabela True/False; prosjek bool kolone je upravo udio True.
    # groupby prima Series (df["source"]), pa radi i nad tom True/False tabelom.
    popunjenost = df.notna().groupby(df["source"]).mean()

    # .T okrece tabelu: red = kolona podataka, kolona = izvor.
    # Tako se dva izvora citaju jedan pored drugog.
    rezultat = popunjenost.T

    # 'source' je po definiciji uvijek popunjen - nista ne govori
    rezultat = rezultat.drop(index="source", errors="ignore")

    rezultat.loc["n_oglasa"] = df["source"].value_counts()
    redoslijed = ["n_oglasa"] + [i for i in rezultat.index if i != "n_oglasa"]

    return rezultat.loc[redoslijed]


def jobs_by_city(df, min_n=5) -> pd.DataFrame:
    """Broj oglasa po gradu: city, n, udio. Grupe ispod min_n se izbacuju.

    Oglasi bez grada se ne bacaju nego se prikazu kao 'nepoznato' - inace
    udjeli ne daju 100% i ispada da trziste ima manje oglasa nego sto ima.
    """
    # value_counts broji koliko puta se javlja svaka vrijednost.
    # dropna=False da 81 oglas bez grada ne nestane iz tabele.
    brojevi = df["city"].fillna("nepoznato").value_counts(dropna=False)

    # value_counts vraca Series (grad je indeks) - reset_index ga pretvara
    # u obicnu tabelu sa kolonama city i n
    rezultat = brojevi.rename_axis("city").reset_index(name="n")

    # udio se racuna od SVIH oglasa, prije odsijecanja malih gradova
    rezultat["udio"] = rezultat["n"] / len(df)

    rezultat = rezultat[rezultat["n"] >= min_n]

    return rezultat.reset_index(drop=True)


def jobs_by_region(df) -> pd.DataFrame:
    """Broj oglasa po pokrajini.

    235 oglasa nema pokrajinu - prikazi ih kao 'nepoznato', nemoj ih tiho
    izbaciti, jer onda udjeli ne daju 100%.
    """
    brojevi = df["region"].fillna("nepoznato").value_counts(dropna=False)

    # dok je Series, 'brojevi' nema kolone - reset_index ga pretvara u tabelu
    # sa kolonama region i n, i tek onda se moze dodati kolona udio
    rezultat = brojevi.rename_axis("region").reset_index(name="n")
    rezultat["udio"] = rezultat["n"] / len(df)

    return rezultat


def top_companies(df, n=15) -> pd.DataFrame:
    """Firme sa najvise oglasa: company_name, n, broj_gradova.

    n je koliko firmi vratiti, ne prag broja oglasa.

    broj_gradova razdvaja dvije razlicite vrste poslodavca: 14 oglasa u
    jednom gradu je firma koja stvarno zaposljava, 14 oglasa u 8 gradova
    je konsultantska kuca koja isti posao objavljuje svuda.
    """
    # value_counts ne moze ovdje jer trebaju DVIJE racunice nad grupom -
    # broj oglasa i broj razlicitih gradova. Zato groupby + agg.
    rezultat = (
        df.groupby(df["company_name"].fillna("nepoznato"))
        .agg(
            n=("company_name", "size"),        # size broji redove u grupi
            broj_gradova=("city", "nunique"),  # nunique broji razlicite vrijednosti
        )
        .reset_index()
    )

    # nlargest je sortiranje + odsijecanje u jednom, umjesto
    # sort_values(...).head(n)
    return rezultat.nlargest(n, "n").reset_index(drop=True)


def jobs_over_time(df, freq="W") -> pd.DataFrame:
    """Broj oglasa kroz vrijeme, razdvojen po izvoru.

    Razdvajanje je obavezno: skok u avgustu je mozda samo dan kad si
    povukao podatke, a ne stvarni skok traznje.

    freq: 'D' dnevno, 'W' sedmicno, 'M' mjesecno, 'Q' kvartalno.
    (to_period trazi 'M'; 'ME' je oznaka za resample i ovdje puca.)

    Vraca jedan red po periodu, kolonu po izvoru, plus kolonu ukupno.
    """
    datumi = pd.to_datetime(df["posted_at"], utc=True)

    # to_period svodi razlicite datume na isti period (svi datumi iz jedne
    # sedmice postaju ista vrijednost), start_time ga vraca u obican datum
    # jer se Period ne moze poslati kao JSON ni nacrtati na osi.
    period = datumi.dt.tz_localize(None).dt.to_period(freq).dt.start_time

    # groupby sa dva kljuca daje Series sa dvonivoskim indeksom
    # (period, source) - jedan red po kombinaciji
    po_periodu = (
        pd.DataFrame({"period": period, "source": df["source"]})
        .groupby(["period", "source"])
        .size()
    )

    # unstack drugi nivo indeksa pretvara u kolone: red = period,
    # kolona = izvor. fill_value=0 jer 'nema oglasa' je 0, ne NaN.
    rezultat = po_periodu.unstack("source", fill_value=0)

    # axis=1 znaci saberi po redu (kroz kolone), ne niz kolonu
    rezultat["ukupno"] = rezultat.sum(axis=1)

    return rezultat.reset_index()


def remote_breakdown(df) -> pd.DataFrame:
    """Onsite / hybrid / remote.

    Racuna se samo nad izvorima koji to polje uopste imaju. Adzunino
    prazno znaci 'ne znamo', a ne 'nije remote' - da se broji zajedno,
    ispalo bi da 58% oglasa nije remote, sto je izmisljotina.

    Kolona osnova_n kaze nad koliko oglasa je udio racunat, da se broj
    nikad ne cita kao udio cijelog trzista.
    """
    # count() broji samo neprazne vrijednosti, pa izvor sa nulom
    # ocito nema to polje. Bolje nego hardkodirati 'karriere_at' -
    # kad dodas treci izvor, ovo radi samo od sebe.
    popunjenost = df.groupby("source")["remote_option"].count()
    izvori_sa_poljem = popunjenost[popunjenost > 0].index

    podskup = df[df["source"].isin(izvori_sa_poljem)]

    brojevi = podskup["remote_option"].fillna("nije navedeno").value_counts()
    rezultat = brojevi.rename_axis("remote_option").reset_index(name="n")

    rezultat["udio"] = rezultat["n"] / len(podskup)
    rezultat["osnova_n"] = len(podskup)

    return rezultat


def employment_breakdown(df) -> pd.DataFrame:
    """Full-time / part-time / internship / apprenticeship, sa udjelima.

    Za razliku od remote_option, ovo polje imaju oba izvora (Adzuna ga
    ima na 41% oglasa), pa se racuna nad svima. Prazno je zasebna
    kategorija, nije izostavljeno.
    """
    brojevi = (
        df["employment_type_norm"].fillna("nije navedeno").value_counts(dropna=False)
    )

    rezultat = brojevi.rename_axis("employment_type").reset_index(name="n")
    rezultat["udio"] = rezultat["n"] / len(df)

    return rezultat


def title_keywords(df, keywords, min_n=5) -> pd.DataFrame:
    """Koliko oglasa spominje koju tehnologiju u naslovu: keyword, n, udio.

    Trazi po granicama rijeci, da 'java' ne uhvati 'JavaScript'. Umjesto
    \\b koristi se (?<!\\w) i (?!\\w) jer \\b ne radi uz znakove kao u
    'C++' i 'C#' - iza plusa nema granice rijeci.

    Naslovi su kratki, pa su brojevi mali: naslov rijetko nabraja
    tehnologije. Za pravu sliku traznje isto ovo treba pustiti nad
    description, i to tek kad Faza 4 sredi vadjenje vjestina.
    """
    naslovi = df["title"].fillna("")

    redovi = []
    for rijec in keywords:
        # re.escape jer '+' i '.' u 'C++' i '.NET' inace znace nesto u regexu
        sablon = r"(?<!\w)" + re.escape(rijec) + r"(?!\w)"
        n = naslovi.str.contains(sablon, case=False, regex=True).sum()
        redovi.append({"keyword": rijec, "n": int(n)})

    rezultat = pd.DataFrame(redovi)
    rezultat["udio"] = rezultat["n"] / len(df)

    rezultat = rezultat[rezultat["n"] >= min_n]

    return rezultat.sort_values("n", ascending=False).reset_index(drop=True)
