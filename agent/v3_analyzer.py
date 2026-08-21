import json
import os
import glob
import re


INPUT_DIR = "results/final_evidence"
OUTPUT_DIR = "results/final_analysis"

os.makedirs(OUTPUT_DIR, exist_ok=True)


# =========================================================
# Evidence helpers
# =========================================================

def normalize(text):
    return re.sub(r"\s+", " ", text.lower()).strip()


def find_snippet(text, keywords, window=180):

    lower = text.lower()

    for keyword in keywords:

        position = lower.find(keyword.lower())

        if position != -1:

            start = max(0, position - window)
            end = min(
                len(text),
                position + len(keyword) + window
            )

            return text[start:end]

    return None


# =========================================================
# Authentication
# =========================================================

def detect_auth(text):

    text = normalize(text)

    methods = []
    evidence = []

    patterns = {
        "OAuth 2.0": [
            "oauth 2.0",
            "oauth2",
            "oauth"
        ],
        "API key": [
            "api key",
            "apikey"
        ],
        "Token": [
            "bearer token",
            "access token",
            "personal access token",
            "api token"
        ],
        "Basic authentication": [
            "basic authentication",
            "basic auth"
        ]
    }

    for method, keywords in patterns.items():

        for keyword in keywords:

            if keyword in text:

                methods.append(method)

                snippet = find_snippet(
                    text,
                    [keyword]
                )

                if snippet:
                    evidence.append({
                        "signal": method,
                        "snippet": snippet
                    })

                break

    methods = list(dict.fromkeys(methods))

    if not methods:

        methods = ["Unknown"]

    return methods, evidence


# =========================================================
# API detection
# =========================================================

def detect_api(text):

    text = normalize(text)

    api_types = []
    evidence = []

    if (
        "rest api" in text
        or "restful api" in text
        or "rest api reference" in text
        or "rest endpoints" in text
    ):

        api_types.append("REST")

        snippet = find_snippet(
            text,
            [
                "rest api",
                "restful api",
                "rest api reference"
            ]
        )

        if snippet:
            evidence.append({
                "signal": "REST",
                "snippet": snippet
            })

    if "graphql" in text:

        api_types.append("GraphQL")

        snippet = find_snippet(
            text,
            ["graphql"]
        )

        if snippet:
            evidence.append({
                "signal": "GraphQL",
                "snippet": snippet
            })

    if (
        "api reference" in text
        or "api documentation" in text
        or "api docs" in text
        or "developer api" in text
    ):

        if not api_types:
            api_types.append(
                "Public API - type unclear"
            )

        snippet = find_snippet(
            text,
            [
                "api reference",
                "api documentation",
                "api docs"
            ]
        )

        if snippet:
            evidence.append({
                "signal": "API documentation",
                "snippet": snippet
            })

    if not api_types:

        api_types = ["Unknown"]

    return list(dict.fromkeys(api_types)), evidence


# =========================================================
# API breadth
# =========================================================

def detect_breadth(text):

    text = normalize(text)

    broad_signals = [
        "api reference",
        "api endpoints",
        "available endpoints",
        "all endpoints",
        "complete api",
        "majority of",
        "wide range of",
        "multiple resources",
        "multiple endpoints"
    ]

    for signal in broad_signals:

        if signal in text:

            snippet = find_snippet(
                text,
                [signal]
            )

            return {
                "value": "Broad",
                "evidence": snippet
            }

    if "api" in text:

        return {
            "value": "Available, breadth unclear",
            "evidence": find_snippet(
                text,
                ["api"]
            )
        }

    return {
        "value": "Unknown",
        "evidence": None
    }


# =========================================================
# Self-serve / gating
# =========================================================

def detect_self_serve(text):

    text = normalize(text)

    positive = [
        "free developer account",
        "free developer edition",
        "developer account",
        "developer sandbox",
        "developer sandbox environment",
        "test account",
        "free trial",
        "sign up",
        "self service",
        "self-serve",
        "create an app",
        "create a developer account"
    ]

    gating = [
        "contact sales",
        "contact our sales team",
        "contact us",
        "partner approval",
        "partnership required",
        "requires approval",
        "admin approval",
        "enterprise plan",
        "paid plan required",
        "paid subscription required",
        "available on enterprise"
    ]

    positive_hits = [
        x for x in positive
        if x in text
    ]

    gating_hits = [
        x for x in gating
        if x in text
    ]

    evidence = []

    for signal in positive_hits[:3]:

        snippet = find_snippet(
            text,
            [signal]
        )

        if snippet:
            evidence.append({
                "type": "self_serve",
                "signal": signal,
                "snippet": snippet
            })

    for signal in gating_hits[:3]:

        snippet = find_snippet(
            text,
            [signal]
        )

        if snippet:
            evidence.append({
                "type": "gating",
                "signal": signal,
                "snippet": snippet
            })

    # Both signals can exist.
    # In that case classify as conditional.
    if positive_hits and gating_hits:

        return (
            "Conditional / plan-dependent",
            evidence
        )

    if positive_hits:

        return (
            "Likely self-serve",
            evidence
        )

    if gating_hits:

        return (
            "Likely gated",
            evidence
        )

    return (
        "Unknown",
        []
    )


# =========================================================
# MCP
# =========================================================

def detect_mcp(text):

    text = normalize(text)

    confirmed = [
        "mcp server",
        "model context protocol",
        "model-context-protocol",
        "official mcp"
    ]

    for signal in confirmed:

        if signal in text:

            return (
                "Confirmed",
                find_snippet(
                    text,
                    [signal]
                )
            )

    return (
        "Not confirmed",
        None
    )


# =========================================================
# Buildability
# =========================================================

def determine_buildability(
    auth,
    api_type,
    self_serve,
    mcp
):

    has_auth = (
        auth != ["Unknown"]
    )

    has_api = (
        api_type != ["Unknown"]
    )

    if has_api and has_auth:

        if self_serve == "Likely gated":

            return (
                "Buildable with access constraint",
                "Credentials/API access are gated."
            )

        if self_serve == "Conditional / plan-dependent":

            return (
                "Buildable with plan constraint",
                "API access depends on account/plan conditions."
            )

        return (
            "Buildable",
            "Public API and authentication mechanism identified."
        )

    if mcp == "Confirmed":

        return (
            "Potentially buildable via MCP",
            "MCP server identified, but API/auth evidence is incomplete."
        )

    return (
        "Needs verification",
        "Insufficient API/authentication evidence."
    )


# =========================================================
# Process one application
# =========================================================

def analyze_file(path):

    with open(
        path,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    combined_text = " ".join(
        source.get("text", "")
        for source in data.get("sources", [])
    )

    auth, auth_evidence = detect_auth(
        combined_text
    )

    api_type, api_evidence = detect_api(
        combined_text
    )

    breadth = detect_breadth(
        combined_text
    )

    self_serve, self_serve_evidence = (
        detect_self_serve(
            combined_text
        )
    )

    mcp, mcp_evidence = detect_mcp(
        combined_text
    )

    buildability, blocker = (
        determine_buildability(
            auth,
            api_type,
            self_serve,
            mcp
        )
    )

    return {
        "id": data["id"],
        "app": data["app"],
        "category": data["category"],
        "website": data["website"],

        "auth_methods": auth,

        "self_serve": self_serve,

        "api_type": api_type,

        "api_breadth": breadth["value"],

        "mcp_available": mcp,

        "buildability": buildability,

        "main_blocker": blocker,

        "evidence": {
            "authentication": auth_evidence,
            "api": api_evidence,
            "self_serve": self_serve_evidence,
            "mcp": mcp_evidence,
            "breadth": breadth["evidence"]
        },

        "evidence_urls": [
            source["url"]
            for source in data.get(
                "sources",
                []
            )
        ],

        "analysis_method":
            "Version 3 signal-based rule analyzer"
    }


# =========================================================
# Run
# =========================================================

files = glob.glob(
    f"{INPUT_DIR}/*.json"
)

print(
    f"Found {len(files)} evidence files."
)

for path in files:

    try:

        result = analyze_file(path)

        filename = os.path.basename(path)

        output_path = os.path.join(
            OUTPUT_DIR,
            filename
        )

        with open(
            output_path,
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
            f"✓ {result['app']}"
        )

    except Exception as error:

        print(
            f"✗ {path}: {error}"
        )


print("\n================================")
print("VERSION 3 ANALYSIS COMPLETE")
print("================================")