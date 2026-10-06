import pytest
import polars as pl

from src.validation.checks import validate_repositories


def valid_dataframe():
    return pl.DataFrame({
        "github_id": [1, 2],
        "full_name": ["example/one", "example/two"],
        "stars": [100, 200],
        "forks": [10, 20],
        "open_issues": [5, 8],
    })


def test_valid_data_passes():
    df = valid_dataframe()

    # Should not raise an exception.
    validate_repositories(df)


def test_duplicate_github_ids_fail():
    df = valid_dataframe().with_columns(
        pl.Series("github_id", [1, 1])
    )

    with pytest.raises(ValueError, match="Duplicate github_id"):
        validate_repositories(df)


def test_negative_stars_fail():
    df = valid_dataframe().with_columns(
        pl.Series("stars", [100, -1])
    )

    with pytest.raises(ValueError, match="Negative star count"):
        validate_repositories(df)


def test_negative_forks_fail():
    df = valid_dataframe().with_columns(
        pl.Series("forks", [10, -1])
    )

    with pytest.raises(ValueError, match="Negative fork count"):
        validate_repositories(df)