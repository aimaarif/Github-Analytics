from src.extract.github_api import deduplicate_repositories


def test_deduplicate_repositories_uses_github_id():
    repositories = [
        {"id": 1, "full_name": "example/one"},
        {"id": 2, "full_name": "example/two"},
        {"id": 1, "full_name": "example/one"},
    ]

    result = deduplicate_repositories(repositories)

    assert len(result) == 2
    assert {repo["id"] for repo in result} == {1, 2}