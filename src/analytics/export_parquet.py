import json

from pathlib import Path

import polars as pl

from src.load.postgres import get_connection


def export_repositories(df):
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "repositories.parquet"

    df.write_parquet(output_file)

    print(f"Repositories exported to {output_file}")

    return output_file


def export_snapshots():
    query = """
        SELECT
            r.id AS repository_id,
            r.github_id,
            r.full_name,
            s.collected_at,
            s.stars,
            s.forks,
            s.open_issues
        FROM repository_snapshots s
        JOIN repositories r
            ON r.id = s.repository_id
        ORDER BY s.collected_at
    """

    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)

            rows = cursor.fetchall()

            columns = [
                "repository_id",
                "github_id",
                "full_name",
                "collected_at",
                "stars",
                "forks",
                "open_issues",
            ]

    df = pl.DataFrame(
        rows,
        schema=columns,
        orient="row",
    )

    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "repositories_snapshots.parquet"

    df.write_parquet(output_file)

    print(f"Snapshots exported to {output_file}")

    return output_file

# if __name__ == "__main__":

#     raw_files = sorted(
#         Path("data/raw").glob("repositories_*.json")
#     )

#     latest_file = raw_files[-1]

#     with open(latest_file, "r", encoding="utf-8") as file:
#         repositories = json.load(file)

#     df = transform_repositories(repositories)

#     export_repositories(df)

if __name__ == "__main__":
    export_snapshots()