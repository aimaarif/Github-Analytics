from src.transform.repositories import transform_repositories


def sample_repository():
    return {
        "id": 12345,
        "name": "sample-project",
        "full_name": "example/sample-project",
        "owner": {"login": "example"},
        "description": None,
        "language": None,
        "stargazers_count": 100,
        "forks_count": 20,
        "open_issues_count": 5,
        "created_at": "2024-01-01T10:00:00Z",
        "updated_at": "2024-06-01T12:00:00Z",
    }


def test_transform_creates_expected_columns():
    df = transform_repositories([sample_repository()])

    expected_columns = [
        "github_id",
        "name",
        "full_name",
        "owner",
        "description",
        "language",
        "stars",
        "forks",
        "open_issues",
        "created_at",
        "updated_at",
    ]

    assert df.columns == expected_columns
    assert df.height == 1


def test_transform_fills_missing_values():
    df = transform_repositories([sample_repository()])

    assert df["description"][0] == "No description"
    assert df["language"][0] == "Unknown"


def test_transform_converts_dates():
    df = transform_repositories([sample_repository()])

    assert df["created_at"].dtype.time_zone == "UTC"
    assert df["updated_at"].dtype.time_zone == "UTC"