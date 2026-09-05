# AI Job Market Intelligence & Personal Job Assistant

Lični alat za analizu austrijskog IT tržišta rada.

Trenutno stanje: **Phase 1** — prikupljanje podataka radi, shema baze postoji, ingestion u izradi.

Puna specifikacija i razvojne faze su u [CLAUDE.md](CLAUDE.md).

## Struktura

```
src/config.py                # citanje .env preko pydantic-settings
src/db/session.py            # SQLAlchemy engine + fabrika sesija
src/db/models.py             # tabele: company, location, raw_job, job
src/acquire_data/azune.py    # Adzuna API (search, histogram, historical avg)
src/acquire_data/apify.py    # karriere.at preko Apify actora (PLACA SE)
src/pipeline/ingest.py       # JSON -> baza (u izradi)
alembic/                     # migracije sheme baze

data/azune/                  # sirovi Adzuna rezultati, 445 unikatnih oglasa
data/apify/probe.json        # karriere.at uzorak, 20 oglasa
data/histogram/              # Adzunina distribucija plata po pojmu
data/historical_avg/         # Adzunin mjesecni prosjek plata
```

## Izvori podataka

| | Adzuna | karriere.at (Apify) |
|---|---|---|
| Cijena | besplatno | **$0.003 po oglasu** |
| Duzina opisa | 500 znakova (odsjeceno) | ~4200 znakova |
| Ima platu | 35% | 100% |
| Tip zaposlenja | 9% | 100% |

## Setup na novom računaru

**1. Kod i okruženje**

```bash
git clone https://github.com/vule-neo/jobmarket.git
cd jobmarket

python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
source venv/bin/activate         # Linux/macOS

pip install -r requirements.txt
```

**2. PostgreSQL**

Instaliraj PostgreSQL 18, pa kreiraj praznu bazu (pgAdmin: desni klik na *Databases* → *Create* → *Database*):

```sql
CREATE DATABASE jobmarket;
```

**3. Kredencijali**

Kopiraj `.env.example` u `.env` i popuni. Trebaju ti Adzuna nalog
(https://developer.adzuna.com/), Apify token
(https://console.apify.com/account/integrations) i lozinka `postgres` korisnika.

`.env` je u `.gitignore` — kredencijali nikad ne idu u repo.

**4. Shema baze**

```bash
alembic upgrade head
```

Ovo napravi tabele. Ne pravi ih ručno u pgAdminu — shema se mijenja samo kroz migracije,
da bi ostala ista na svim mašinama.

Provjera da je prošlo:

```bash
python -c "from src.db.session import engine; from sqlalchemy import text; print(engine.connect().execute(text('select count(*) from job')).scalar())"
```

## Pokretanje

**Adzuna** (besplatno):

```bash
python -m src.acquire_data.azune
```

**karriere.at preko Apify** — ⚠️ **ovo troši novac**. Skripta bez `--yes` samo ispiše
procjenu troška i izađe:

```bash
python -m src.acquire_data.apify           # samo procjena, ne trosi nista
python -m src.acquire_data.apify --yes     # stvarno pokrece, ~$0.10
python -m src.acquire_data.apify --run <ID>  # preuzme vec placen run, besplatno
```

Sirovi podaci se ne brišu i ne mijenjaju — svako naredno procesiranje radi nad njima
(CLAUDE.md, sekcija 6).
