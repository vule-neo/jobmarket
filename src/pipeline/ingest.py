from datetime import datetime, timezone
from pathlib import Path
import json

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert

from src.db.models import Company, Job, Location, RawJob
from src.db.session import SessionLocal

def _parse_datetime(value):
    """Adzuna salje '2026-08-06T12:37:40Z', karriere.at salje '2026-08-27'.

    Kolona posted_at je timezone-aware, pa goli datum tumacimo kao ponoc UTC.
    """
    if not value:
        return None
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def adzune_adjust(adzune_dict):
    # '0'/'1' dolazi kao string, kolona je Boolean; ako polja nema -> ne znamo
    predicted = adzune_dict.get("salary_is_predicted")

    transformed_dict = {
        "source": "adzuna",
        "source_job_id": adzune_dict["id"],
        "title": adzune_dict["title"],
        "description": adzune_dict.get("description"),

        "salary_min": adzune_dict.get("salary_min"),
        "salary_max": adzune_dict.get("salary_max"),
        # Adzuna ne salje valutu ni period - izvedeno iz /jobs/at/ endpointa
        "salary_currency": "EUR",
        "salary_period": "yearly",
        "salary_is_predicted": None if predicted is None else predicted == "1",

        "employment_type": adzune_dict.get("contract_time"),
        "remote_option": None,
        "category_label": adzune_dict.get("category", {}).get("label"),
        "url": adzune_dict.get("redirect_url"),
        "posted_at": _parse_datetime(adzune_dict.get("created")),

        # ovo ne ide direktno u job - rjesava se preko get_or_create
        "company_name": adzune_dict.get("company", {}).get("display_name"),
        "location_display_name": adzune_dict.get("location", {}).get("display_name"),
        "location_area": adzune_dict.get("location", {}).get("area"),
        "latitude": adzune_dict.get("latitude"),
        "longitude": adzune_dict.get("longitude"),
    }
    return transformed_dict


def apify_adjust(apify_dict):
    transformed_dict = {
        "source": "karriere_at",
        "source_job_id": apify_dict["id"],
        "title": apify_dict["title"],
        # description_full, ne description_snippet - snippet je odsjecen
        "description": apify_dict.get("description_full"),

        "salary_min": apify_dict.get("salary_min"),
        "salary_max": apify_dict.get("salary_max"),
        "salary_currency": apify_dict.get("salary_currency"),
        "salary_period": apify_dict.get("salary_period"),
        "salary_is_predicted": None,

        "employment_type": apify_dict.get("employment_type"),
        "remote_option": apify_dict.get("remote_option"),
        "category_label": None,
        "url": apify_dict.get("source_url"),
        "posted_at": _parse_datetime(apify_dict.get("posted_at")),

        "company_name": apify_dict.get("company"),
        "location_display_name": apify_dict.get("location"),
        "location_area": None,
        "latitude": None,
        "longitude": None,
    }
    return transformed_dict


def load_adzuna_files():
    """Vraca listu parova (sirovi_oglas, pojam_pretrage)."""
    lista_oglasa = []
    for path in Path("data/azune").glob("*.json"):
        pojam = path.stem.replace("_", " ")

        with path.open(encoding="utf-8") as f:
            stranice = json.load(f)      # vrh fajla je LISTA stranica

        for stranica in stranice:
            for oglas in stranica.get("results", []):
                lista_oglasa.append((oglas, pojam))

    return lista_oglasa

def load_apify_file():
    """Vraca listu parova (sirovi_oglas, pojam_pretrage)."""
    lista_oglasa = []

    for path in Path("data/apify").glob("*.json"):
        with path.open(encoding="utf-8") as f:
            oglasi = json.load(f)      # obicna lista oglasa, bez omotaca

        for oglas in oglasi:
            lista_oglasa.append((oglas, oglas.get("search_query")))

    return lista_oglasa


def get_or_create_company(session, ime):
    if not ime:
        return None
    firma = session.execute(
        select(Company).where(Company.name == ime)
        ).scalar_one_or_none()
    if firma is not None:
        return firma.id

    firma = Company(name=ime)
    session.add(firma)
    session.flush()
    return firma.id


def get_or_create_location(session, podaci):
    ime = podaci.get("location_display_name")
    if not ime:
        return None

    lokacija = session.execute(
        select(Location).where(Location.display_name == ime)
        ).scalar_one_or_none()
    if lokacija is not None:
        # nadjena - ne diramo joj area/koordinate, vrijedi prvo vidjeno stanje
        return lokacija.id

    lokacija = Location(
        display_name=ime,
        area=podaci.get("location_area"),
        latitude=podaci.get("latitude"),
        longitude=podaci.get("longitude"),
    )
    session.add(lokacija)
    session.flush()
    return lokacija.id


def upsert_raw_job(session, source, source_job_id, payload, search_phrase):
    """Upisuje netaknuti oglas iz JSON-a. Ako vec postoji, osvjezi ga.

    Nema SELECT-a - provjeru radi baza kroz ON CONFLICT. Id nam ne treba
    nazad, pa nema ni flush().
    """
    stmt = insert(RawJob).values(
        source=source,
        source_job_id=source_job_id,
        payload=payload,
        search_phrase=search_phrase,
    )
    # sudar na (source, source_job_id) = ovaj oglas smo vec vidjeli
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "source_job_id"],
        set_={
            "payload": stmt.excluded.payload,
            "search_phrase": stmt.excluded.search_phrase,
            "fetched_at": func.now(),
        },
    )
    session.execute(stmt)


def upsert_job(session, podaci):
    """Upisuje normalizovan oglas.

    Pet kljuceva iz adaptera nisu kolone u job tabeli - zamjenjuju se
    brojevima koje vrate get_or_create funkcije.
    """
    vrijednosti = dict(podaci)   # kopija, original ostaje netaknut za main()

    # prvo brojevi, tek onda upis - job.company_id je strani kljuc
    vrijednosti["company_id"] = get_or_create_company(
        session, vrijednosti.pop("company_name")
    )
    vrijednosti["location_id"] = get_or_create_location(session, podaci)

    for kljuc in ("location_display_name", "location_area", "latitude", "longitude"):
        vrijednosti.pop(kljuc)

    stmt = insert(Job).values(**vrijednosti)
    # source i source_job_id su kljuc sudara - njih ne mijenjamo.
    # ingested_at izostavljen namjerno: ostaje kad smo oglas PRVI put vidjeli.
    stmt = stmt.on_conflict_do_update(
        index_elements=["source", "source_job_id"],
        set_={
            k: stmt.excluded[k]
            for k in vrijednosti
            if k not in ("source", "source_job_id")
        },
    )
    session.execute(stmt)


def main():
    adzuna = load_adzuna_files()
    apify = load_apify_file()
    print(f"ucitano: {len(adzuna)} adzuna + {len(apify)} karriere.at zapisa")

    with SessionLocal() as session:
        for oglas, pojam in adzuna:
            upsert_raw_job(session, "adzuna", oglas["id"], oglas, pojam)
            upsert_job(session, adzune_adjust(oglas))

        for oglas, pojam in apify:
            upsert_raw_job(session, "karriere_at", oglas["id"], oglas, pojam)
            upsert_job(session, apify_adjust(oglas))

        # jedan commit na kraju: sve ili nista.
        # u petlji bi bilo 900+ transakcija i gubis atomicnost.
        session.commit()

        print("upisano u bazu:")
        for model in (RawJob, Job, Company, Location):
            n = session.execute(select(func.count()).select_from(model)).scalar()
            print(f"  {model.__tablename__:10} {n}")


if __name__ == "__main__":
    main()
