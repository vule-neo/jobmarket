from apify_client import ApifyClient
import dotenv
import os
import sys
import json

dotenv.load_dotenv()
APIFY_API_KEY=os.getenv("APIFY_API_KEY")

client = ApifyClient(APIFY_API_KEY)

actor_id = "santamaria-automations/karriere-at-scraper"

# cijene actora: start $0.001, oglas sa detaljima $0.005
PRICE_START = 0.001
PRICE_JOB_WITH_DETAILS = 0.005


def probe_karriere_at(max_results=20, max_per_query=10):
    """Jedan jeftin testni run da vidimo kakve podatke actor vraca.

    Svih 9 pojmova ide u JEDAN run - actor dedupira rezultate izmedju upita,
    pa isti oglas ne placamo pod svakim pojmom pod kojim se pojavi.
    maxResults je tvrdi cap i jedina stvar koja stoji izmedju nas i $4.50 racuna.
    """
    search_phrases = ["data science", "data engineer", "ai engineer", "java", "java developer", "springboot", "angular", "python", "data analyst"]
    params = {
        "searchQueries": search_phrases,
        "location": "wien",
        "sortBy": "date",
        "includeJobDetails": True,
        "maxResultsPerQuery": max_per_query,
        "maxResults": max_results,
    }

    run = client.actor(actor_id).call(run_input=params)
    return save_run_items(run)


def fetch_existing_run(run_id):
    """Preuzmi rezultate runa koji je vec placen - ne kosta nista dodatno."""
    run = client.run(run_id).get()
    if run is None:
        raise RuntimeError(f"Run {run_id} ne postoji")
    return save_run_items(run)


def save_run_items(run):
    # Run je pydantic model, ne dict - atributi su snake_case
    # neuspio run vraca prazan dataset, ne damo mu da prepise dobre podatke
    if run.status != "SUCCEEDED":
        raise RuntimeError(f"Run nije uspio, status: {run.status} (run id: {run.id})")

    items = list(client.dataset(run.default_dataset_id).iterate_items())

    os.makedirs("data/apify", exist_ok=True)
    with open("data/apify/probe.json", "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    print(f"Run {run.id} SUCCEEDED, {len(items)} oglasa -> data/apify/probe.json")
    if run.usage_total_usd is not None:
        print(f"Stvarni trosak runa: ${run.usage_total_usd:.4f}")
    return items


if __name__ == "__main__":
    # --run <id> preuzima vec placen run, bez novog troska
    if "--run" in sys.argv:
        fetch_existing_run(sys.argv[sys.argv.index("--run") + 1])
        sys.exit(0)

    max_results = 20
    cost = PRICE_START + max_results * PRICE_JOB_WITH_DETAILS
    if "--yes" not in sys.argv:
        print(f"Ovo je PLACEN poziv. Procijenjeni trosak: ${cost:.3f} (do {max_results} oglasa).")
        print("Pokreni sa --yes ako si siguran.")
        sys.exit(1)
    probe_karriere_at(max_results=max_results)
