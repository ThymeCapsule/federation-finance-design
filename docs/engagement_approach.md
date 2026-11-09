# Engagement approach and scoping

How I would approach the front end of an engagement of this kind: what to learn first, how to size it, and what an executive trade-off paper would contain. This is a thinking exercise. I have not run or sold a Workday engagement, so the approach below is reasoned from this model and from the public record, not from delivery experience.

## 1. First two weeks: discovery

| Topic | Questions | Output |
|---|---|---|
| Entities and obligations | Which legal entities, and what must each report? | Entity map, reporting calendar |
| Funding and restrictions | Which funders require their own categories or balances? | Fund and reporting requirements list |
| Systems | Which systems feed finance and in what shape? | Integration inventory (see `integrations_and_reporting.md`) |
| Pain points | Where do spreadsheets and manual steps hold the close? | Ranked process list |
| Governance | Who owns the chart, funds, hierarchies after go-live? | Draft operating model |

## 2. What drives size and complexity

The model in this repo is deliberately small. The drivers below are what I would count in the real organisation, with the repo figure only as a reference for scale.

| Driver | Repo | Why it matters |
|---|---|---|
| Legal entities | 2 | Intercompany, balancing, statutory reporting per entity |
| Ledger accounts | 24 | Mapping and conversion effort grows with accounts and legacy codes |
| Cost centers and hierarchies | 10, two reporting views | Hierarchy governance and restructure risk |
| Funds and restriction rules | 4 funds | Rule count drives configuration and testing |
| Grants and projects | 3 | Billing terms, indirect cost recovery, sponsor reporting |
| Inbound feeds | 3 simulated (payroll, billing, intercompany) | Often the largest single source of effort and risk |
| Security roles and SoD pairs | 10 groups, 7 pairs | Design and access testing |
| Reports | 10 | Certified report catalogue and tie-out |
| Conversion | Opening balances only | Open items, history and mappings dominate in practice |

I would not put hours or days against these without client facts and a delivery team's own estimating data. For a proposal I would show ranges tied to the drivers and list what would move them.

## 3. Executive trade-off paper (outline)

1. The decision and why it is needed now.
2. Two or three options, each with what it costs and what it protects.
3. My recommendation and what would change it.
4. Risks and how each is reduced.
5. What I need from the executive, and by when.

The five trade-offs in `solution_design.md` section 9 are written to this shape, with DD-01 (balancing worktags) the one I would take to the executive first because it is the hardest to reverse.

## 4. Delivery assurance

Review designs against the checklist in `design_governance.md`, require each module design to name its tie-out report, and run the controls in `fdm_checks.py` against every load file before it is submitted.
