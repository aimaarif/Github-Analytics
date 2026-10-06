import polars as pl


def validate_repositories(df):
    errors = []

    if df["github_id"].is_duplicated().any():
        errors.append("Duplicate github_id values found")

    if (df["stars"] < 0).any():
        errors.append("Negative star count found")

    if (df["forks"] < 0).any():
        errors.append("Negative fork count found")

    if df["full_name"].is_null().any():
        errors.append("Null full_name found")

    if errors:
        raise ValueError(
            "Validation failed:\n"
            + "\n".join(errors)
        )

    print("Validation passed.")