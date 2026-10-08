import streamlit as st
import duckdb
import pandas as pd
from pathlib import Path



# Configuration


st.set_page_config(
    page_title="GitHub Analytics",
    page_icon="",
    layout="wide",
)


BASE_DIR = Path(__file__).resolve().parents[2]

REPOSITORIES_FILE = (
    BASE_DIR / "data" / "processed" / "repositories.parquet"
)

SNAPSHOTS_FILE = (
    BASE_DIR / "data" / "processed" / "repositories_snapshots.parquet"
)

# Database connection

@st.cache_resource
def get_connection():
    return duckdb.connect()

conn = get_connection()

# Data loading

@st.cache_data
def load_repositories():
    query = f"""
        SELECT *
        FROM read_parquet('{REPOSITORIES_FILE}')
    """

    return conn.execute(query).df()


@st.cache_data
def load_snapshots():
    query = f"""
        SELECT *
        FROM read_parquet('{SNAPSHOTS_FILE}')
    """

    return conn.execute(query).df()


repositories = load_repositories()
snapshots = load_snapshots()

# Sidebar

st.sidebar.title("GitHub Analytics")

page = st.sidebar.radio(
    "Navigate",
    [
        "Overview",
        "Repositories",
        "Languages",
        "Growth",
        "Snapshots",
        "Data",
    ],
)

# Overview

if page == "Overview":

    st.title("GitHub Analytics Dashboard")

    st.write(
        "Explore repository data collected from the GitHub API."
    )

    total_repositories = len(repositories)
    total_stars = int(repositories["stars"].sum())
    total_forks = int(repositories["forks"].sum())
    total_issues = int(repositories["open_issues"].sum())

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Repositories",
        f"{total_repositories:,}",
    )

    col2.metric(
        "Total Stars",
        f"{total_stars:,}",
    )

    col3.metric(
        "Total Forks",
        f"{total_forks:,}",
    )

    col4.metric(
        "Open Issues",
        f"{total_issues:,}",
    )

    st.divider()

    st.subheader("Top Repositories")

    top_repositories = (
        repositories
        .sort_values("stars", ascending=False)
        .head(10)
    )

    st.dataframe(
        top_repositories[
            [
                "full_name",
                "language",
                "stars",
                "forks",
                "open_issues",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

# Repositories

elif page == "Repositories":

    st.title("Repositories")

    search = st.text_input(
        "Search repositories",
        placeholder="django, tensorflow, pandas..."
    )

    languages = sorted(
        repositories["language"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_language = st.selectbox(
        "Language",
        ["All"] + languages,
    )

    filtered = repositories.copy()

    if search:
        filtered = filtered[
            filtered["full_name"]
            .str.contains(
                search,
                case=False,
                na=False,
            )
        ]

    if selected_language != "All":
        filtered = filtered[
            filtered["language"] == selected_language
        ]

    st.write(
        f"Showing {len(filtered):,} repositories"
    )

    st.dataframe(
        filtered[
            [
                "full_name",
                "owner",
                "language",
                "stars",
                "forks",
                "open_issues",
                "created_at",
                "updated_at",
            ]
        ].sort_values(
            "stars",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

# Languages

elif page == "Languages":

    st.title("Language Analysis")

    language_stats = (
        repositories[
            repositories["language"] != "Unknown"
        ]
        .groupby("language")
        .agg(
            repositories=("full_name", "count"),
            average_stars=("stars", "mean"),
            total_stars=("stars", "sum"),
        )
        .reset_index()
        .sort_values(
            "repositories",
            ascending=False,
        )
    )

    st.subheader("Repositories by Language")

    st.bar_chart(
        language_stats.set_index("language")[
            "repositories"
        ]
    )

    st.subheader("Language Statistics")

    language_stats["average_stars"] = (
        language_stats["average_stars"]
        .round(0)
        .astype(int)
    )

    st.dataframe(
        language_stats,
        use_container_width=True,
        hide_index=True,
    )

# Growth

elif page == "Growth":

    st.title("Repository Growth")

    query = f"""
        WITH ranked AS (
            SELECT
                github_id,
                full_name,
                collected_at,
                stars,

                ROW_NUMBER() OVER (
                    PARTITION BY github_id
                    ORDER BY collected_at ASC
                ) AS first_row,

                ROW_NUMBER() OVER (
                    PARTITION BY github_id
                    ORDER BY collected_at DESC
                ) AS latest_row

            FROM read_parquet('{SNAPSHOTS_FILE}')
        ),

        first_values AS (
            SELECT
                github_id,
                full_name,
                stars AS first_stars
            FROM ranked
            WHERE first_row = 1
        ),

        latest_values AS (
            SELECT
                github_id,
                full_name,
                stars AS latest_stars
            FROM ranked
            WHERE latest_row = 1
        )

        SELECT
            f.github_id,
            f.full_name,
            f.first_stars,
            l.latest_stars,
            l.latest_stars - f.first_stars AS star_growth

        FROM first_values f

        JOIN latest_values l
            ON f.github_id = l.github_id

        ORDER BY star_growth DESC

        LIMIT 20
    """

    growth = conn.execute(query).df()

    st.subheader("Fastest Growing Repositories")

    st.dataframe(
        growth,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Star Growth")

    st.bar_chart(
        growth.set_index("full_name")[
            "star_growth"
        ]
    )

# Snapshots

elif page == "Snapshots":

    st.title("Historical Snapshots")

    snapshot_dates = sorted(
        snapshots["collected_at"]
        .dt.date
        .unique(),
        reverse=True,
    )

    st.metric(
        "Snapshot Dates",
        len(snapshot_dates),
    )

    st.metric(
        "Total Snapshot Records",
        f"{len(snapshots):,}",
    )

    st.subheader("Available Snapshot Dates")

    for date in snapshot_dates:
        st.write(str(date))

    st.subheader("Snapshot Data")

    st.dataframe(
        snapshots.sort_values(
            "collected_at",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

# Data

elif page == "Data":

    st.title("Processed Data")

    st.subheader("Repositories")

    st.write(
        f"{len(repositories):,} repository records"
    )

    st.download_button(
        label="Download Repository Data",
        data=repositories.to_csv(index=False),
        file_name="repositories.csv",
        mime="text/csv",
    )

    st.dataframe(
        repositories,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader("Snapshots")

    st.write(
        f"{len(snapshots):,} snapshot records"
    )

    st.download_button(
        label="Download Snapshot Data",
        data=snapshots.to_csv(index=False),
        file_name="repositories_snapshots.csv",
        mime="text/csv",
    )