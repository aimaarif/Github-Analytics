import polars as pl


import polars as pl


def transform_repositories(repositories):
    rows = []

    for repo in repositories:
        rows.append({
            "github_id": repo["id"],
            "name": repo["name"],
            "full_name": repo["full_name"],
            "owner": repo["owner"]["login"],
            "description": repo["description"],
            "language": repo["language"],
            "stars": repo["stargazers_count"],
            "forks": repo["forks_count"],
            "open_issues": repo["open_issues_count"],
            "created_at": repo["created_at"],
            "updated_at": repo["updated_at"],
        })

    df = pl.DataFrame(rows)

    df = df.with_columns(
    pl.col("created_at").str.to_datetime(
        "%Y-%m-%dT%H:%M:%SZ",
        strict=False,
        time_zone="UTC",
    ),
    pl.col("updated_at").str.to_datetime(
        "%Y-%m-%dT%H:%M:%SZ",
        strict=False,
        time_zone="UTC",
    ),
)

    df = df.with_columns(
        pl.col("description").fill_null("No description"),
        pl.col("language").fill_null("Unknown"),
    )

    return df

if __name__ == "__main__":
    import json
    from pathlib import Path

    from src.validation.checks import validate_repositories

    raw_files = sorted(
        Path("data/raw").glob("repositories_*.json")
    )

    latest_file = raw_files[-1]

    with open(latest_file, "r", encoding="utf-8") as file:
        repositories = json.load(file)

    df = transform_repositories(repositories)

    print(df)
    print("\nShape:")
    print(df.shape)

    validate_repositories(df)