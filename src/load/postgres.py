import os
import json
import psycopg
from dotenv import load_dotenv
from pathlib import Path
from src.transform.repositories import transform_repositories
from datetime import datetime, timezone

load_dotenv()


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

def create_tables():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            with open("sql/schema.sql", "r", encoding="utf-8") as file:
                schema = file.read()

            cursor.execute(schema)

        connection.commit()

    print("Tables created successfully.")

def load_repositories(df):
    with get_connection() as connection:
        with connection.cursor() as cursor:

            for row in df.iter_rows(named=True):
                cursor.execute(
                    """
                    INSERT INTO repositories (
                        github_id,
                        name,
                        full_name,
                        owner,
                        description,
                        language,
                        stars,
                        forks,
                        open_issues,
                        created_at,
                        updated_at
                    )
                    VALUES (
                        %(github_id)s,
                        %(name)s,
                        %(full_name)s,
                        %(owner)s,
                        %(description)s,
                        %(language)s,
                        %(stars)s,
                        %(forks)s,
                        %(open_issues)s,
                        %(created_at)s,
                        %(updated_at)s
                    )
                    ON CONFLICT (github_id)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        full_name = EXCLUDED.full_name,
                        owner = EXCLUDED.owner,
                        description = EXCLUDED.description,
                        language = EXCLUDED.language,
                        stars = EXCLUDED.stars,
                        forks = EXCLUDED.forks,
                        open_issues = EXCLUDED.open_issues,
                        updated_at = EXCLUDED.updated_at;
                    """,
                    row,
                )

        connection.commit()

    print(f"{len(df)} repositories loaded.")

def create_snapshots(df):
    collected_at = datetime.now(timezone.utc)
    snapshot_date = collected_at.date()
    inserted_count = 0

    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in df.iter_rows(named=True):
                cur.execute(
                    """
                    INSERT INTO repository_snapshots (
                        repository_id,
                        snapshot_date,
                        collected_at,
                        stars,
                        forks,
                        open_issues
                    )
                    SELECT
                        id,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    FROM repositories
                    WHERE github_id = %s
                    ON CONFLICT (repository_id, snapshot_date)
                    DO NOTHING
                    """,
                    (
                        snapshot_date,
                        collected_at,
                        row["stars"],
                        row["forks"],
                        row["open_issues"],
                        row["github_id"],
                    ),
                )

                inserted_count += cur.rowcount

    print(
        f"{inserted_count} new snapshots created; "
        f"{df.height - inserted_count} existing daily snapshots skipped."
    )

    return inserted_count

if __name__ == "__main__":
    create_tables()

    # raw_files = sorted(
    #     Path("data/raw").glob("repositories_*.json")
    # )

    # latest_file = raw_files[-1]

    # with open(latest_file, "r", encoding="utf-8") as file:
    #     repositories = json.load(file)

    # df = transform_repositories(repositories)

    # load_repositories(df)

    # create_snapshots(df)