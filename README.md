# Northpeak Outfitters – Unified Customer 360 & Store Assistant

Demo build for **Northpeak Outfitters**, an outdoor gear retailer with 40 stores, a webshop and the **Summit Club** loyalty programme.
The same customer often exists in up to three systems. This project unifies them in Data Cloud, scores them, builds a
"High-Value At Risk" audience and gives store staff an Agentforce agent that answers *"who is this customer and what should I recommend?"*.

## What's in the box

| Area | Component | Notes |
|---|---|---|
| Sample data | `data/generate.py` → `data/out/` | 200 people, 379 source records (120 CRM, 145 webshop, 114 loyalty), 438 orders, 3,589 web events, 40 products. Fixed seed, deliberate duplicates and personas. |
| CRM | Account, Contacts, Product2 and PricebookEntry records | Loaded from `data/load/` |
| Data Cloud ingestion | IngestAPI connections `Northpeak_Commerce` and `Northpeak_Loyalty` | Schemas: NpEcomCustomer, NpOrder, NpWebEvent, NpLoyaltyMember |
| Data model | Custom DMOs `NP_Order`, `NP_Web_Event`, `NP_Loyalty_Member`, plus mappings to Individual / ContactPointEmail / ContactPointPhone | Relationships to Individual: `force-app/main/default/fieldSrcTrgtRelationships` |
| Identity resolution | Ruleset **NPCU**, "Northpeak Customer Unification" | Rules: normalized email, and fuzzy first name + exact last name + E.164 phone |
| Calculated insights | `NP_Customer_LTV__cio`, `NP_Web_Engagement__cio` | Lifetime spend, recency-weighted LTV score, web engagement score |
| Segment | `NP_High_Value_At_Risk` (Dbt, on Unified Individual) | Spend ≥ $1,500, no order in 180 days, ≤ 2 web events in 30 days. Published daily. |
| Agent | `Northpeak_Store_Assistant` (Agent Script, employee agent) | `force-app/main/default/aiAuthoringBundles` |
| Apex | `NP_CustomerProfileService`, `NP_GetCustomerProfile`, `NP_GetRecommendations` (+ tests) | Data Cloud queries via ConnectApi; recommendations from the NP-xxx catalog |
| Access | Permission set `Northpeak_Store_Assistant_Access` | Agent access + Apex classes + Product2 read |
| Tests | `specs/Northpeak_Store_Assistant-testSpec.yaml` | 6 agent test cases |

## Build scripts (`scripts/`)

Run these in order. `np.py` holds the shared helpers and `state.json` records the created IDs.

1. `p3_connections.py` – IngestAPI connections and schemas
2. `p3_streams.py` – data streams
3. `p3_dmos.py` – custom DMOs and DLO→DMO mappings
4. `p3_ingest.py` – stream the sample data
5. `p3_verify.py` – record count checks
6. `p4_verify.py` – unification check against personas
7. `p5_cis.py` / `p5_verify.py` – calculated insights and score checks

Deploy metadata:
```bash
sf project deploy start --source-dir force-app --test-level RunSpecifiedTests --tests NP_CustomerProfileServiceTest -o <org>
sf agent publish authoring-bundle --api-name Northpeak_Store_Assistant -o <org>
sf agent activate --api-name Northpeak_Store_Assistant -o <org>
```

## Results (demo org)
- 379 Northpeak source records → **202 unified profiles** for 200 people. 198 people unified perfectly; 0 of 5 look-alikes were wrongly merged.
- The at-risk segment has **27 members**, including all 25 planted at-risk customers.
- Agent tests: 5 of 6 fully passing.

## Known limitations
- The date windows in the calculated insights and segment are fixed to 2026‑11‑19, because Data Cloud SQL has no current-date function here. Update them for long-running demos.
- Two loyalty records with typo-spelled first names (Khloe/Chloe, Mathew/Matthew) did not merge.
- All emails use the `example.com/.net/.org` domains. All data is fictional.
