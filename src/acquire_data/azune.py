import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY")

url = "https://api.adzuna.com/v1/api/jobs/at/search/1"
url_hist_avg = "https://api.adzuna.com/v1/api/jobs/at/history"
url_histogram = "https://api.adzuna.com/v1/api/jobs/at/histogram"

def load_all_adzuna():
    os.makedirs("data/azune", exist_ok=True)
    search_phrases = ["data science", "data engineer", "ai engineer", "java", "java developer", "springboot", "angular", "python", "data analyst"]
    for phrase in search_phrases:
        params = {
            "app_id": f'{ADZUNA_APP_ID}',
            "app_key": ADZUNA_API_KEY,
            "results_per_page": 50,
            "what_phrase": phrase,
            "what_exclude": "senior lead",
        }
        response = requests.get(url, params)
        with open(f"data/azune/{phrase.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)


def historical_avg():
    os.makedirs("data/azune", exist_ok=True)

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
    }
    response = requests.get(url_hist_avg, params)
    with open(f"data/historical_avg/avg_hist.json", "w", encoding="utf-8") as f:
        data = response.json()
        sortedm = dict(sorted(data["month"].items()))
        json.dump(sortedm, f, indent=2, ensure_ascii=False)


def histogram_salary():
    os.makedirs("data/azune", exist_ok=True)
    search_phrases = ["data science", "data engineer", "ai engineer", "java", "java developer", "springboot", "angular", "python", "data analyst"]
    for phrase in search_phrases:
        params = {
            "app_id": f'{ADZUNA_APP_ID}',
            "app_key": ADZUNA_API_KEY,
            "what": phrase,
        }
        response = requests.get(url_histogram, params)
        with open(f"data/histogram/{phrase.replace(' ', '_')}.json", "w", encoding="utf-8") as f:
            json.dump(response.json(), f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    histogram_salary()