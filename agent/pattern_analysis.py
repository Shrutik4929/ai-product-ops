import csv
import json
from collections import Counter, defaultdict


INPUT_FILE = "results/final_master_dataset.csv"
OUTPUT_FILE = "results/pattern_analysis.json"


def read_csv():
    with open(
        INPUT_FILE,
        "r",
        encoding="utf-8-sig"
    ) as f:
        return list(csv.DictReader(f))


def split_values(value):
    if not value:
        return []

    return [
        x.strip()
        for x in value.split(";")
        if x.strip()
    ]


def normalize(value):
    return value.lower().strip()


def count_auth(rows):
    counter = Counter()

    for row in rows:
        methods = split_values(
            row["auth_methods"]
        )

        if not methods:
            counter["Unknown"] += 1
            continue

        for method in methods:
            counter[method] += 1

    return counter


def classify_self_serve(value):

    v = normalize(value)

    if not v or "unknown" in v:
        return "Unknown"

    if (
        "gated" in v
        or "contact sales" in v
        or "partnership" in v
        or "partner" in v
    ):
        return "Gated"

    if (
        "conditional" in v
        or "plan" in v
        or "paid" in v
        or "admin" in v
    ):
        return "Conditional"

    if (
        "self-serve" in v
        or "self serve" in v
        or "free" in v
        or "yes" in v
    ):
        return "Self-serve"

    return "Unknown"


def classify_mcp(value):

    v = normalize(value)

    # Check negative cases FIRST because
    # "not confirmed" contains "confirmed".

    if (
        "not confirmed" in v
        or "not found" in v
        or "unknown" in v
    ):
        return "Not confirmed"

    if "confirmed" in v:
        return "Confirmed"

    return "Unknown"


def classify_buildability(value):

    v = normalize(value)

    if not v or "unknown" in v:
        return "Unknown"

    if (
        "needs verification" in v
        or "review" in v
    ):
        return "Needs verification"

    if (
        "gated" in v
        or "outreach" in v
        or "partnership" in v
    ):
        return "Gated / outreach"

    if "buildable" in v:
        return "Buildable"

    return "Other"


def category_summary(rows):

    result = defaultdict(
        lambda: {
            "apps": 0,
            "buildable": 0,
            "mcp_confirmed": 0,
            "self_serve": 0
        }
    )

    for row in rows:

        category = row["category"]

        result[category]["apps"] += 1

        if (
            classify_buildability(
                row["buildability"]
            ) == "Buildable"
        ):
            result[category]["buildable"] += 1

        if (
            classify_mcp(
                row["mcp_available"]
            ) == "Confirmed"
        ):
            result[category]["mcp_confirmed"] += 1

        if (
            classify_self_serve(
                row["self_serve"]
            ) == "Self-serve"
        ):
            result[category]["self_serve"] += 1

    return dict(result)


def blocker_summary(rows):

    counter = Counter()

    for row in rows:

        blocker = row["main_blocker"].strip()

        if not blocker:
            counter["Unknown"] += 1
        else:
            counter[blocker] += 1

    return counter


rows = read_csv()

print("=" * 65)
print("100-APP PATTERN ANALYSIS")
print("=" * 65)

print(f"\nTotal apps: {len(rows)}")


# --------------------------------------------------
# AUTH
# --------------------------------------------------

auth = count_auth(rows)

print("\nAUTHENTICATION")
print("-" * 40)

for name, count in auth.most_common():

    percentage = (
        count / len(rows) * 100
    )

    print(
        f"{name}: "
        f"{count} ({percentage:.1f}%)"
    )


# --------------------------------------------------
# SELF SERVE
# --------------------------------------------------

self_serve = Counter(
    classify_self_serve(
        row["self_serve"]
    )
    for row in rows
)

print("\nSELF-SERVE / ACCESS")
print("-" * 40)

for name, count in self_serve.most_common():

    print(
        f"{name}: "
        f"{count} "
        f"({count / len(rows) * 100:.1f}%)"
    )


# --------------------------------------------------
# MCP
# --------------------------------------------------

mcp = Counter(
    classify_mcp(
        row["mcp_available"]
    )
    for row in rows
)

print("\nMCP")
print("-" * 40)

for name, count in mcp.most_common():

    print(
        f"{name}: "
        f"{count} "
        f"({count / len(rows) * 100:.1f}%)"
    )


# --------------------------------------------------
# BUILDABILITY
# --------------------------------------------------

buildability = Counter(
    classify_buildability(
        row["buildability"]
    )
    for row in rows
)

print("\nBUILDABILITY")
print("-" * 40)

for name, count in buildability.most_common():

    print(
        f"{name}: "
        f"{count} "
        f"({count / len(rows) * 100:.1f}%)"
    )


# --------------------------------------------------
# BLOCKERS
# --------------------------------------------------

blockers = blocker_summary(rows)

print("\nTOP BLOCKERS")
print("-" * 40)

for name, count in blockers.most_common(10):

    print(
        f"{count} × {name}"
    )


# --------------------------------------------------
# CATEGORY ANALYSIS
# --------------------------------------------------

categories = category_summary(rows)

print("\nCATEGORY ANALYSIS")
print("-" * 40)

for category, data in sorted(
    categories.items()
):

    print(
        f"\n{category}"
    )

    print(
        f"  Apps: {data['apps']}"
    )

    print(
        f"  Buildable: {data['buildable']}"
    )

    print(
        f"  MCP confirmed: "
        f"{data['mcp_confirmed']}"
    )

    print(
        f"  Self-serve: "
        f"{data['self_serve']}"
    )


# --------------------------------------------------
# EASY WINS
# --------------------------------------------------

easy_wins = []

for row in rows:

    build = classify_buildability(
        row["buildability"]
    )

    selfserve = classify_self_serve(
        row["self_serve"]
    )

    if (
        build == "Buildable"
        and selfserve == "Self-serve"
    ):
        easy_wins.append(
            row["app"]
        )


print("\nEASY-WIN CANDIDATES")
print("-" * 40)

for app in easy_wins:

    print(
        f"✓ {app}"
    )


# --------------------------------------------------
# SAVE RESULTS
# --------------------------------------------------

output = {
    "total_apps": len(rows),
    "authentication": dict(auth),
    "self_serve": dict(self_serve),
    "mcp": dict(mcp),
    "buildability": dict(buildability),
    "top_blockers": dict(
        blockers.most_common(10)
    ),
    "categories": categories,
    "easy_wins": easy_wins
}


with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        output,
        f,
        indent=2,
        ensure_ascii=False
    )


print("\n" + "=" * 65)
print("PATTERN ANALYSIS COMPLETE")
print("=" * 65)

print(
    f"Saved to: {OUTPUT_FILE}"
)