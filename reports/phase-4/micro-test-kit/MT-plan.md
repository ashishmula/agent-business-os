# Micro-test plan (DEC-0006)

Prepared 2026-10-20 · Builds on R10 §3.3 and §11, R11 (rules check), R12 (events, benchmarks, ads). Every number is from those reports or marked ESTIMATED. Not legal advice.

## In one line
Test whether people want this before spending real money. Step 0 is a small online test, about CAD 300–600 over 2 weeks. Then free samples at 2–3 Toronto events, about CAD 2,500–4,100. Score every result with `./abos microtest <tally.csv>`.

## Step 0: waitlist page + Instagram ads (2 weeks, ≤ CAD 600)
- **Page:** `waitlist-page-draft.html` (not published). It asks two questions, can vs pouch and a fair pouch price, then email plus a CASL consent box. The CASL wording follows R11 §5 [SRC-R11 CASL rows]. Before launch it needs a business name and a mailing address.
- **Ads:** Instagram only, targeted to Toronto. TikTok needs at least about USD 20 a day per ad group, which would use most of a CAD 300 budget [R12 §C].
- **Expected results (ESTIMATED, R12 §C):**
  - Cost per sign-up: CAD 4–40, about CAD 12 in the base case.
  - CAD 600 buys about 50 sign-ups in the base case, or 15 in a bad case.
- **Pass (config/microtest.toml):**
  - Spend ≤ CAD 600.
  - At least 30 sign-ups.
  - Cost per sign-up ≤ CAD 15.
- **No claims before there is proof:**
  - No protein grams and no "energy" or "recovery" wording.
  - "Plant protein" stays generic until the recipe is fixed [R11 §4].
- **Personal data:** emails stay in the email tool, never in the repo. The scorer refuses email and name columns.

## Micro-test: free samples at 2–3 events (6–8 weeks)
- **Targets:**
  - Weekly run clubs that already let drink brands sample. Dupont Run Club hosted Alma Mate and WakeWater [R12 §A].
  - Then one coffee-rave style party: COFFEE RAVE, House Brew, Fresh Ravers or The Coffee Party, whichever has a date [R12 §A].
  - None of these has a published date for Nov 2026–Mar 2027, so each one has to be checked first.
- **What is poured:**
  - Sealed, store-bought Canadian products only. That fits the Toronto "approved source" rule and avoids needing an import licence [R11 §1–2].
  - Benchmarks to taste: brüst, Super Coffee and Premier Protein café latte (milk protein), and OWYN (the only plant-protein coffee drink found) [R12 §B].
  - The tasting set costs about CAD 60–80 (ESTIMATED).
- **What the booth needs [R11 §2]:**
  - A certified food handler at the table the whole time.
  - Protein drinks kept at 4 °C or colder.
  - Single-use cups.
  - A handwashing station if anything is mixed on site.
  - Organizers notify Toronto Public Health at least 30 days ahead, and vendor forms are due 3 weeks before.
  - Toronto parks need a permit for business activity. Whether that covers free samples is UNCLEAR, so pick run clubs that start at a cafe or private venue.
- **Data:** one `tasting-card.md` per person, tallied into `tally-template.csv` format.
- **Pass (config/microtest.toml):**
  - At least 300 samplers.
  - At least 10% scan the QR code.
  - At least 3% sign up.
  - At least 2 organizers invite the booth back.
  - At least 40 people score the drink, and at least 60% of them give it 4 or 5 out of 5.

## Stop rules
- If step 0 fails on both sign-ups and cost per sign-up, rewrite the page and test once more. If it fails again, the overall answer is no-go.
- If the micro-test overall result is FAIL, stop at about CAD 4,000 spent (R10 §5).
- A gate with no data is NOT_TESTED, never PASS.

## Questions for an advisor before the events (from R11)
1. Does a run club or coffee rave count as a "food exhibition / trade show or similar event" for the 100 kg sample exemption? (Only matters if you import.)
2. Does a whey-based powder count as "dairy" for the exemption from writing a food safety plan?
3. Does handing out free samples in a Toronto park need a parks permit?
4. Can a PO box be the CASL mailing address?
