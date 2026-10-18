# Capability scout: reusable skills, plugins, MCP servers and guardrail tools

**Read-only pass on 2026-10-18.** Nothing was installed, cloned, run, signed up for or logged in to. Every README, repo and web page was treated as untrusted data.

**Where the facts come from**
- **Stars, last push and license:** the GitHub repository search API, read through the GitHub MCP connector on 2026-10-18. Stars change daily, so treat each count as a snapshot.
- **Release dates and versions:** the PyPI JSON API, the npm registry and GitHub release pages, all read 2026-10-18.
- **Unconfirmed values** are marked `NOT_VERIFIED`. Nothing was guessed.

This pass adds to [02-adoption-matrix.md](../phase-1/02-adoption-matrix.md) and does not repeat it. Items already decided there are only cross-referenced: anthropics/skills (xlsx/pdf/skill-creator), OWASP playbook, ccusage, OTel, pip-audit, Bandit/Semgrep, LiteLLM, Langfuse, the GitHub MCP server, Apify MCP, garak, inspect-ai and Guardrails. The Phase 4 needs come from [07-business-research-plan.md](../phase-1/07-business-research-plan.md): R1 market and competitors, R2 GTA price scan, R5 Canadian regulatory path, R6 supplier longlist, and demand signals for R0.

**Headline findings**
1. **Anthropic's own plugin directory already covers several things we planned to build by hand:** `security-guidance` (hook-based secret and injection warnings), `claude-security`, `session-report` (token and cost HTML report) and `skill-creator` with evals.
2. **No MCP servers exist for Canadian regulators.** Health Canada LNHPD, StatCan WDS and open.canada.ca have free official JSON APIs, which a small read-only T0 script or the built-in WebFetch can call. A third-party MCP wrapper adds risk and no value.
3. **The Amazon, Shopify-admin and Google Trends MCPs are mostly single-developer scrapers or paid hosted services.** The only vendor-official candidates are Shopify's **Catalog MCP** (cross-merchant product search) and Google's **Trends API alpha**, which requires an application.
4. **Two tools from the earlier shortlist now need different decisions.** `detect-secrets` has not released since 2024-05-06, so **gitleaks** is the pick. `llm-guard` is now **archived** on GitHub, so the matrix's NOT_NOW becomes REJECT.

## Summary table

| # | Item | Need | Stars (2026-10-18) | License | Last release / push | Maintainer | Cost | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | Plugin directory (skills/agents/hooks) | 41,943 | Apache-2.0 (each plugin has its own) | push 2026-10-17 | Anthropic (official) | Free | **ADOPT-CANDIDATE** (Anthropic-authored `/plugins` only) |
| 2 | `security-guidance` + `claude-security` plugins (in #1) | Security review, replaces home-made pattern scanner | (repo of #1) | Apache-2.0 (repo) | security-guidance v2.0.14 per marketplace.json; claude-security version `NOT_VERIFIED` | Anthropic | Free; uses plan tokens | **ADOPT-CANDIDATE** |
| 3 | `session-report` plugin (in #1) | Cost/usage tracking | (repo of #1) | Apache-2.0 (repo) | version `NOT_VERIFIED` | Anthropic | Free | **ADOPT-CANDIDATE** (beside ccusage) |
| 4 | [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins) | Phase 4 research/PM/finance/legal workflows | 30,030 | Apache-2.0 | push 2026-10-17 | Anthropic | Free | **ADOPT-CANDIDATE** (adapt, read-only) |
| 5 | [anthropics/claude-code-security-review](https://github.com/anthropics/claude-code-security-review) | PR security review action | 6,414 | MIT | push 2026-02-11 | Anthropic | Needs API key (paid usage) | **WATCH** |
| 6 | Community collections: [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents), [hesreallyhim/awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code), [wshobson/agents](https://github.com/wshobson/agents) | Prompt ideas for subagents | 25,805 / 55,917 / 40,983 | MIT / NOASSERTION / MIT | push 2026-10-11 / 10-18 / 10-17 | Individuals / community | Free | **WATCH** (reference only) |
| 7 | [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | R2 price scan on JS-rendered retailer pages | 38,299 | Apache-2.0 | npm `@playwright/mcp` 0.0.83, 2026-09-28 | Microsoft (official) | Free | **ADOPT-CANDIDATE** (Phase 4, sandboxed) |
| 8 | [Shopify Catalog MCP](https://shopify.dev/docs/agents/catalog/catalog-mcp) | R1/R2 competitor products and prices across Shopify merchants | n/a (hosted) | Shopify terms `NOT_VERIFIED` | Status/date `NOT_VERIFIED`; cites UCP spec 2026-08-25 | Shopify (official) | `NOT_VERIFIED` | **WATCH** |
| 9 | Government of Canada open APIs: [LNHPD](https://health-products.canada.ca/api/documentation/lnhpd-documentation-en.html), [StatCan WDS](https://statcan.gc.ca/eng/developers/wds), [open.canada.ca CKAN](https://open.canada.ca/en/access-our-application-programming-interface-api) | R5 regulatory lookup, R1 market statistics | n/a | Terms `NOT_VERIFIED` (OGL-Canada likely) | Doc pages modified 2018-03-30 / 2025-12-10 / 2021-08-12 | Government of Canada (official) | Free | **ADOPT-CANDIDATE** (plain HTTP, no MCP) |
| 10 | [Open Food Facts API + data dumps](https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/) | R1/R4 competitor ingredients, nutrition, protein per serving | 1,183 (server repo) | ODbL (data), AGPL-3.0 (code) | push 2026-10-18 | Open Food Facts (non-profit) | Free | **ADOPT-CANDIDATE** |
| 11 | [Google Trends API (alpha)](https://developers.google.com/search/apis/trends) | R0/R1 demand signals by country/sub-region | n/a | Google terms `NOT_VERIFIED` | Alpha; announced 2025-07 | Google (official) | `NOT_VERIFIED` | **WATCH** (apply for access) |
| 12 | [gitleaks](https://github.com/gitleaks/gitleaks) | Secret scanner (pre-commit) | 30,077 | MIT | v8.30.1, 2026-03-21; push 2026-09-30 | Vendor-backed OSS | Free | **ADOPT-CANDIDATE** (over detect-secrets) |
| 13 | [promptfoo](https://github.com/promptfoo/promptfoo) | Eval harness + prompt-injection red team | 26,097 | MIT | npm 0.124.1, 2026-10-08 | Vendor (promptfoo Inc.) | Free CLI | **ADOPT-CANDIDATE** (Phase 3 red-team suite) |
| 14 | [Llama Prompt Guard 2](https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/) ([PurpleLlama](https://github.com/meta-llama/PurpleLlama)) | Local prompt-injection classifier for untrusted web text | 4,437 (repo) | Llama 3.2 Community License (model); MIT (CyberSecEval) | push 2026-10-12; `llamafirewall` PyPI 1.0.3, 2025-05-29 | Meta (official) | Free | **WATCH** |
| 15 | [snyk/agent-scan](https://github.com/snyk/agent-scan) (formerly invariantlabs mcp-scan) | Scan our MCP servers, skills and Claude Code config | 3,145 | Apache-2.0 | PyPI `snyk-agent-scan` 0.6.8, 2026-09-29 | Snyk (vendor) | Needs Snyk account/token | **WATCH** |

## Shortlisted items

### 1. anthropics/claude-plugins-official
- **URL:** https://github.com/anthropics/claude-plugins-official
- **Need:** This is the official Claude Code plugin marketplace. Its `marketplace.json` lists 315 plugins. Those under `./plugins` are authored by Anthropic, including `security-guidance`, `claude-security`, `session-report`, `receipts`, `skill-creator`, `hookify`, `pr-review-toolkit`, `code-review` and `plugin-dev`. Those under `external_plugins` and URL sources are from third parties.
- **Stars, license and activity:** 41,943 stars. Apache-2.0 for the repo; each plugin carries its own license. Last push 2026-10-17. Plugin entries have no version field, so we would have to pin by commit SHA.
- **Security:** The README itself says Anthropic does not control what third-party plugins contain and cannot verify that they won't change. Plugins can bundle hooks (local code), MCP servers and scripts. Install only Anthropic-authored plugins, pin the commit, and read every hook and script first.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE**, limited to Anthropic-authored plugins. It is the most trustworthy source for the "reuse, don't build" goal.

### 2. `security-guidance` and `claude-security` plugins (Anthropic)
- **Need:** These could replace our home-made pattern scanners.
  - `security-guidance` (v2.0.14) gives pattern-based warnings on edits, runs an LLM diff review on Stop, and has an agentic commit reviewer that covers injection, XSS, SSRF, hardcoded secrets and "25+ other vulnerability classes".
  - `claude-security` runs a deep vulnerability scan inside the session at a chosen effort tier. It challenges each finding before reporting it and proposes patches but does not apply them.
- **Stars and license:** See #1.
- **Security:** Both run local hooks or agents with repo read access. The LLM review on Stop spends plan tokens on every stop, so the Governor's budget needs to account for it. Neither replaces gitleaks or the PreToolUse deny-list: it is guidance, not enforcement (Section 2A).
- **Cost:** Free plugin; it uses Claude usage.
- **Verdict:** **ADOPT-CANDIDATE.** Use it in place of our regex code-review scanner. Keep hooks and allowlists as the enforcement layer.

### 3. `session-report` plugin (Anthropic)
- **Need:** Cost and usage tracking. It builds an HTML report from local `~/.claude/projects` transcripts covering tokens, cache efficiency, subagents, skills and the most expensive prompts. The sibling `receipts` plugin says that "only counts and project names are sent" to write its report.
- **Security:** Reads local transcripts. Whether `session-report` makes any network call is `NOT_VERIFIED`; read its source before install.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE.** It complements ccusage and the status-line ledger with a per-prompt cost view, and may make a custom HTML cost report unnecessary.

### 4. anthropics/knowledge-work-plugins
- **URL:** https://github.com/anthropics/knowledge-work-plugins
- **Need:** Ready-made Phase 4 workflows:
  - `product-management`: competitor tracking, user-research synthesis.
  - `marketing`: competitor briefs.
  - `finance`: statements, variance.
  - `legal`: compliance and risk triage.
  - `data`: statistics, dashboards.
  - A `small-business` folder.
  - There is no dedicated market-research plugin.
- **Stars, license and activity:** 30,030 stars. Apache-2.0. Last push 2026-10-17.
- **Security:** Several plugins expect connectors (email, CRM, drive). Copy only the skill text, not the connector configs.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE** in ADAPT mode. Lift the competitor-brief and finance-statement skill text into our reviewed agent prompts. It is aimed at Cowork, so check that it fits Claude Code.

### 5. anthropics/claude-code-security-review
- **Need:** Security review on pull requests via a GitHub Action. The same analysis ships as the built-in `/security-review` command.
- **Stars, license and activity:** 6,414 stars. MIT. Last push 2026-02-11, so it is quieter than the plugin route.
- **Security:** Needs a Claude API key stored as a repo secret. The README says it is **not hardened against prompt injection** and should run only on trusted PRs.
- **Cost:** API usage is paid, separate from the plan.
- **Verdict:** **WATCH.** The repo is not on GitHub yet (blocking Q4), and `/security-review` plus `security-guidance` already cover local use.

### 6. Community subagent and skill collections
- **Repos:**
  - VoltAgent/awesome-claude-code-subagents: 25,805 stars, MIT, 100+ subagents.
  - hesreallyhim/awesome-claude-code: 55,917 stars. Curated list of skills, agents, status lines, hooks and plugins.
  - wshobson/agents: 40,983 stars, MIT. A multi-harness plugin marketplace.
- **Need:** Ideas for researcher, test-writer and security-auditor subagent prompts, and discovery of status-line or cost tools.
- **Security:** Maintained by individuals or communities, and contents change daily. Some entries bundle hooks or scripts that execute code. Never install them as a marketplace: copy individual prompt text after review, under our tool allowlists.
- **Verdict:** **WATCH**, as a reference library. awesome-claude-code is the best single discovery index to re-check at each gate.

### 7. microsoft/playwright-mcp
- **URL:** https://github.com/microsoft/playwright-mcp. Also listed in the official plugin directory as `playwright`.
- **Need:** R2 GTA unit-pricing scan on retailer pages that need JavaScript to render. Built-in WebFetch only sees static HTML.
- **Stars, license and release:** 38,299 stars. Apache-2.0. npm `@playwright/mcp` 0.0.83, released 2026-09-28.
- **Security:**
  - Drives a real browser that runs page JavaScript from the internet.
  - Can fill forms and click.
  - Downloads browser binaries on first use.
  - Mitigations: a fresh profile per run (no logged-in sessions or cookies), no credentials, a domain allowlist (supported flags `NOT_VERIFIED`), and a T0 rate limiter. All page text goes into the untrusted-input path.
  - Retailer terms of use need checking before any scraping.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE** for Phase 4 only, after a sandbox test. Prefer static fetch first.

### 8. Shopify Catalog MCP (official, hosted)
- **URL:** https://shopify.dev/docs/agents/catalog/catalog-mcp
- **Need:** R1/R2. It searches products across all Shopify merchants, with filters including `ships_to` and `ships_from` (CA works as a value). This covers many DTC coffee and protein brands.
- **Endpoint and tools:** `POST https://catalog.shopify.com/api/ucp/mcp` (JSON-RPC). Tools: `search_catalog`, `lookup_catalog`, `get_product`. Up to 50 results per page and 1,000 per query.
- **Security:** Each request must reference a published **UCP agent profile** URL. Eligibility, signup, rate limits, cost and GA status are not stated (`NOT_VERIFIED`). The data is read-only, though the tools also return checkout links. Treat product text as untrusted.
- **Verdict:** **WATCH.** It is strong for competitor scans if access turns out to be free and self-serve. Confirm the terms before Phase 4. Shopify's dev-docs MCP (`@shopify/dev-mcp` 1.17.0, 2026-10-16) and the Shopify AI Toolkit (604 stars, MIT) only matter if we build a Shopify store later.

### 9. Government of Canada open APIs (LNHPD, StatCan WDS, open.canada.ca CKAN)
- **What each provides:**
  - **LNHPD:** `https://health-products.canada.ca/api/natural-licences/` with endpoints `productlicence`, `medicinalingredient`, `productpurpose`, `productrisk`, `productdose` and others. JSON or XML, EN/FR, no auth mentioned. Doc page dated 2018-03-30, so it may be stale.
  - **StatCan Web Data Service:** 15 methods, including vector and latest-N-period lookups and full-table CSV/SDMX. Doc modified 2025-12-10. Auth and rate limits not stated.
  - **open.canada.ca CKAN Action API:** GET-only catalogue search for open-data datasets.
- **Need:**
  - R5: which licensed natural health products resemble a caffeinated protein drink, plus their claims, risks and doses. This helps tell the NHP route apart from supplemented foods.
  - R1: StatCan market and consumption statistics.
- **Coverage gap:** No API was found for CFIA labelling or Supplemented Foods rules. Those remain canada.ca guidance pages, read with WebFetch and cited as SRC.
- **Security:** Government-run with no credentials. Licence terms are `NOT_VERIFIED` (Open Government Licence – Canada is likely). A third-party StatCan MCP hosted on onrender.com was found and rejected (see below).
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE** through a tiny read-only T0 Python client with a fixed host allowlist and caching. No MCP needed.

### 10. Open Food Facts (API and data dumps)
- **URL:** https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
- **Need:** R1 and R4 competitor tables: ingredients, nutrition, protein and caffeine on the label, and brands, for RTD coffee and protein products sold in Canada.
- **Licensing and limits:** Data under ODbL, with attribution and share-alike if we redistribute. Server code is AGPL-3.0 (1,183 stars, push 2026-10-18). Reads need no auth but must send a custom User-Agent (`App/Version (email)`). Limits: 15 product reads/min and 10 searches/min per IP. For more than a few hundred products, the docs ask for the CSV/JSONL dumps instead.
- **Security:** Crowdsourced data, so label every value as `SRC-OFF`, unverified until checked against the brand's own page. Use a project email, not a personal one, in the User-Agent.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE.** Download the dump once and filter offline with T0 or T1 (Ollama). Several community OFF MCPs exist, but they are not needed.

### 11. Google Trends API (alpha)
- **URL:** https://developers.google.com/search/apis/trends
- **Need:** R0/R1 demand signals across countries and sub-regions (for example Ontario against the US and UK). It gives consistently scaled data over a rolling 5 years at daily, weekly, monthly or yearly granularity.
- **Status:** Alpha with application-based access. Google prioritizes applicants with clear use cases. Pricing and terms `NOT_VERIFIED`.
- **Security:** Official, so no scraping. Credentials would be a Google API key or OAuth (`NOT_VERIFIED`).
- **Verdict:** **WATCH.** Apply now; it is cheap to ask. Until access arrives, use the public trends.google.com UI manually and save CSVs as SRC. Community Trends MCPs are rejected (see below).

### 12. gitleaks
- **URL:** https://github.com/gitleaks/gitleaks
- **Need:** Secret scanner for pre-commit and CI. The matrix said "gitleaks or detect-secrets, pick one".
- **Stars, license and release:** 30,077 stars. MIT. Latest release v8.30.1 on 2026-03-21 (GitHub releases page); last push 2026-09-30.
- **Comparison:**
  - detect-secrets: Apache-2.0, 4,652 stars, last PyPI release **1.5.0 on 2024-05-06**.
  - trufflehog: 28,558 stars, AGPL-3.0. Verifies secrets by calling live provider APIs, which is a network action.
- **Security:** A single Go binary with no network needed for scanning. Pin by release checksum.
- **Cost:** Free.
- **Verdict:** **ADOPT-CANDIDATE.** Pick gitleaks; this settles the matrix's open choice.

### 13. promptfoo
- **URL:** https://github.com/promptfoo/promptfoo
- **Need:** Declarative eval harness and prompt-injection red-team suite that can target Ollama `qwen2.5:3b` and Claude. It could replace a home-made injection test runner.
- **Stars, license and release:** 26,097 stars. MIT. npm 0.124.1 released 2026-10-08; push 2026-10-18.
- **Security:**
  - An npm package with a large dependency tree. Pin it and run it in an isolated directory.
  - Some red-team plugins generate attacks with a remote model, which can spend API credit.
  - Whether telemetry is on by default and how to disable it is `NOT_VERIFIED`. Check the docs before first run.
  - Do not use the cloud sharing features.
- **Cost:** Free CLI; there is a paid cloud tier.
- **Verdict:** **ADOPT-CANDIDATE** for the Phase 3 adversarial suite. Already "INVESTIGATE FURTHER" in the matrix; the evidence here supports moving it forward.

### 14. Llama Prompt Guard 2 (Meta PurpleLlama)
- **URLs:** https://github.com/meta-llama/PurpleLlama · model cards at llama.com
- **Need:** A small local classifier (86M and 22M variants) that flags prompt-injection and jailbreak text in scraped web pages before an agent reads them. It could replace regex-based injection pattern lists.
- **Stars, license and activity:** PurpleLlama has 4,437 stars and its last push was 2026-10-12. The model is under the Llama 3.2 Community License; CyberSecEval and CodeShield are MIT. `llamafirewall` on PyPI: 1.0.3, 2025-05-29, with no newer release.
- **Security:**
  - The Hugging Face weights are gated: a login and licence acceptance are needed, which is an approval item.
  - It runs locally and offline after download.
  - It is a detector, not a boundary: false negatives are expected, so our allowlists stay.
  - Running it on an M1 with 8 GB alongside Ollama is likely fine for the 22M model (`NOT_VERIFIED`).
- **Verdict:** **WATCH.** Test it in Phase 3 against our injection corpus next to promptfoo results.

### 15. snyk/agent-scan (formerly mcp-scan)
- **URL:** https://github.com/snyk/agent-scan
- **Need:** Scans MCP servers, skills and Claude Code configs for tool poisoning, toxic flows and malicious skills. Useful before adopting any plugin from #1 or #6.
- **Stars, license and release:** 3,145 stars. Apache-2.0. PyPI `snyk-agent-scan` 0.6.8 released 2026-09-29; the old `mcp-scan` package stopped at 0.4.3 (2026-03-02).
- **Security:**
  - **Sends tool descriptions and skill content to Snyk's API.** Secrets are said to be redacted.
  - Needs a `SNYK_TOKEN` account.
  - **Starts stdio MCP servers** to read their tools; it asks for consent interactively, and the README recommends a sandbox.
  - No documented offline mode.
- **Cost:** Needs a Snyk account. Free-tier terms `NOT_VERIFIED`.
- **Verdict:** **WATCH.** Use it only if you approve sending our skill text to Snyk. Otherwise rely on a manual review checklist plus the OWASP MCP-server-review play.

## Rejected or skipped

| Item | Stars (2026-10-18) | Reason |
|---|---|---|
| affaan-m/ECC | 282,661 | Huge third-party harness with its own memory, hooks and "instincts". It would overlap and conflict with our hooks, memory and governance, and its attack surface is too broad to review. |
| thedotmack/claude-mem | 101,449 | External memory store. The matrix already rejects this class: memory must stay canonical and versioned in the repo. |
| cc-switch, OmniRoute, CLIProxyAPI, free-claude-code | 145,604 / 77,795 / 55,552 / 61,310 | Proxy or route credentials through third parties; terms-of-service and credential risk. |
| x1xhlol/system-prompts…, asgeirtj/system_prompts_leaks | 144,075 / 69,821 | Not a capability; IP and provenance concerns. |
| Community Amazon MCPs (apiguru-app/amazon-scraper-v2, rigwild/mcp-server-amazon, HasData/amazon-mcp; Fewsats/amazon-mcp **archived**) | 220 / 54 / 10 / 81 | Individual or vendor scrapers. Some can **purchase** products. Amazon terms risk. For Amazon demand, use the official `amazon-selling-partner` plugin only once we have a seller account (needs Seller Central OAuth, in beta). |
| Community Shopify admin MCPs (GeLi2001/shopify-mcp, others) | 236 and below | Need a store admin token; we have no store. Catalog MCP (#8) covers research. |
| trendsmcp-ai/Trends-MCP and google-trends-mcp | 44 / 14 | Hosted paid service: 100 requests/month free, then USD 19–199/month. Upstream sources not disclosed. |
| jmanek/google-news-trends-mcp | 88 | Individual maintainer, uses Google RSS endpoints. Low value next to the official alpha API and manual CSV export. Could be revisited. |
| HasData google-trends-mcp / amazon-mcp | 5 / 10 | Paid scraping-API wrappers, new repos. |
| Bright Data MCP (brightdata/brightdata-mcp) | 2,679 | Paid, and its stated features include anti-bot detection evasion, which is not "polite scraping". |
| Firecrawl MCP (firecrawl/firecrawl-mcp-server) | 7,627 (MIT, npm 3.30.3, 2026-10-17) | Official and active, but needs an API key and cloud credits (free tier `NOT_VERIFIED`). Duplicates Apify (already on the device) and Playwright. Fallback only. |
| MCP reference `fetch` server (modelcontextprotocol/servers; PyPI `mcp-server-fetch` 2026.10.10) | 91,335 (repo) | Obeys robots.txt and blocks private IPs by default. It duplicates Claude Code's built-in WebFetch, which also refused a robots-disallowed page during this pass. Only useful for a non-Claude MCP client. |
| Community StatCan MCP (mcp-statcan.onrender.com) | `NOT_VERIFIED` | Third-party hosted, unverified operator; the official WDS API is simpler. |
| protectai/llm-guard | 3,215, **archived** | Archived. Change the matrix entry from NOT_NOW to REJECT. |
| Yelp/detect-secrets | 4,652 | Last release 2024-05-06; gitleaks chosen instead. |
| trufflehog | 28,558 | AGPL-3.0; verification makes live network calls to providers. Overkill for one repo. |
| Exa, Tavily, You.com, Zyte, Nimble plugins (official directory, third-party) | n/a | Paid search or scraping APIs; built-in WebSearch/WebFetch plus Apify cover Phase 4 within budget. |
| garak, inspect_ai | 9,608 / 3,030 | Already in the matrix: garak 0.17.1 (2026-10-16) remains INVESTIGATE; inspect-ai 0.3.281 (2026-10-15, MIT) remains NOT_NOW. |
| modelcontextprotocol/registry | 7,372 | Discovery registry only, not a tool. Useful for re-checking for official servers at each gate. |
| Supplier / co-packer directory MCPs | none found | No credible MCP for co-packer directories. R6 stays manual web research plus Apify under approval. |

## Sources
- GitHub repository search API via the GitHub MCP connector, queried 2026-10-18. Source for every star count, `pushed_at` and SPDX license above.
- https://raw.githubusercontent.com/anthropics/claude-plugins-official/main/.claude-plugin/marketplace.json (plugin list, authors, security-guidance v2.0.14)
- https://github.com/anthropics/claude-plugins-official
- https://github.com/anthropics/knowledge-work-plugins
- https://github.com/anthropics/claude-code-security-review
- https://github.com/VoltAgent/awesome-claude-code-subagents · https://github.com/hesreallyhim/awesome-claude-code · https://github.com/wshobson/agents
- https://github.com/microsoft/playwright-mcp · https://registry.npmjs.org/@playwright/mcp
- https://shopify.dev/docs/agents/catalog/catalog-mcp · https://registry.npmjs.org/@shopify/dev-mcp
- https://health-products.canada.ca/api/documentation/lnhpd-documentation-en.html
- https://statcan.gc.ca/eng/developers/wds
- https://open.canada.ca/en/access-our-application-programming-interface-api
- https://www.canada.ca/en/health-canada/services/food-nutrition/supplemented-foods/share-information.html
- https://openfoodfacts.github.io/documentation/docs/Product-Opener/api/
- https://developers.google.com/search/apis/trends · https://developers.google.com/search/blog/2025/07/trends-api
- https://github.com/gitleaks/gitleaks/releases
- https://pypi.org/pypi/detect-secrets/json · https://pypi.org/pypi/garak/json · https://pypi.org/pypi/inspect-ai/json · https://pypi.org/pypi/llamafirewall/json · https://pypi.org/pypi/mcp-server-fetch/json · https://pypi.org/pypi/snyk-agent-scan/json · https://pypi.org/pypi/mcp-scan/json
- https://registry.npmjs.org/promptfoo · https://registry.npmjs.org/firecrawl-mcp · https://registry.npmjs.org/@apify/actors-mcp-server
- https://github.com/meta-llama/PurpleLlama · https://www.llama.com/docs/model-cards-and-prompt-formats/prompt-guard/
- https://github.com/snyk/agent-scan
- https://raw.githubusercontent.com/modelcontextprotocol/servers/main/src/fetch/README.md
- https://github.com/trendsmcp-ai/Trends-MCP · https://github.com/jmanek/google-news-trends-mcp
