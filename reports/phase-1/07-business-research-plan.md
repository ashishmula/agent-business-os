# 07 · Business research plan (designed now, run in Phase 4)

Phase 1 only designs this. No market sizes, quotes, MOQs, certifications or supplier contact here.

## 7.1 Decision variables to resolve first (Section 6.1)

| Variable | Default assumption until you decide | Confidence |
|---|---|---|
| First region | **Open: pick the best market(s) by evidence**, not only GTA/Canada. You live in the GTA, so it is the home base for local tests and a strong default for the first physical launch (Ashish, 2026-10-18) | high |
| Capital | CAD 10,000–15,000 portfolio cap (currency assumed CAD), may grow with investors once progress, results and revenue can be shown | high |
| Tools budget | Free tools and APIs preferred; paid tools only when clearly needed | high |
| Format | Open: RTD vs powder (powder likely lower MOQ/freight — hypothesis to test) | low |
| Dairy vs plant | Open | — |
| Protein / caffeine targets | Open; any brief example is not a decision | — |
| Capital available, launch horizon, entity status, existing suppliers | Unknown (Q5) | — |

## 7.2 Coffee-protein workstream (Section 6, dependency-ordered)

| Step | Owner | Tier | Primary sources first | Output | Gate |
|---|---|---|---|---|---|
| R0 Market selection: score candidate markets (Canada, US, UK/EU, others reachable online) on regulatory path, landed cost, shipping, competition, demand signals and ability to run a small test from the GTA | Research Lead (Muse) + Challenger | T4 | Regulators per market, trade/customs sources | Ranked market shortlist; each market gets its own regulatory track | You choose |
| R1 Market, segments, jobs/pains, substitutes | Research Lead (Dot/Muse) | T4 | Official company/product data, StatCan; reviews labeled anecdotal | Segment + competitor table with SRC IDs | — |
| R2 Unit pricing scan (GTA retail + online) | Local Extractor | T1 + T0 | Retailer product pages | Price-per-serving table | — |
| R3 ≥3 niche/positioning routes with kill criteria | Research Lead + Challenger | T4 | R1/R2 evidence | Route cards | You choose |
| R4 RTD vs powder, dairy vs plant comparison | Specialist (product) | T4 | Manufacturer docs | Decision matrix; formulation left to professionals | You |
| R5 Canada regulatory path (Health Canada / CFIA; supplemented foods; caffeine) | Regulatory specialist | T4 floor + different-provider review | canada.ca guidance, Food and Drug Regulations, Supplemented Foods Regulations | Confirmed vs needs-counsel checklist | **Human professional** |
| R6 Manufacturer longlist → shortlist (≥3) | Supplier specialist | T3/T4 | Manufacturer sites, certifications registries | Supplier scorecard (no contact) | Contact needs approval |
| R7 Quality/testing plan | Quality specialist | T4 | Standards, regulator guidance | Test plan; no invented results | Professional |
| R8 Financial model (3+ scenarios, landed COGS, break-even, runway) | Finance specialist + T0 calculators | T4 + T0 | Inputs from R2/R6 labeled ESTIMATED until quoted | Formula-auditable workbook | **CRITICAL** review |
| R9 Go-to-market: B2C vs B2B vs hybrid, demand tests, stop-loss | GTM specialist | T4 | Platform eligibility pages | Experiment plan with budgets | You |
| R10 Roadmap + decision dossier + go/no-go | Orchestrator | T4 | All above | Dossier | **You** |

Section 6A coverage matrix (10 areas: product choices; manufacturer search; brand/trademark/packaging; formulation/spec/IP; production/testing/release; freight/storage/customs; labeling/GTIN; commerce/B2B terms; customer testing/channels; fulfillment/returns) becomes one ledger task group per area in Phase 2, each starting `NOT_STARTED` with an owner, so nothing is summarized away.

## 7.3 Portfolio pipeline (Section 6B)

**Flow:** candidate generation (≥12) → screening scorecard → top 3–5 side-by-side with coffee-protein → one-page brief each → smallest local test → launch / scale / kill gates → next product only when the current one passes or is killed.

**Draft scorecard weights (need your agreement before any scoring, Q5):**

| Factor | Weight |
|---|---|
| Startup capital + MOQ | 12 |
| Regulatory/licensing burden (local, online, interprovincial) | 12 |
| Safety/liability risk + insurance | 8 |
| Gross margin at small volume | 10 |
| Repeat-purchase potential | 8 |
| Real differentiation levers (confirmed by manufacturer) | 8 |
| Local channel fit (markets, cafés, gyms, independents, own store) | 8 |
| Shipping weight/fragility/cost | 6 |
| Shelf life + storage | 6 |
| Competitive saturation | 5 |
| Time to first sale | 5 |
| Portfolio synergy | 4 |
| Your time capacity | 4 |
| Downside if it fails (dead stock) | 4 |
| Seasonality | 0 (tracked, not scored) |
| **Total** | **100** |

**Each candidate records:** `product_id`, customization level (`WHITE_LABEL` / `PRIVATE_LABEL_CUSTOMIZED` / `CUSTOM_FORMULATION`), applicable rule set identified from primary sources (food licensing, natural health product licensing, cosmetic notification, consumer-product labeling — which one applies is researched, not assumed), and a change log for every manufacturer change (source, date, IP owner, regulatory/label impact).

**Templates to create in Phase 2** (`/workflows/templates/product/`): brief, scorecard, supplier checklist, regulatory checklist, test plan, financial-model tab, launch/scale/kill criteria. Adding a product = copying these with a new `product_id`.

**Brand architecture:** umbrella vs per-niche decided in Phase 4 with evidence (shared customers vs. category mismatch).

## 7.4 Acceptance for this workstream

Every number carries an `SRC-*` or `ESTIMATED` label; every regulatory line is either "confirmed from primary source" or "question for counsel/agency"; zero supplier contacts without an `APR-*` record.
