import json
import glob
import csv
import os


INPUT_DIR = "results/final_analysis"
OUTPUT_DIR = "results"

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "final_master_dataset.csv"
)


FIELDS = [
    "id",
    "app",
    "category",
    "website",
    "auth_methods",
    "self_serve",
    "api_type",
    "api_breadth",
    "mcp_available",
    "buildability",
    "main_blocker",
    "evidence",
    "evidence_urls",
    "analysis_method"
]


def flatten(value):
    """Convert lists into readable text."""

    if isinstance(value, list):
        return "; ".join(
            str(x) for x in value
        )

    if isinstance(value, dict):
        return json.dumps(
            value,
            ensure_ascii=False
        )

    if value is None:
        return ""

    return str(value)


files = glob.glob(
    os.path.join(
        INPUT_DIR,
        "*.json"
    )
)


print("=" * 60)
print("BUILDING MASTER DATASET")
print("=" * 60)

print(
    f"Analysis files found: {len(files)}"
)


rows = []


for file in files:

    try:

        with open(
            file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)


        row = {}

        for field in FIELDS:

            row[field] = flatten(
                data.get(field, "")
            )


        rows.append(row)

        print(
            f"✓ {data.get('app', 'Unknown')}"
        )


    except Exception as error:

        print(
            f"✗ Failed: {file}"
        )

        print(
            f"  Reason: {error}"
        )


# Sort alphabetically
rows.sort(
    key=lambda x: x["app"].lower()
)


os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


with open(
    OUTPUT_FILE,
    "w",
    newline="",
    encoding="utf-8-sig"
) as f:

    writer = csv.DictWriter(
        f,
        fieldnames=FIELDS
    )

    writer.writeheader()

    writer.writerows(rows)


print()
print("=" * 60)
print("MASTER DATASET CREATED")
print("=" * 60)

print(
    f"Rows: {len(rows)}"
)

print(
    f"Columns: {len(FIELDS)}"
)

print(
    f"Saved to: {OUTPUT_FILE}"
)