import csv
import json
import os
import requests

from bs4 import BeautifulSoup

from doc_finder import find_documentation


CSV_FILE = "data/apps.csv"
OUTPUT_DIR = "results/smart_evidence"

os.makedirs(OUTPUT_DIR, exist_ok=True)


def collect_page(url):

    print(f"    Downloading: {url}")

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
        timeout=20
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    for element in soup([
        "script",
        "style",
        "nav",
        "footer"
    ]):
        element.decompose()

    text = soup.get_text(
        separator=" ",
        strip=True
    )

    return {
        "url": response.url,
        "title": (
            soup.title.get_text(strip=True)
            if soup.title
            else ""
        ),
        "text": text
    }


def safe_filename(name):

    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
    )


# ---------------------------------------
# Read applications
# ---------------------------------------

with open(
    CSV_FILE,
    "r",
    encoding="utf-8"
) as file:

    apps = list(
        csv.DictReader(file)
    )


# ---------------------------------------
# Test first 3 applications
# ---------------------------------------

test_apps = apps[:3]

print(
    f"Testing smart evidence collection "
    f"on {len(test_apps)} apps...\n"
)


# ---------------------------------------
# Process applications
# ---------------------------------------

for app in test_apps:

    app_id = app["id"]
    app_name = app["app"]
    website = app["website"]

    print("\n" + "=" * 60)
    print(f"[{app_id}/100] {app_name}")
    print("=" * 60)

    try:

        # Find developer/API documentation
        documentation_pages = (
            find_documentation(website)
        )

        if not documentation_pages:

            print(
                "  No documentation pages found."
            )

            continue

        sources = []

        # Collect only the first few useful pages
        for page in documentation_pages[:5]:

            try:

                source = collect_page(
                    page["url"]
                )

                sources.append(source)

            except Exception as error:

                print(
                    f"    Could not collect "
                    f"{page['url']}: {error}"
                )

        result = {
            "id": app_id,
            "app": app_name,
            "category": app["category"],
            "website": website,
            "sources": sources
        }

        filename = (
            f"{OUTPUT_DIR}/"
            f"{safe_filename(app_name)}.json"
        )

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        print(
            f"\n  ✓ Saved: {filename}"
        )

        print(
            f"  ✓ Sources collected: "
            f"{len(sources)}"
        )

    except Exception as error:

        print(
            f"  ✗ Failed: {error}"
        )


print("\n" + "=" * 60)
print("SMART COLLECTION TEST COMPLETE")
print("=" * 60)