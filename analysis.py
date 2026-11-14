"""
Day 1 - API Data Analysis Using Python Structures
Squad Python Specialization - Data Science, AI & Analytics

Fetches the Pesa Pulse partner customer directory, explores its nested
structure, answers "where are our customers?" with plain Python structures,
cross-checks with pandas, exports CSVs and saves charts.
"""
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless-safe backend; we only save files
import matplotlib.pyplot as plt
import pandas as pd
import requests

API_URL = "https://jsonplaceholder.typicode.com/users"
TIMEOUT_SECONDS = 10
OUTPUT_DIR = Path("output")


# ---------------------------------------------------------------------------
# Task 1: retrieve data
# ---------------------------------------------------------------------------
def get_customers(url: str = API_URL) -> list[dict]:
    """Fetch the customer list. Report failures clearly instead of crashing.

    Returns an empty list on any failure so callers can decide what to do.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
    except requests.exceptions.Timeout:
        print(f"ERROR: request to {url} timed out after {TIMEOUT_SECONDS}s.")
        return []
    except requests.exceptions.ConnectionError:
        print(f"ERROR: could not connect to {url}. Check your internet connection.")
        return []
    except requests.exceptions.RequestException as exc:
        print(f"ERROR: request to {url} failed: {exc}")
        return []

    if response.status_code != 200:
        print(f"ERROR: {url} returned HTTP {response.status_code}, expected 200.")
        return []

    try:
        data = response.json()
    except ValueError:
        print(f"ERROR: {url} did not return valid JSON.")
        return []

    if not isinstance(data, list):
        print(f"ERROR: expected a list of customers, got {type(data).__name__}.")
        return []
    return data


# ---------------------------------------------------------------------------
# Task 2: explore nested structure
# ---------------------------------------------------------------------------
def explore(record: dict, indent: int = 0) -> None:
    """Print every key in a (possibly nested) record with its type, indented by depth."""
    pad = "  " * indent
    for key, value in record.items():
        print(f"{pad}{key}: {type(value).__name__}")
        if isinstance(value, dict):
            explore(value, indent + 1)
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    print(f"{pad}  [list item]")
                    explore(item, indent + 2)
                    break  # one sample item shows the shape


# ---------------------------------------------------------------------------
# Task 3: extract attributes
# ---------------------------------------------------------------------------
def _email_tld(email: str) -> str:
    """Return the top-level domain of an email address ('a@b.biz' -> 'biz')."""
    host = email.rsplit("@", 1)[-1]
    return host.rsplit(".", 1)[-1].lower()


def extract_attributes(customers: list[dict]) -> list[dict]:
    """Return one flat dict per customer with the attributes listed in the task."""
    rows = []
    for c in customers:
        address = c.get("address", {})
        geo = address.get("geo", {})
        rows.append(
            {
                "customer_id": int(c["id"]),
                "name": c.get("name"),
                "username": c.get("username"),
                "email": c.get("email"),
                "email_domain": _email_tld(c.get("email", "")),
                "phone": c.get("phone"),
                "city": address.get("city"),
                "zipcode": address.get("zipcode"),
                "latitude": float(geo["lat"]) if geo.get("lat") is not None else None,
                "longitude": float(geo["lng"]) if geo.get("lng") is not None else None,
                "company": c.get("company", {}).get("name"),
                "website": c.get("website"),
            }
        )
    return rows


# ---------------------------------------------------------------------------
# Task 4: sets
# ---------------------------------------------------------------------------
def unique_cities(customers: list[dict]) -> set[str]:
    """Return the set of distinct cities."""
    return {c["address"]["city"] for c in customers}


# ---------------------------------------------------------------------------
# Task 5: counting without Counter or pandas
# ---------------------------------------------------------------------------
def _sort_counts(counts: dict[str, int]) -> dict[str, int]:
    """Sort by count descending, then key ascending."""
    return dict(sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])))


def city_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per city using a loop and/or a dict comprehension (no Counter, no pandas)."""
    counts: dict[str, int] = {}
    for c in customers:
        city = c["address"]["city"]
        counts[city] = counts.get(city, 0) + 1
    return _sort_counts(counts)


def email_domain_counts(customers: list[dict]) -> dict[str, int]:
    """Count customers per email top-level domain (e.g. 'biz', 'tv')."""
    domains = [_email_tld(c["email"]) for c in customers]
    return _sort_counts({d: domains.count(d) for d in set(domains)})


# ---------------------------------------------------------------------------
# Task 6: pandas
# ---------------------------------------------------------------------------
def to_dataframe(rows: list[dict]) -> pd.DataFrame:
    """Convert flat rows into a DataFrame."""
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Task 8: charts
# ---------------------------------------------------------------------------
def plot_distribution(
    counts: dict[str, int],
    path: Path,
    title: str = "Customers by City",
    xlabel: str = "City",
    ylabel: str = "Number of customers",
) -> None:
    """Save a labelled chart of the distribution to path."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(list(counts.keys()), list(counts.values()), color="#2a6f97")
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(counts.values(), default=1) + 1)
    ax.yaxis.get_major_locator().set_params(integer=True)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def main() -> int:
    customers = get_customers()
    if not customers:
        print("No data retrieved. Exiting.")
        return 1

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Task 2
    print("Structure of one customer record:")
    explore(customers[0])
    print()

    # Tasks 3-5
    rows = extract_attributes(customers)
    cities = unique_cities(customers)
    by_city = city_counts(customers)
    by_domain = email_domain_counts(customers)

    # Task 6: pandas cross-check
    df = to_dataframe(rows)
    pandas_city = df["city"].value_counts().to_dict()
    pandas_domain = df["email_domain"].value_counts().to_dict()
    assert by_city == pandas_city, "City counts differ between dict and pandas"
    assert by_domain == pandas_domain, "Domain counts differ between dict and pandas"
    print(f"DataFrame shape: {df.shape}")
    print("DataFrame dtypes:")
    print(df.dtypes.to_string())
    print("pandas agrees with hand-written counts: True")
    print()

    # Task 7: exports
    df.to_csv(OUTPUT_DIR / "customers.csv", index=False)
    city_df = (
        pd.DataFrame(list(by_city.items()), columns=["city", "customer_count"])
        .sort_values(["customer_count", "city"], ascending=[False, True])
    )
    city_df.to_csv(OUTPUT_DIR / "city_counts.csv", index=False)

    # Task 8: charts
    chart_path = OUTPUT_DIR / "customer_distribution.png"
    plot_distribution(by_city, chart_path)
    plot_distribution(
        by_domain,
        OUTPUT_DIR / "email_domain_distribution.png",
        title="Customers by Email Top-Level Domain",
        xlabel="Email TLD",
    )

    # Findings
    top_city, top_n = next(iter(by_city.items()))
    print(f"Customers retrieved : {len(customers)}")
    print(f"Unique cities       : {len(cities)}")
    print(f"Most common city    : {top_city} ({top_n})")
    print(f"Email domains       : {by_domain}")
    print(f"Chart saved to      : {chart_path}")
    if len(cities) == len(customers):
        print("Every customer is in a different city: city is too granular for campaigns.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
