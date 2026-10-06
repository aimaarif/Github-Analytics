import duckdb

def get_connection():
    return duckdb.connect("data/github.duckdb")

def top_repositories():
    connection = get_connection()

    result = connection.execute(
        """
        SELECT
            full_name,
            language,
            stars,
            forks
        FROM 'data/processed/repositories.parquet'
        ORDER BY stars DESC
        LIMIT 10
        """
    ).fetchall()

    connection.close()

    return result

def repositories_by_language():
    connection = get_connection()

    result = connection.execute(
        """
        SELECT
            language,
            COUNT(*) AS repository_count,
            ROUND(AVG(stars), 0) AS average_stars,
            MAX(stars) AS maximum_stars
        FROM 'data/processed/repositories.parquet'
        WHERE language != 'Unknown'
        GROUP BY language
        ORDER BY repository_count DESC
        """
    ).fetchall()

    connection.close()

    return result

def snapshot_count():
    connection = get_connection()

    result = connection.execute(
        """
        SELECT COUNT(*)
        FROM 'data/processed/repositories_snapshots.parquet'
        """
    ).fetchone()

    connection.close()

    return result[0]

def repository_growth():
    connection = get_connection()

    result = connection.execute(
        """
        WITH first_snapshot AS (
            SELECT
                github_id,
                full_name,
                stars,
                collected_at,
                ROW_NUMBER() OVER (
                    PARTITION BY github_id
                    ORDER BY collected_at
                ) AS row_num
            FROM 'data/processed/repositories_snapshots.parquet'
        ),

        last_snapshot AS (
            SELECT
                github_id,
                stars,
                collected_at,
                ROW_NUMBER() OVER (
                    PARTITION BY github_id
                    ORDER BY collected_at DESC
                ) AS row_num
            FROM 'data/processed/repositories_snapshots.parquet'
        )

        SELECT
            f.full_name,
            f.stars AS first_stars,
            l.stars AS latest_stars,
            l.stars - f.stars AS star_growth
        FROM first_snapshot f
        JOIN last_snapshot l
            ON f.github_id = l.github_id
        WHERE f.row_num = 1
          AND l.row_num = 1
        ORDER BY star_growth DESC
        LIMIT 20
        """
    ).fetchall()

    connection.close()

    return result

if __name__ == "__main__":
    # print("\nTop repositories:")

    # for row in top_repositories():
    #     print(row)

    # print("\nRepositories by language:")

    # for row in repositories_by_language():
    #     print(row)

    # print(
    #     "Snapshot rows:",
    #     snapshot_count()
    # )

    print("\nRepository growth:")

    for row in repository_growth():
        print(row)