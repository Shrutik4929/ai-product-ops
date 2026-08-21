\# AI Product Ops Research — 100-App Integration Readiness



\## Overview



This project is an evidence-driven research pipeline designed to evaluate

third-party applications for agent-toolkit integration readiness.



The system researches official developer documentation, collects evidence,

analyzes integration characteristics, performs human verification, and

converts the findings into product-level recommendations.



The research covers 100 applications across multiple categories.



\---



\## Problem



When deciding which applications to support as agent toolkits, API

availability alone is not enough.



An integration can be technically possible but still difficult to build

because of:



\- Authentication requirements

\- API access restrictions

\- Account or plan requirements

\- Permission requirements

\- Gated credentials

\- Missing or conflicting documentation

\- Unclear MCP support



The goal of this project is to make those factors explicit and

prioritizable.



\---



\## Research Questions



For each application, the system evaluates:



1\. What authentication methods are available?

2\. Is the application self-serve?

3\. What type of API is available?

4\. How broad is the API?

5\. Is MCP support confirmed?

6\. Is the integration technically buildable?

7\. What is the main implementation blocker?

8\. What evidence supports the classification?



\---



\## Methodology



The pipeline follows:



&#x20;   App Dataset

&#x20;        ↓

&#x20;   Documentation Discovery

&#x20;        ↓

&#x20;   Evidence Collection

&#x20;        ↓

&#x20;   Rule-Based Analysis

&#x20;        ↓

&#x20;   Human Verification

&#x20;        ↓

&#x20;   Final Dataset

&#x20;        ↓

&#x20;   Pattern Analysis

&#x20;        ↓

&#x20;   Product Recommendations



Evidence is stored with source URLs so that classifications can be

reviewed rather than treated as unsupported assumptions.



\---



\## Dataset



The final research dataset contains:



\- 100 applications

\- 14 structured fields

\- Evidence URLs

\- Authentication information

\- Self-service classification

\- API classification

\- MCP status

\- Buildability

\- Main blocker

\- Analysis method



The master dataset is:



`results/final\_master\_dataset.csv`



\---



\## Key Findings



\### Buildability



79 of 100 applications were classified as buildable.



\### MCP



51 of 100 applications had MCP support classified as confirmed.



\### Self-service



30 of 100 applications were clearly classified as self-serve.



32 were conditional on account, plan, permission, or similar requirements.



10 were classified as gated.



28 remained uncertain under the current rules.



\### Easy Wins



26 applications were identified as easy-win candidates using the current

rule:



\*\*Buildable + clearly self-serve\*\*



These candidates provide a practical starting point for integration

prioritization.



\---



\## Main Integration Blockers



The most common blockers identified were:



1\. Public API and authentication mechanism not clearly identified

2\. API access depending on account or plan conditions

3\. Insufficient API or authentication evidence

4\. Credentials or API access being gated

5\. MCP being identified while API/authentication evidence remained incomplete



This suggests that access and authentication clarity can be a larger

source of integration friction than API availability itself.



\---



\## Accuracy and Verification



The analysis was iteratively improved:



| Version | Sample Accuracy |

|---|---:|

| First pass | 22.22% |

| Second pass | 33.33% |

| V3 + human verification | 66.67% |



The accuracy figure is based on a small human-verified sample and should

therefore be treated as a directional quality indicator rather than a

statistically representative benchmark.



An important design principle was to avoid silently guessing when

documentation could not be retrieved or verified.



\---



\## Important Example



Some developer documentation could not be retrieved automatically because

of access restrictions such as HTTP 403 responses.



Instead of treating blocked pages as evidence that an API did not exist,

the system flagged those cases for verification.



This prevents:



\*\*No evidence → False conclusion\*\*



and instead produces:



\*\*No evidence → Verification required\*\*



\---



\## Product Recommendations



\### 1. Prioritize easy wins



Start with applications that combine technical buildability with

self-service access.



\### 2. Separate technical feasibility from commercial access



An integration can be technically buildable while still requiring a

specific plan, account, or permission.



These should be tracked separately.



\### 3. Create an access-readiness score



A future prioritization score could combine:



\- API availability

\- Authentication clarity

\- Self-service availability

\- MCP availability

\- Plan restrictions

\- Evidence quality



\### 4. Turn uncertainty into a workflow



Applications with incomplete evidence should automatically enter a human

verification queue rather than receiving a confident classification.



\### 5. Maintain evidence over time



Developer documentation changes. High-priority integrations should be

periodically rechecked.



\---



\## Project Structure



```text

ai-product-ops/
│
├── agent/
│   ├── targeted_evidence_collector.py
│   ├── smart_evidence_collector.py
│   ├── v3_analyzer.py
│   ├── pattern_analysis.py
│   ├── build_master_dataset.py
│   └── build_case_study.py
│
├── data/
│   └── apps.csv
│
├── results/
│   ├── final_analysis/
│   │   └── 100 app analysis JSON files
│   ├── final_master_dataset.csv
│   ├── final_evidence_dataset.csv
│   ├── pattern_analysis.json
│   ├── human_verified.json
│   └── verification_report.json
│
├── web/
│   └── case_study.html
│
├── README.md
├── requirements.txt
└── .gitignore
