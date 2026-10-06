import os

import requests
from dotenv import load_dotenv
import json
from datetime import datetime
from pathlib import Path


load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}

SEARCH_QUERIES = [
    "language:Python stars:>5000",
    "language:JavaScript stars:>5000",
    "language:TypeScript stars:>5000",
    "topic:machine-learning stars:>5000",
    "topic:data-engineering stars:>1000",
]

def search_repositories(query, page=1, per_page=100):
    url = f"{BASE_URL}/search/repositories"

    params = {
        "q": query,
        "page": page,
        "per_page": per_page,
    }

    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()

def search_all_repositories(query, max_pages=2):
    repositories = []

    for page in range(1, max_pages + 1):
        data = search_repositories(
            query=query,
            page=page,
            per_page=100,
        )

        repositories.extend(data["items"])

        print(
            f"Page {page}: "
            f"{len(data['items'])} repositories retrieved"
        )

    return repositories

def discover_repositories(queries, max_pages=2):
    repositories = []

    for query in queries:
        print(f"\nSearching: {query}")

        results = search_all_repositories(
            query=query,
            max_pages=max_pages,
        )

        repositories.extend(results)

    return repositories

def deduplicate_repositories(repositories):
    unique_repositories = {}

    for repository in repositories:
        github_id = repository["id"]

        unique_repositories[github_id] = repository

    return list(unique_repositories.values())

def save_raw_data(repositories):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_path = output_dir / f"repositories_{timestamp}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            repositories,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return file_path

if __name__ == "__main__":
    repositories = discover_repositories(
        SEARCH_QUERIES,
        max_pages=2,
    )

    print(
        "\nTotal repositories before deduplication:",
        len(repositories)
    )

    unique_repositories = deduplicate_repositories(
        repositories
    )

    print(
        "Total repositories after deduplication:",
        len(unique_repositories)
    )

    file_path = save_raw_data(unique_repositories)

    print("\nRaw data saved to:", file_path)

