# Step 0 launch kit (APR-0006)

Approved 2026-10-20 with one condition from Ashish: **no money is spent until he OKs the exact amount.**
Claude makes no accounts and pays nothing.

## 1. Pick a working name (Ashish)
Quick web check, 2026-10-20. This is not a trademark search.

| Name | Idea | Quick check |
|---|---|---|
| **Daybeat** | daytime + beat | No coffee brand found in a web search |
| **Kickdrum** | the techno kick drum | No coffee or protein brand found |
| **Four/Four** | 4/4, the techno time signature | "4/4 Seasons Coffee" is a café in Tokyo. Probably fine in Canada, but weaker |
| ~~Bassline~~ | | Already taken by a coffee roaster (Bassline Coffee) |

Before you settle on a name, search it on the Canadian Trademarks Database (ised-isde.canada.ca, free, no account). Also check that the Instagram handle and the .ca web address are free.

## 2. Set up the free tools (Ashish, about 30 minutes)
1. **Email form:** create a Google Form using your Google account. Add the two questions from the page draft (can or pouch, and pouch price). Add an email field. Add a required consent checkbox using this wording:
   "Yes, email me updates and launch offers from [Name], [mailing address], [email]. You can unsubscribe at any time."
   The form keeps the emails. Only daily totals go into the repo.
2. **Page:** Claude fills the name and the form link into `waitlist-page-draft.html`. You then publish it free on GitHub Pages from a new public repo, or skip the page and use the Google Form link on its own.
3. **Instagram:** create a business account for the name and connect it to Meta Business Suite. Add a card only when you're ready to approve spend.

## 3. Ad copy (Claude, ready now)
Each ad runs as a square image or a 9:16 story: acid-green and magenta flyer art, with the headline written large.

- **A: the scene.** "Toronto's mornings got loud. Cold brew + plant protein for coffee raves and run clubs. Join the waitlist for the first drop."
- **B: no-alcohol angle.** "No hangover, all bass. A coffee made for sober daytime raves. Get on the list."
- **C: can or pouch.** "Grab-and-go can at the event, or a pouch for home? Vote and get first access."

Rules for every ad:
- No protein grams.
- No "energy" or "recovery" wording.
- No alcohol imagery.
- No health claims.

## 4. Ad setup when spend is approved (draft)
- **Audience:** Toronto plus 10 km, ages 19–35. Interests: electronic music, techno, running clubs, cold brew.
- **Budget:** Meta's daily budget (CAD 21 a day for 14 days ≈ CAD 300, or CAD 43 a day ≈ CAD 600) plus a CAD 600 account spending limit as a hard stop.
- **Format:** run all three ads, and let Meta move money toward the best one after 3 days.
- **Tracking:** each day, copy the spend and sign-up totals into a CSV with one row per day, `ads,,,,<signups>,,,<spend>`. Run `./abos microtest` on it. Pass means at least 30 sign-ups at no more than CAD 15 each.
