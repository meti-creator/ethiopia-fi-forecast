# Data Enrichment Log — Task 1

## Purpose
This log documents all additions made to `ethiopia_fi_unified_data` beyond the original
starter dataset (43 records: 30 observations, 10 events, 3 targets, plus 14 impact_links).

## Summary of Additions
| Record ID | Type | Indicator | Pillar | Value | Confidence |
|---|---|---|---|---|---|
| REC_0034 | observation | Smartphone Penetration Rate | ACCESS | 15% | medium |
| REC_0035 | observation | Smartphone Ownership Gender Gap | GENDER | 12pp | medium |
| REC_0036 | observation | Telebirr Agent Network Size | ACCESS | 216,000 agents | medium |
| REC_0037 | observation | Mobile Money Agent Transaction Share | USAGE | 17.04% | medium |
| IMP_0015 | impact_link | NFIS-II effect on Account Ownership | ACCESS | (enabling, no point estimate) | medium |

---

## Record Details

### REC_0034 — Smartphone Penetration Rate
- **Source:** GSMA data, cited via Birr Metrics
- **URL:** https://birrmetrics.com/ethiopia-narrows-mobile-gender-gap-to-24-but-smartphone-access-for-women-remains-just-6/
- **Original text:** "Smartphone penetration remains low, at just 15 percent of the population"
- **Confidence:** Medium — secondary source citing GSMA, not the primary GSMA report
- **Why it's useful:** Basic mobile phone ownership is high (86% male / 65% female), but
  smartphone penetration is only 15%. This gap matters because app-based mobile money
  features (vs. USSD) require a smartphone — this indicator helps explain a ceiling on
  deeper digital usage that raw phone-ownership numbers would hide.

### REC_0035 — Smartphone Ownership Gender Gap
- **Source:** Same as above (GSMA via Birr Metrics)
- **Original text:** "only six percent of women own a smartphone compared to 18 percent of men"
- **Confidence:** Medium
- **Why it's useful:** The existing dataset has `GEN_GAP_MOBILE` (basic phone ownership gap,
  24pp). This new indicator shows the smartphone-specific gap is proportionally much wider,
  which is a more precise signal for forecasting app-based Usage adoption by gender.

### REC_0036 — Telebirr Agent Network Size
- **Source:** Shega, citing Ethio Telecom
- **URL:** https://shega.co/news/the-rise-of-mobile-money-in-ethiopia-without-the-agents
- **Original text:** "around 216,000 agents as of June 2024"
- **Confidence:** Medium — journalism source citing operator figures, not a primary Ethio
  Telecom report
- **Why it's useful:** Agent density is flagged in the Additional Data Points Guide (Sheet B)
  as a direct correlate of financial inclusion. This gives a concrete count for Ethiopia to
  benchmark against.

### REC_0037 — Mobile Money Agent Transaction Share
- **Source:** Shega
- **URL:** https://shega.co/news/the-rise-of-mobile-money-in-ethiopia-without-the-agents
- **Original text:** "agent transactions accounted for only 17.04% of total mobile money
  transactions" (FY2023/24); average of 314 transactions per agent per year
- **Confidence:** Medium
- **Why it's useful:** This is the more important half of the agent story. Registered agent
  count (REC_0036) alone overstates real accessibility — most agents are barely used
  (fewer than 1 transaction/day on average). This matches the Additional Data Points
  Guide's explicit warning (Sheet B, item 1) to distinguish *registered* vs. *active*
  infrastructure. Including both numbers together tells a more honest story than either
  alone.

### IMP_0015 — NFIS-II Strategy effect on Account Ownership
- **Parent event:** EVT_0009 (NFIS-II Strategy Launch, 2021-09-01)
- **Source:** Analytical inference by trainee (no external source quote — this connects
  two existing dataset records: the NFIS-II event and the ACC_OWNERSHIP target)
- **Confidence:** Medium
- **Relationship type:** `enabling` (not `direct`) — NFIS-II is Ethiopia's national strategy
  umbrella; it doesn't directly open accounts the way a product launch does, it creates
  policy conditions (e.g. enabling Telebirr, Fayda, Safaricom's entry) under which other
  events operate.
- **Why it's useful:** Before this addition, NFIS-II — the umbrella policy that most other
  events sit under — had zero modeled effect on any indicator, despite having an explicit
  official target (70% Account Ownership by 2025). This fills that gap.
- **Important caveat (documented honestly rather than glossed over):** NFIS-II's official
  target was 70% Account Ownership by 2025. Actual measured progress during this period
  was only 46% → 49% (+3pp, 2021→2024) — far short of the target. I deliberately did **not**
  assign this impact_link a specific `impact_estimate`, and set `evidence_basis: theoretical`
  rather than `empirical`, to avoid overstating a policy effect that the data doesn't
  actually support. This impact_link exists to represent the *coordinating policy layer*,
  not to double-count effects already captured in the Telebirr/Fayda/Safaricom impact_links.

---

## Known Limitations of This Enrichment Pass
- All four new observations are `confidence: medium`, since they come from research/news
  sources citing primary data (GSMA, Ethio Telecom) rather than the primary sources
  themselves. A future pass could try to reach GSMA Intelligence or NBE reports directly.
- This pass focused on ACCESS/USAGE/GENDER enrichment per the guide's "Direct" and
  "Indirect Correlation" sheets. Other pillars (QUALITY, TRUST, DEPTH) remain uncovered,
  consistent with the existing dataset's focus on Access/Usage as the core forecast targets.
- No new **events** were added this pass (only observations + one impact_link). Additional
  events (e.g. specific NBE regulatory directives, additional product launches) are a
  candidate for a future enrichment round if time permits.
  