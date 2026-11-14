# Day 1: API Data Analysis Using Python Structures

Pesa Pulse customer directory analysis. Fetches customers from the JSONPlaceholder Users API, explores the nested JSON, and answers "where are our customers?" with plain Python structures, then pandas.

## How to run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python analysis.py
```

Requires Python 3.9+ and internet access. Outputs are written to `output/`:

- `customers.csv`
- `city_counts.csv`
- `customer_distribution.png` (customers by city)
- `email_domain_distribution.png` (customers by email TLD)

## Approach

| Task | Implementation |
|---|---|
| 1. Retrieve | `get_customers` uses `requests.get` with a 10 s timeout, checks for HTTP 200, validates JSON and list type. Each failure prints one clear message and returns `[]`. `main` exits with code 1 if no data. |
| 2. Explore | `explore` recurses through dicts and prints `key: type`, indented two spaces per depth level. |
| 3. Extract | `extract_attributes` flattens each record. `latitude` and `longitude` are cast to `float`. |
| 4. Sets | `unique_cities` uses a set comprehension. |
| 5. Counting | `city_counts` uses a loop with `dict.get`. `email_domain_counts` uses a dict comprehension. No `Counter`, no pandas. Both sort by count descending, then key ascending. |
| 6. pandas | `to_dataframe` builds the DataFrame. `main` asserts that `value_counts()` equals the hand-written counts, and prints shape and dtypes. |
| 7. Export | `to_csv(..., index=False)` for both files, columns as in the expected-output resource. |
| 8. Chart | `plot_distribution` draws a titled, labelled bar chart. It is called twice: by city and by email TLD. |

## Nested structure

Nested attributes:

- `address` (dict)
  - `geo` (dict) inside `address`
- `company` (dict)

Deepest attribute is latitude: `customer["address"]["geo"]["lat"]`. Longitude is `customer["address"]["geo"]["lng"]`. Depth is 3 keys. Both values arrive as strings and are cast to float.

## Findings

1. There are 10 customers and 10 unique cities. Every city appears once. The comparison tells marketing that city is too granular to plan regional campaigns, because no city has more than one customer.
2. The email TLD chart is more useful. `.biz` is the only repeated value (3 of 10, 30%). Every other TLD (`ca`, `info`, `io`, `me`, `net`, `org`, `tv`) appears once. The city chart is flat and shows no differences between categories.
3. pandas `value_counts()` matches the hand-written dict counts for both city and email TLD.

Observations on the data:

- The data is mock. City names, coordinates and zipcodes are fictional and not geographically consistent, so latitude and longitude cannot support real regional analysis.
- A usable regional view needs a coarser field (region, county or country). The directory does not provide one.

## Assumptions

- "Email domain" in the CSV means the top-level domain (`biz`, `tv`), as the starter docstring and expected-output file specify. The full host (`april.biz`) is recoverable from `email`.
- TLDs are lowercased.
- Ties in counts are broken alphabetically so output is deterministic.
- "Most common city" with all counts equal is the first city alphabetically.
- `plot_distribution` has optional `title`, `xlabel` and `ylabel` arguments, with defaults for the city chart, so the same function draws both charts.
- Charts use the non-interactive `Agg` backend. No window opens.

## Structure

```
day1-api-analysis/
├── analysis.py
├── output/
│   ├── customers.csv
│   ├── city_counts.csv
│   ├── customer_distribution.png
│   └── email_domain_distribution.png
├── requirements.txt
└── README.md
```
