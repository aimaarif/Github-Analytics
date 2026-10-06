CREATE TABLE IF NOT EXISTS repositories (
    id BIGSERIAL PRIMARY KEY,
    github_id BIGINT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    full_name TEXT UNIQUE NOT NULL,
    owner TEXT NOT NULL,
    description TEXT,
    language TEXT,
    stars INTEGER NOT NULL,
    forks INTEGER NOT NULL,
    open_issues INTEGER NOT NULL,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS repository_snapshots (
    id BIGSERIAL PRIMARY KEY,
    repository_id BIGINT NOT NULL
        REFERENCES repositories(id),
    snapshot_date DATE NOT NULL,
    collected_at TIMESTAMPTZ NOT NULL,
    stars INTEGER NOT NULL,
    forks INTEGER NOT NULL,
    open_issues INTEGER NOT NULL,

    UNIQUE (repository_id, snapshot_date)
);