# AI Job Market Intelligence & Personal Job Assistant

Lični alat za analizu austrijskog IT tržišta rada. Trenutno stanje: **Phase 1 — prikupljanje podataka** sa Adzuna API-ja.

Puna specifikacija i razvojne faze projekta su u [CLAUDE.md](CLAUDE.md).

## Struktura

```
src/acquire_data/azune.py   # Adzuna API klijent (search, histogram, historical avg)
data/azune/                 # sirovi rezultati pretrage po pojmu
data/histogram/             # distribucija plata po pojmu
data/historical_avg/        # historijski prosjek plata po mjesecu
```

## Setup na novom računaru

```bash
git clone <URL-repoa>
cd jobmarket

python -m venv venv
# Windows PowerShell:
venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Zatim kopiraj `.env.example` u `.env` i popuni svoje Adzuna kredencijale
(registracija: https://developer.adzuna.com/):

```
ADZUNA_APP_ID=...
ADZUNA_API_KEY=...
```

`.env` je namjerno u `.gitignore` — kredencijali nikad ne idu u repo.

## Pokretanje

```bash
python -m src.acquire_data.azune
```

Skripta upisuje JSON fajlove u `data/`. Sirovi podaci se ne brišu i ne mijenjaju —
svako naredno procesiranje radi nad njima (vidi CLAUDE.md, sekcija 6).
