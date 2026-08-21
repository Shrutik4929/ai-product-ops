import csv
import json
import os
import requests

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

from doc_finder import find_documentation


CSV_FILE = "data/apps.csv"
OUTPUT_DIR = "results/final_evidence"

os.makedirs(OUTPUT_DIR, exist_ok=True)


KEYWORDS = [
    "authentication",
    "auth",
    "oauth",
    "api",
    "api reference",
    "api documentation",
    "developer",
    "token",
    "access token",
    "credentials",
    "getting started",
    "mcp",
    "model context protocol",
    "rest",
    "graphql",
    "private app",
    "public app"
]


def normalize_domain(url):

    parsed = urlparse(url)

    domain = parsed.netloc.lower()

    if domain.startswith("www."):
        domain = domain[4:]

    return domain


def download_page(url):

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

    links = []

    for link in soup.find_all(
        "a",
        href=True
    ):

        href = urljoin(
            response.url,
            link["href"]
        )

        text = link.get_text(
            " ",
            strip=True
        )

        links.append({
            "url": href,
            "text": text
        })

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
            soup.title.get_text(
                strip=True
            )
            if soup.title
            else ""
        ),
        "text": text,
        "links": links
    }


def score_link(link):

    combined = (
        link["url"] + " " + link["text"]
    ).lower()

    score = 0

    for keyword in KEYWORDS:

        if keyword in combined:
            score += 1

    return score


def collect_relevant_links(
    page,
    allowed_domain
):

    results = []

    for link in page["links"]:

        try:
            domain = normalize_domain(
                link["url"]
            )

            # Stay on official domain
            if (
                domain != allowed_domain
                and not domain.endswith(
                    "." + allowed_domain
                )
            ):
                continue

            score = score_link(link)

            if score > 0:

                results.append({
                    "url": link["url"],
                    "text": link["text"],
                    "score": score
                })

        except Exception:
            pass

    return results


def safe_filename(name):

    return (
        name.lower()
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
        .replace("(", "")
        .replace(")", "")
    )


# -----------------------------------------
# Read apps
# -----------------------------------------

with open(
    CSV_FILE,
    "r",
    encoding="utf-8"
) as file:

    apps = list(
        csv.DictReader(file)
    )


# TEST ONLY 3
test_apps = apps


print(
    f"Deep evidence collection "
    f"for {len(test_apps)} apps\n"
)


for app in test_apps:

    app_name = app["app"]
    website = app["website"]

    print("\n" + "=" * 60)
    print(app_name)
    print("=" * 60)

    try:

        allowed_domain = normalize_domain(
            website
        )

        # ---------------------------------
        # Discover developer pages
        # ---------------------------------

        documentation_pages = (
            find_documentation(website)
        )

        seed_urls = [
            page["url"]
            for page in documentation_pages
        ]

        # Remove duplicates
        seed_urls = list(
            dict.fromkeys(seed_urls)
        )

        print(
            f"Developer pages found: "
            f"{len(seed_urls)}"
        )

        # ---------------------------------
        # Download seed pages
        # ---------------------------------

        pages_to_process = []

        for url in seed_urls[:5]:

            try:

                print(
                    f"Reading seed: {url}"
                )

                page = download_page(url)

                pages_to_process.append(page)

            except Exception as error:

                print(
                    f"Could not read {url}: "
                    f"{error}"
                )

        # ---------------------------------
        # Discover relevant links
        # ---------------------------------

        all_candidates = {}

        for page in pages_to_process:

            links = collect_relevant_links(
                page,
                allowed_domain
            )

            for link in links:

                existing = all_candidates.get(
                    link["url"]
                )

                if (
                    existing is None
                    or link["score"] > existing["score"]
                ):

                    all_candidates[
                        link["url"]
                    ] = link

        candidates = list(
            all_candidates.values()
        )

        candidates.sort(
            key=lambda x: x["score"],
            reverse=True
        )

        print(
            f"Relevant official links: "
            f"{len(candidates)}"
        )

        # ---------------------------------
        # Collect deeper pages
        # ---------------------------------

        sources = []

        collected_urls = set()

        # Add seed pages
        for page in pages_to_process:

            sources.append({
                "url": page["url"],
                "title": page["title"],
                "text": page["text"]
            })

            collected_urls.add(
                page["url"]
            )

        # Visit top relevant links
        for candidate in candidates[:15]:

            url = candidate["url"]

            if url in collected_urls:
                continue

            try:

                print(
                    f"Targeted: {url}"
                )

                page = download_page(url)

                sources.append({
                    "url": page["url"],
                    "title": page["title"],
                    "text": page["text"]
                })

                collected_urls.add(
                    page["url"]
                )

            except requests.exceptions.HTTPError as error:

                status_code = None

                if error.response is not None:
                    status_code = error.response.status_code

                sources.append({
                    "url": url,
                    "title": "",
                    "text": "",
                    "access_status": "blocked",
                    "http_status": status_code
                })

                print(
                    f"Blocked: {url} "
                    f"(HTTP {status_code})"
                )

            except Exception as error:

                sources.append({
                    "url": url,
                    "title": "",
                    "text": "",
                    "access_status": "error",
                    "http_status": None
                })

                print(
                    f"Error: {url} - {error}"
                )

        # ---------------------------------
        # Save
        # ---------------------------------

        result = {
            "id": app["id"],
            "app": app_name,
            "category": app["category"],
            "website": website,
            "sources": sources
        }

        output_file = os.path.join(
            OUTPUT_DIR,
            safe_filename(app_name)
            + ".json"
        )

        with open(
            output_file,
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
            f"\n✓ Saved: {output_file}"
        )

        print(
            f"✓ Sources: {len(sources)}"
        )

    except Exception as error:

        print(
            f"✗ Failed: {error}"
        )


print("\n" + "=" * 60)
print("DEEP EVIDENCE COLLECTION COMPLETE")
print("=" * 60)