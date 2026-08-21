import csv
import json
import html
import os


CSV_FILE = "results/final_master_dataset.csv"
PATTERN_FILE = "results/pattern_analysis.json"
OUTPUT_DIR = "web"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "case_study.html")


def esc(value):
    return html.escape(str(value or ""))


# -----------------------------
# LOAD DATA
# -----------------------------

with open(CSV_FILE, "r", encoding="utf-8-sig") as f:
    apps = list(csv.DictReader(f))

with open(PATTERN_FILE, "r", encoding="utf-8") as f:
    patterns = json.load(f)


total = patterns["total_apps"]

buildable = patterns["buildability"].get("Buildable", 0)
needs_verification = patterns["buildability"].get(
    "Needs verification", 0
)

mcp_confirmed = patterns["mcp"].get("Confirmed", 0)
mcp_not_confirmed = patterns["mcp"].get(
    "Not confirmed", 0
)

self_serve = patterns["self_serve"].get(
    "Self-serve", 0
)

conditional = patterns["self_serve"].get(
    "Conditional", 0
)

gated = patterns["self_serve"].get(
    "Gated", 0
)

unknown_access = patterns["self_serve"].get(
    "Unknown", 0
)

easy_wins = patterns.get("easy_wins", [])

categories = patterns.get("categories", {})

blockers = patterns.get("top_blockers", {})


def pct(value):
    return f"{value / total * 100:.0f}%" if total else "0%"


# -----------------------------
# CATEGORY ROWS
# -----------------------------

category_rows = ""

for category, data in categories.items():

    apps_count = data["apps"]
    build_count = data["buildable"]
    mcp_count = data["mcp_confirmed"]
    self_count = data["self_serve"]

    category_rows += f"""
    <tr>
        <td>{esc(category)}</td>
        <td>{apps_count}</td>
        <td>
            <strong>{build_count}/{apps_count}</strong>
            <span class="muted">
                ({build_count/apps_count*100:.0f}%)
            </span>
        </td>
        <td>{mcp_count}/{apps_count}</td>
        <td>{self_count}/{apps_count}</td>
    </tr>
    """


# -----------------------------
# EASY WIN CARDS
# -----------------------------

easy_win_html = ""

for app in easy_wins:

    easy_win_html += f"""
    <span class="tag green">
        {esc(app)}
    </span>
    """


# -----------------------------
# BLOCKER ROWS
# -----------------------------

blocker_html = ""

for blocker, count in list(blockers.items())[:5]:

    width = count / max(blockers.values()) * 100

    blocker_html += f"""
    <div class="bar-row">
        <div class="bar-label">
            <span>{esc(blocker)}</span>
            <strong>{count}</strong>
        </div>

        <div class="bar">
            <div class="bar-fill" style="width:{width:.0f}%"></div>
        </div>
    </div>
    """


# -----------------------------
# APP TABLE
# -----------------------------

app_rows = ""

for app in apps:

    evidence_urls = app.get("evidence_urls", "")

    links = ""

    if evidence_urls:

        for url in evidence_urls.split(";"):

            url = url.strip()

            if url.startswith("http"):

                links += f"""
                <a href="{esc(url)}"
                   target="_blank"
                   class="evidence-link">
                    Evidence ↗
                </a>
                """

    app_rows += f"""
    <tr
        data-search="{esc(
            app.get('app','') + ' ' +
            app.get('category','') + ' ' +
            app.get('buildability','')
        ).lower()}"
    >
        <td class="app-name">
            {esc(app.get("app"))}
        </td>

        <td>{esc(app.get("category"))}</td>

        <td>{esc(app.get("auth_methods"))}</td>

        <td>{esc(app.get("self_serve"))}</td>

        <td>{esc(app.get("api_type"))}</td>

        <td>
            {esc(app.get("mcp_available"))}
        </td>

        <td>
            <span class="status">
                {esc(app.get("buildability"))}
            </span>
        </td>

        <td>
            {esc(app.get("main_blocker"))}
        </td>

        <td>
            {links}
        </td>
    </tr>
    """


# -----------------------------
# HTML
# -----------------------------

page = f"""<!DOCTYPE html>

<html lang="en">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>
AI Product Ops Research — 100 App Integration Readiness
</title>

<style>

:root {{
    --bg: #08090c;
    --panel: #111318;
    --panel2: #171a21;
    --border: #272b35;
    --text: #f4f5f7;
    --muted: #9da3ae;
    --green: #65e6a5;
    --blue: #7da7ff;
    --yellow: #f4c96b;
    --red: #ff7f8b;
}}

* {{
    box-sizing: border-box;
}}

html {{
    scroll-behavior: smooth;
}}

body {{
    margin: 0;
    background:
        radial-gradient(
            circle at 80% 0%,
            #172337 0,
            transparent 35%
        ),
        var(--bg);

    color: var(--text);

    font-family:
        Inter,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    line-height: 1.6;
}}

.container {{
    width: min(1180px, 92%);
    margin: auto;
}}

nav {{
    border-bottom: 1px solid var(--border);
    position: sticky;
    top: 0;
    background: rgba(8,9,12,.88);
    backdrop-filter: blur(14px);
    z-index: 10;
}}

.nav-inner {{
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.logo {{
    font-weight: 800;
    letter-spacing: -.03em;
}}

.nav-links {{
    display: flex;
    gap: 22px;
}}

.nav-links a {{
    color: var(--muted);
    text-decoration: none;
    font-size: 14px;
}}

.nav-links a:hover {{
    color: white;
}}

.hero {{
    padding: 100px 0 70px;
}}

.eyebrow {{
    color: var(--green);
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: .12em;
    font-size: 12px;
}}

h1 {{
    font-size: clamp(42px, 7vw, 78px);
    line-height: .98;
    letter-spacing: -.055em;
    max-width: 900px;
    margin: 18px 0 25px;
}}

.hero p {{
    max-width: 760px;
    font-size: 20px;
    color: var(--muted);
}}

.highlight {{
    color: white;
}}

.kpis {{
    display: grid;
    grid-template-columns:
        repeat(4, 1fr);

    gap: 14px;
    margin-top: 45px;
}}

.kpi {{
    background: linear-gradient(
        145deg,
        var(--panel2),
        var(--panel)
    );

    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 24px;
}}

.kpi-number {{
    font-size: 42px;
    font-weight: 800;
    letter-spacing: -.04em;
}}

.kpi-label {{
    color: var(--muted);
    font-size: 14px;
}}

section {{
    padding: 75px 0;
}}

.section-title {{
    font-size: 34px;
    letter-spacing: -.035em;
    margin-bottom: 10px;
}}

.section-description {{
    color: var(--muted);
    max-width: 720px;
    margin-bottom: 32px;
}}

.insights {{
    display: grid;
    grid-template-columns:
        repeat(3, 1fr);

    gap: 16px;
}}

.card {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
    padding: 26px;
}}

.card h3 {{
    margin-top: 0;
}}

.card p {{
    color: var(--muted);
}}

.number {{
    font-size: 30px;
    font-weight: 800;
    color: var(--green);
}}

.two-col {{
    display: grid;
    grid-template-columns:
        1fr 1fr;

    gap: 20px;
}}

.bar-row {{
    margin: 20px 0;
}}

.bar-label {{
    display: flex;
    justify-content: space-between;
    gap: 20px;
    font-size: 14px;
    color: var(--muted);
}}

.bar {{
    height: 8px;
    background: #242833;
    border-radius: 99px;
    margin-top: 8px;
    overflow: hidden;
}}

.bar-fill {{
    height: 100%;
    background: var(--blue);
    border-radius: inherit;
}}

.tags {{
    display: flex;
    flex-wrap: wrap;
    gap: 9px;
}}

.tag {{
    display: inline-block;
    padding: 7px 11px;
    border-radius: 999px;
    font-size: 13px;
    border: 1px solid var(--border);
    background: var(--panel2);
}}

.tag.green {{
    border-color: #2f7555;
    color: var(--green);
}}

.table-wrap {{
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 16px;
}}

table {{
    width: 100%;
    border-collapse: collapse;
    min-width: 1100px;
}}

th, td {{
    padding: 13px 15px;
    text-align: left;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
    vertical-align: top;
}}

th {{
    background: var(--panel2);
    color: var(--muted);
    position: sticky;
    top: 0;
}}

td {{
    color: #d9dce2;
}}

.app-name {{
    font-weight: 700;
    color: white;
}}

.status {{
    color: var(--green);
}}

.evidence-link {{
    color: var(--blue);
    text-decoration: none;
    white-space: nowrap;
}}

.search {{
    width: 100%;
    background: var(--panel);
    border: 1px solid var(--border);
    color: white;
    padding: 15px 17px;
    border-radius: 12px;
    margin-bottom: 15px;
    font-size: 15px;
    outline: none;
}}

.search:focus {{
    border-color: var(--blue);
}}

.workflow {{
    display: grid;
    grid-template-columns:
        repeat(5, 1fr);

    gap: 10px;
}}

.step {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 14px;
    padding: 20px;
}}

.step-number {{
    color: var(--green);
    font-weight: 800;
}}

.accuracy {{
    display: grid;
    grid-template-columns:
        repeat(3, 1fr);

    gap: 14px;
}}

.accuracy-card {{
    padding: 30px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 18px;
}}

.accuracy-value {{
    font-size: 42px;
    font-weight: 800;
}}

.recommendations {{
    counter-reset: recommendation;
}}

.recommendation {{
    counter-increment: recommendation;
    display: grid;
    grid-template-columns: 55px 1fr;
    gap: 15px;
    padding: 24px 0;
    border-bottom: 1px solid var(--border);
}}

.recommendation::before {{
    content: counter(recommendation);
    width: 42px;
    height: 42px;
    border-radius: 50%;
    display: grid;
    place-items: center;
    background: var(--panel2);
    border: 1px solid var(--border);
    color: var(--green);
    font-weight: 800;
}}

.recommendation h3 {{
    margin: 0;
}}

.recommendation p {{
    color: var(--muted);
    margin-bottom: 0;
}}

.footer {{
    border-top: 1px solid var(--border);
    padding: 45px 0;
    color: var(--muted);
    font-size: 13px;
}}

@media (max-width: 850px) {{

    .kpis,
    .insights,
    .two-col,
    .accuracy {{
        grid-template-columns: 1fr 1fr;
    }}

    .workflow {{
        grid-template-columns: 1fr 1fr;
    }}

    .nav-links {{
        display: none;
    }}
}}

@media (max-width: 600px) {{

    .kpis,
    .insights,
    .two-col,
    .accuracy {{
        grid-template-columns: 1fr;
    }}

    .workflow {{
        grid-template-columns: 1fr;
    }}

    .hero {{
        padding-top: 65px;
    }}
}}

</style>

</head>

<body>

<nav>

<div class="container nav-inner">

<div class="logo">
AI Product Ops Research
</div>

<div class="nav-links">
<a href="#insights">Insights</a>
<a href="#categories">Categories</a>
<a href="#apps">Apps</a>
<a href="#method">Method</a>
</div>

</div>

</nav>


<main>

<!-- HERO -->

<section class="hero">

<div class="container">

<div class="eyebrow">
100-App Integration Readiness Study
</div>

<h1>
Finding the apps that are
<span class="highlight">
actually ready
</span>
for agent toolkits.
</h1>

<p>
An evidence-driven research pipeline evaluating
100 third-party applications across API access,
authentication, self-service availability, MCP support,
and buildability.
</p>

<div class="kpis">

<div class="kpi">
<div class="kpi-number">
{buildable}%
</div>
<div class="kpi-label">
Apps classified as buildable
</div>
</div>

<div class="kpi">
<div class="kpi-number">
{mcp_confirmed}%
</div>
<div class="kpi-label">
MCP confirmed
</div>
</div>

<div class="kpi">
<div class="kpi-number">
{self_serve}%
</div>
<div class="kpi-label">
Clearly self-serve
</div>
</div>

<div class="kpi">
<div class="kpi-number">
{len(easy_wins)}
</div>
<div class="kpi-label">
Easy-win candidates
</div>
</div>

</div>

</div>

</section>


<!-- EXECUTIVE INSIGHTS -->

<section id="insights">

<div class="container">

<h2 class="section-title">
What the research says
</h2>

<p class="section-description">
The research suggests that API availability itself is
usually not the biggest obstacle. Access, credentials,
plan restrictions, and evidence quality create more
friction.
</p>

<div class="insights">

<div class="card">

<div class="number">
{buildable}/{total}
</div>

<h3>
Most apps are technically buildable
</h3>

<p>
{pct(buildable)} of the researched apps were classified
as buildable. This creates a large pool for potential
agent-toolkit expansion.
</p>

</div>


<div class="card">

<div class="number">
{self_serve}/{total}
</div>

<h3>
Self-service is much less common
</h3>

<p>
Only {pct(self_serve)} were clearly self-serve.
{conditional} were conditional on plans or account
requirements, while {gated} were gated.
</p>

</div>


<div class="card">

<div class="number">
{needs_verification}
</div>

<h3>
Evidence quality remains a bottleneck
</h3>

<p>
{needs_verification} apps require additional verification
under the current classification rules, highlighting
where automated research needs human review.
</p>

</div>

</div>

</div>

</section>


<!-- BLOCKERS -->

<section>

<div class="container">

<div class="two-col">

<div>

<h2 class="section-title">
Where integration friction comes from
</h2>

<p class="section-description">
The most common blockers are not simply "no API".
They are uncertainty around credentials, authentication,
and account or plan requirements.
</p>

{blocker_html}

</div>


<div class="card">

<h3>
Product interpretation
</h3>

<p>
The research points toward a prioritization strategy:
start with integrations that are technically buildable
and self-serve, then separately address high-value
integrations where plan or authentication constraints
create friction.
</p>

<h3>
Why this matters
</h3>

<p>
A research system should not treat missing evidence as
a negative result. Instead, uncertainty should become an
explicit signal for human verification or product
outreach.
</p>

</div>

</div>

</div>

</section>


<!-- EASY WINS -->

<section>

<div class="container">

<h2 class="section-title">
26 easy-win candidates
</h2>

<p class="section-description">
These apps were identified by the current rule as both
buildable and clearly self-serve. They form a practical
starting point for prioritization.
</p>

<div class="tags">

{easy_win_html}

</div>

</div>

</section>


<!-- CATEGORY -->

<section id="categories">

<div class="container">

<h2 class="section-title">
Category-level comparison
</h2>

<p class="section-description">
Comparing categories helps identify where integration
effort may have the highest payoff.
</p>

<div class="table-wrap">

<table>

<thead>

<tr>
<th>Category</th>
<th>Apps</th>
<th>Buildable</th>
<th>MCP</th>
<th>Self-serve</th>
</tr>

</thead>

<tbody>

{category_rows}

</tbody>

</table>

</div>

</div>

</section>


<!-- APP DATA -->

<section id="apps">

<div class="container">

<h2 class="section-title">
The 100-app research dataset
</h2>

<p class="section-description">
Every row is backed by the collected research artifacts.
Use the search field to explore the dataset.
</p>

<input
    id="search"
    class="search"
    type="text"
    placeholder="Search app, category, or buildability..."
>

<div class="table-wrap">

<table id="appTable">

<thead>

<tr>
<th>App</th>
<th>Category</th>
<th>Authentication</th>
<th>Self-serve</th>
<th>API</th>
<th>MCP</th>
<th>Buildability</th>
<th>Main blocker</th>
<th>Evidence</th>
</tr>

</thead>

<tbody>

{app_rows}

</tbody>

</table>

</div>

</div>

</section>


<!-- WORKFLOW -->

<section id="method">

<div class="container">

<h2 class="section-title">
How the research system works
</h2>

<p class="section-description">
The workflow was designed to be repeatable rather than
manually researching each application independently.
</p>

<div class="workflow">

<div class="step">
<div class="step-number">01</div>
<h3>Input</h3>
<p>App list and categories.</p>
</div>

<div class="step">
<div class="step-number">02</div>
<h3>Discover</h3>
<p>Find official developer documentation.</p>
</div>

<div class="step">
<div class="step-number">03</div>
<h3>Collect</h3>
<p>Capture evidence and URLs.</p>
</div>

<div class="step">
<div class="step-number">04</div>
<h3>Analyze</h3>
<p>Apply structured classification rules.</p>
</div>

<div class="step">
<div class="step-number">05</div>
<h3>Verify</h3>
<p>Human-review ambiguous results.</p>
</div>

</div>

</div>

</section>


<!-- ACCURACY -->

<section>

<div class="container">

<h2 class="section-title">
Agent accuracy improved through iteration
</h2>

<p class="section-description">
The workflow was tested and refined instead of assuming
that the first automated result was correct.
</p>

<div class="accuracy">

<div class="accuracy-card">

<div class="accuracy-value">
22.22%
</div>

<strong>
First pass
</strong>

<p>
Initial rule-based analysis.
</p>

</div>


<div class="accuracy-card">

<div class="accuracy-value">
33.33%
</div>

<strong>
Second pass
</strong>

<p>
Improved evidence collection and rules.
</p>

</div>


<div class="accuracy-card">

<div class="accuracy-value">
66.67%
</div>

<strong>
V3 + human verification
</strong>

<p>
Final verified sample accuracy.
</p>

</div>

</div>

<p class="section-description"
   style="margin-top:20px">

Important limitation: the accuracy evaluation was based
on a small verified sample, so it should be treated as a
directional quality measure rather than a statistically
representative benchmark.

</p>

</div>

</section>


<!-- RECOMMENDATIONS -->

<section>

<div class="container">

<h2 class="section-title">
Recommended product actions
</h2>

<div class="recommendations">

<div class="recommendation">

<div>
<h3>
Prioritize the 26 easy wins
</h3>

<p>
These apps combine buildability with a clearly
self-serve access model, reducing integration friction
and making them strong candidates for near-term toolkit
development.
</p>
</div>

</div>


<div class="recommendation">

<div>
<h3>
Create an access-readiness score
</h3>

<p>
Combine API availability, authentication clarity,
self-service status, MCP availability, and plan
constraints into one prioritization score.
</p>
</div>

</div>


<div class="recommendation">

<div>
<h3>
Turn uncertainty into a workflow
</h3>

<p>
Apps with missing authentication or API evidence should
automatically enter a human-review queue instead of
being classified from weak evidence.
</p>
</div>

</div>


<div class="recommendation">

<div>
<h3>
Separate technical feasibility from commercial access
</h3>

<p>
A technically buildable integration can still be difficult
to activate. Tracking buildability and access friction as
separate dimensions makes prioritization more actionable.
</p>
</div>

</div>


<div class="recommendation">

<div>
<h3>
Use evidence freshness as a maintenance signal
</h3>

<p>
Developer documentation changes. Re-check high-priority
integrations periodically so the research remains useful
after the initial study.
</p>
</div>

</div>

</div>

</div>

</section>


<!-- LIMITATIONS -->

<section>

<div class="container">

<div class="card">

<h2 class="section-title">
Limitations & responsible interpretation
</h2>

<p>
Automated documentation retrieval can encounter HTTP
403 responses, redirects, dynamic pages, or incomplete
documentation. Those cases were treated as evidence
limitations rather than silently converted into confident
claims.
</p>

<p>
The classification system is rule-based and therefore
cannot perfectly capture every commercial or technical
nuance. Human verification is particularly important for
ambiguous authentication, pricing, and access models.
</p>

<p>
The accuracy progression shown above is based on a small
verified sample and should not be interpreted as a
population-level accuracy estimate.
</p>

</div>

</div>

</section>


</main>


<footer class="footer">

<div class="container">

AI Product Ops Research · 100 applications ·
Evidence-driven integration readiness analysis

</div>

</footer>


<script>

const search = document.getElementById("search");

const rows =
    document.querySelectorAll(
        "#appTable tbody tr"
    );

search.addEventListener(
    "input",
    function () {{

        const query =
            this.value.toLowerCase().trim();

        rows.forEach(
            row => {{

                const text =
                    row.dataset.search || "";

                row.style.display =
                    text.includes(query)
                        ? ""
                        : "none";

            }}
        );

    }}
);

</script>


</body>

</html>
"""


# -----------------------------
# WRITE FILE
# -----------------------------

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    f.write(page)


print("=" * 60)
print("CASE STUDY CREATED")
print("=" * 60)
print(f"Apps included: {len(apps)}")
print(f"Output: {OUTPUT_FILE}")
print()
print("Open the HTML file in your browser.")