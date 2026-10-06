
import logging
from datetime import datetime
from pathlib import Path

from src.extract.github_api import (
    SEARCH_QUERIES,
    discover_repositories,
    deduplicate_repositories,
    save_raw_data,
)
from src.transform.repositories import transform_repositories
from src.validation.checks import validate_repositories
from src.load.postgres import (
    create_tables,
    load_repositories,
    create_snapshots,
)
from src.analytics.export_parquet import (
    export_repositories,
    export_snapshots,
)
from src.analytics.duckdb_queries import (
    top_repositories,
    repositories_by_language,
)


# Configure logging
Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("logs/pipeline.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

logger = logging.getLogger(__name__)


def run_pipeline():
    start_time = datetime.now()

    try:
        logger.info("ETL pipeline started")

        # 1. Extract
        repositories = discover_repositories(
            SEARCH_QUERIES,
            max_pages=2,
        )

        unique_repositories = deduplicate_repositories(
            repositories
        )

        logger.info(
            "Extracted %s results; %s unique repositories",
            len(repositories),
            len(unique_repositories),
        )

        if not unique_repositories:
            raise ValueError("No repositories were extracted")

        # 2. Save raw data
        raw_file = save_raw_data(unique_repositories)
        logger.info("Raw data saved to %s", raw_file)

        # 3. Transform
        df = transform_repositories(unique_repositories)
        logger.info("Transformed DataFrame shape: %s", df.shape)

        # 4. Validate
        validate_repositories(df)
        logger.info("Validation completed")

        # 5. Create database tables if needed
        create_tables()

        # 6. Load current repository data
        load_repositories(df)

        # 7. Record historical snapshots
        create_snapshots(df)

        # 8. Export Parquet files
        export_repositories(df)
        export_snapshots()

        # 9. Run analytics
        logger.info("Top repositories by stars:")
        for row in top_repositories():
            logger.info("%s", row)

        logger.info("Repository counts by language:")
        for row in repositories_by_language():
            logger.info("%s", row)

        elapsed = datetime.now() - start_time
        logger.info("ETL pipeline completed in %s", elapsed)

    except Exception:
        logger.exception("ETL pipeline failed")
        raise


if __name__ == "__main__":
    run_pipeline()