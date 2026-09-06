from collections import defaultdict
from decimal import Decimal
import re

from sqlalchemy import select

from src.db.models import Job, Location
from src.db.session import SessionLocal

bezirke = [
    "Innere Stadt",
    "Leopoldstadt",
    "Landstraße",
    "Wieden",
    "Margareten",
    "Mariahilf",
    "Neubau",
    "Josefstadt",
    "Alsergrund",
    "Favoriten",
    "Simmering",
    "Meidling",
    "Hietzing",
    "Penzing",
    "Rudolfsheim-Fünfhaus",
    "Ottakring",
    "Hernals",
    "Währing",
    "Döbling",
    "Brigittenau",
    "Floridsdorf",
    "Donaustadt",
    "Liesing",
]

# devet saveznih pokrajina - area[1] je uvijek jedna od njih
pokrajine = {
    "Burgenland",
    "Kärnten",
    "Niederösterreich",
    "Oberösterreich",
    "Salzburg",
    "Steiermark",
    "Tirol",
    "Vorarlberg",
    "Wien",
}

# Wien i Salzburg su i grad i pokrajina - te dvije ne odbacujemo kao "nije grad"
samo_pokrajine = pokrajine - {"Wien", "Salzburg"}

# (?!...Umgebung) jer 'Wien-Umgebung' je okrug u Nizoj Austriji, ne Bec.
# \bWien\b ne hvata 'Wiener Neudorf' - iza 'Wien' dolazi slovo, nema granice.
wien_re = r"\bWien\b(?!\s*-?\s*Umgebung)"
# becki postanski brojevi su cetverocifreni: 1010-1230, uvijek 1XX0
wien_postanski_re = r"\b1\d{2}0\b"

# 'Wien, Österreich' -> 'Wien';  '1020 Wien' -> 'Wien'
postanski_prefiks_re = r"^\d{4}\s+"


def _je_bec(display_name, area):
    """Bec se prepoznaje po pokrajini, a tek onda po tekstu.

    area[1] == 'Wien' pokriva sva 23 kvarta odjednom - zato se
    'Schwechat, Wien-Umgebung' (pokrajina Niederösterreich) ne uhvati.
    """
    if len(area) >= 2 and area[1] == "Wien":
        return True

    # bez area (karriere.at) - ostaje tekst
    if display_name in bezirke:
        return True
    if re.search(wien_re, display_name, re.IGNORECASE):
        return True
    if re.search(wien_postanski_re, display_name):
        return True

    return False


def normalize_city(display_name, area):
    """'Innere Stadt, Wien' -> 'Wien', 'Graz, Steiermark' -> 'Graz'.

    Vraca None kad grad ne postoji ('Österreich' je drzava, ne grad) -
    radije prazno nego izmisljeno.
    """
    if not display_name:
        return None
    area = area or []

    if _je_bec(display_name, area):
        return "Wien"

    # area ide od opsteg ka konkretnom: [drzava, pokrajina, okrug, mjesto].
    # Zadnji element je najkonkretniji, ali samo ako je ispod pokrajine -
    # ['Österreich', 'Tirol'] nema grad.
    if len(area) >= 3:
        return area[-1]

    # bez upotrebljive area - prvi dio prije zareza
    grad = display_name.split(",")[0].strip()
    grad = re.sub(postanski_prefiks_re, "", grad)

    if not grad or grad == "Österreich" or grad in samo_pokrajine:
        return None

    return grad


def normalize_region(display_name, area):
    """'Graz, Steiermark' -> 'Steiermark'. Vraca None kad se ne moze utvrditi."""
    if not display_name:
        return None
    area = area or []

    # area[0] je uvijek 'Österreich', area[1] je pokrajina
    if len(area) >= 2 and area[1] in pokrajine:
        return area[1]

    # bez area - trazi se ime pokrajine bilo gdje u display_name
    for dio in display_name.split(","):
        dio = dio.strip()
        if dio in pokrajine:
            return dio

    # 'Wien' i '1020 Wien' su i grad i pokrajina
    if _je_bec(display_name, area):
        return "Wien"

    return None




# ---------------------------------------------------------------- plate

# U Austriji se plata isplacuje 14 puta godisnje (13. i 14. su Urlaubs-
# i Weihnachtsgeld). Mjesecni iznos * 12 bi potcijenio godisnji.
ISPLATA_GODISNJE = 14

# Ispod ovog iznosa "godisnja" plata nije godisnja - Adzuna svemu lijepi
# 'yearly', pa nam tu upadnu satnice (50) i mjesecni iznosi (2080).
# Kolektivni ugovori u IT-u ne idu ispod ~30k, pa je 15k siguran prag.
MIN_GODISNJA = Decimal("15000")


def to_yearly(iznos, period):
    """Svede platu na godisnji nivo da bi se iznosi smjeli porediti.

    Bez poznatog perioda vraca None - ne pogadja se.
    """
    if iznos is None or not period:
        return None

    p = period.strip().lower()
    if p == "yearly":
        return Decimal(iznos)
    if p == "monthly":
        return Decimal(iznos) * ISPLATA_GODISNJE

    return None


# ------------------------------------------------------- tip zaposlenja

# lijeva strana je uvijek na mala slova sa '-' pretvorenim u '_'
zaposlenje_mapa = {
    "full_time": "full_time",
    "fulltime": "full_time",
    "vollzeit": "full_time",
    "part_time": "part_time",
    "parttime": "part_time",
    "teilzeit": "part_time",
    "geringfugig": "part_time",
    "internship": "internship",
    "praktikum": "internship",
    "contract": "contract",
    "freelance": "contract",
    "werkvertrag": "contract",
}


def normalize_employment(vrijednost):
    """'full-time', 'Vollzeit', 'full_time' -> 'full_time'.

    Nepoznat oblik vraca None umjesto da ga propusti dalje neociscenog -
    tako se u statistici odmah vidi da ga treba dodati u mapu.
    """
    if not vrijednost:
        return None

    kljuc = vrijednost.strip().lower().replace("-", "_").replace(" ", "_")
    kljuc = kljuc.replace("ü", "u").replace("ä", "a").replace("ö", "o")

    return zaposlenje_mapa.get(kljuc)


# ------------------------------------------------------------ duplikati

# '(m/w/d)', '(w/m/x)', '(m/f/d)' - isti posao, razlicito pisan rodni dodatak
rodni_dodatak_re = r"\(\s*[mwfdxa](?:\s*[/|]\s*[mwfdxa])+\s*\)"


def job_fingerprint(title, company_id):
    """Kljuc po kojem se prepoznaje isti oglas objavljen vise puta.

    Lokacija namjerno NIJE u otisku: Adzuna istom oglasu daje razlicitu
    granularnost ('Innere Stadt, Wien' i 'Wien, Österreich' su isti Bec),
    pa bi poredjenje po lokaciji razdvojilo 35 od 39 stvarnih grupa.
    """
    if not title or not company_id:
        return None

    t = title.lower()
    t = re.sub(rodni_dodatak_re, " ", t)
    t = re.sub(r"[^\w\s]", " ", t)      # interpunkcija i crtice
    t = re.sub(r"\s+", " ", t).strip()

    if not t:
        return None

    return f"{t}|{company_id}"


# ----------------------------------------------------------- koraci nad bazom


def normalize_locations(session):
    """Popuni Location.city i Location.region. Vraca broj izmijenjenih."""
    izmijenjeno = 0

    for lokacija in session.execute(select(Location)).scalars():
        grad = normalize_city(lokacija.display_name, lokacija.area)
        pokrajina = normalize_region(lokacija.display_name, lokacija.area)

        if lokacija.city != grad or lokacija.region != pokrajina:
            lokacija.city = grad
            lokacija.region = pokrajina
            izmijenjeno += 1

    return izmijenjeno


def normalize_jobs(session):
    """Popuni salary_*_yearly i employment_type_norm. Vraca broj izmijenjenih."""
    izmijenjeno = 0
    odbaceno = 0

    for oglas in session.execute(select(Job)).scalars():
        min_god = to_yearly(oglas.salary_min, oglas.salary_period)
        max_god = to_yearly(oglas.salary_max, oglas.salary_period)

        # oznaceno kao godisnje, a iznos je ocito satnica ili mjesecna plata:
        # radije prazno nego pogresan broj u statistici
        if min_god is not None and min_god < MIN_GODISNJA:
            min_god = max_god = None
            odbaceno += 1

        tip = normalize_employment(oglas.employment_type)

        if (oglas.salary_min_yearly != min_god
                or oglas.salary_max_yearly != max_god
                or oglas.employment_type_norm != tip):
            oglas.salary_min_yearly = min_god
            oglas.salary_max_yearly = max_god
            oglas.employment_type_norm = tip
            izmijenjeno += 1

    if odbaceno:
        print(f"  (odbaceno {odbaceno} nevjerodostojnih plata ispod {MIN_GODISNJA})")

    return izmijenjeno


def mark_duplicates(session):
    """Grupise oglase po otisku i oznaci ponovljene.

    U svakoj grupi najstariji ostaje glavni, ostali dobiju duplicate_of =
    source_job_id glavnog. Nista se ne brise - duplikati se samo filtriraju
    u analizi (WHERE duplicate_of IS NULL).
    """
    grupe = defaultdict(list)

    for oglas in session.execute(select(Job)).scalars():
        # ponovno pokretanje mora dati isti rezultat, pa se stare oznake brisu
        oglas.duplicate_of = None

        otisak = job_fingerprint(oglas.title, oglas.company_id)
        if otisak:
            grupe[otisak].append(oglas)

    oznaceno = 0
    for oglasi in grupe.values():
        if len(oglasi) < 2:
            continue

        # najstariji je original; id je rezerva kad su datumi isti
        oglasi.sort(key=lambda o: (o.posted_at, o.id))
        glavni, ponovljeni = oglasi[0], oglasi[1:]

        for oglas in ponovljeni:
            oglas.duplicate_of = glavni.source_job_id
            oznaceno += 1

    return oznaceno


def main():
    with SessionLocal() as session:
        print("normalizacija lokacija...")
        n_lok = normalize_locations(session)
        print("normalizacija oglasa...")
        n_job = normalize_jobs(session)
        print("trazenje duplikata...")
        n_dup = mark_duplicates(session)

        # jedan commit na kraju: ili prodje cijela normalizacija, ili nista
        session.commit()

        print("\nizmijenjeno:")
        print(f"  lokacija          {n_lok}")
        print(f"  oglasa            {n_job}")
        print(f"  oznaceno duplikata {n_dup}")


if __name__ == "__main__":
    main()
