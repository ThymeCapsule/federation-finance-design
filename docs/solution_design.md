# Solution Design: Workday Financials for Federation University Australia (modelled from public information)

> **Read this first.** This is an independent portfolio exercise. It is not a Cognizant or Federation University document, I have no inside knowledge of either organisation, and it is not a Workday configuration. The organisation is real, so I separate what is **public** (with sources in section 14) from what I have **assumed**. All amounts in the accompanying dataset are invented and are not Federation's results.

## 1. Public facts versus assumptions

| Topic | Public (source) | Assumed in this model |
|---|---|---|
| Organisation | Regional dual-sector (university and TAFE) institution with campuses in Ballarat, Berwick, Gippsland and Wimmera, plus online offerings [1][2] | Generic delivery units per campus and sector; real faculty and school structure not used |
| Starting point | Finance, HR and payroll relied on manual workarounds, offline data sources, point solutions and outdated infrastructure [1] | n/a |
| Cognizant's role | Cognizant deployed Workday HCM and Payroll; the case study describes Workday Financials as the next major phase, and an AWS migration of Workday integrations to prepare for it [1] | Scope and timing of any Financials program |
| Design principles used on HCM | Standardisation, simplification and minimal customisation; a process to park non-critical enhancements; internal champions [1] | That the same principles would apply to Financials |
| Financial pressure | A 2024 operating loss of about $26.2m after an $81m deficit in 2023 [3]; a program launched in March 2024 to cut ongoing annual expenditure by $40m by 2026 [2] | Impact on finance priorities |
| Legal entities, chart of accounts, funds, projects | Not used | **All of it.** The second company is hypothetical, added to exercise intercompany design |

## 2. Why this organisation

Cognizant's own case study names Workday Financials as the next phase after HCM and Payroll [1]. That makes it a realistic, public example of a finance design problem: a multi-campus, dual-sector public institution moving off fragmented finance processes, under financial pressure, with design principles already agreed on the people side.

## 3. Business drivers and success measures (derived)

| Driver | Measure of success |
|---|---|
| Replace manual workarounds and offline data in finance [1] | Core finance processes run in one platform; spreadsheets removed from the close |
| Cost discipline [2] | Cost center and fund reporting trusted enough to track a savings program |
| Funder and audit accountability | Restricted funds and grants provably not overspent; clear audit trail |
| Platform ready for later phases | Data model that supports student and analytics integration without rework |

## 4. Scope by process area

| Area | Design intent | In the model |
|---|---|---|
| Record-to-Report | Ledger by entity, fund and cost center; close and reconciliations | Journals, trial balance, intercompany, results by campus, sector and fund |
| Procure-to-Pay | Supplier invoices coded to cost center and fund | AP subledger of occupancy and capex invoices and payments (simplified) |
| Grants and research projects | Cash received in advance, revenue recognised as costs are incurred, restricted to the research fund | Income in advance, recognition, grant controls |
| Assets and capital works | Register ties to ledger; capital grants held in a capital fund | Asset register, depreciation, capital grant |
| Order-to-Cash | Student and commercial billing; receipts; AR tied to the ledger | AR subledger, receipts, summary student billing journals (feed itself not in scope) |
| Expenses | Expense reports coded to cost center, fund and project | Design only: see `process_design.md` |
| Projects, project billing, Accounting Center | Cost capture to grants, sponsor billing, rule-based journals from external events | Grants are in the model; billing and Accounting Center are design only |
| Budgets | Budget ledger on the same worktags as actuals | Budget lines and report 08 (simulated) |
| Reporting | Rollups by campus, sector and fund | Ten SQL reports using hierarchies; see `integrations_and_reporting.md` |

## 5. Legal entity and accounting architecture (assumed)

- **University (UNI):** the main entity, carrying nearly all activity.
- **Controlled commercial entity (COM), hypothetical:** included to show intercompany design. Whether a real separate entity is needed is a discovery question.
- **Balancing dimension:** Company. A journal can span both companies but must balance within each.
- **Currency:** single AUD ledger in this model; foreign currency would be added if overseas partner activity requires it.
- **Intercompany:** the University charges shared services to COM with explicit receivable and payable accounts and a counter-company tag, reconciled and eliminated at group level.

## 6. Financial data model

| Dimension | Purpose | Rule in this model |
|---|---|---|
| Company | Legal entity, balancing | On every line |
| Ledger account | Nature of the transaction | Drives which other dimensions are required, and which funds are allowed |
| Cost center | Responsibility for income and cost | Required on every revenue and expense line; each cost center belongs to one company |
| Fund | Source and restriction of resources | Required on every revenue and expense line; **each account allows only certain funds** (e.g. research grant revenue only on the research fund) |
| Project | Research grant or program | Required on grant revenue, research cost and income in advance; the project's fund must match the line's fund |
| Counter company | Intercompany partner | Required on intercompany receivable and payable |
| Campus and Sector | Reporting views | **Derived from two parallel cost center hierarchies, not tagged on lines** |

**Design choice, parallel hierarchies.** Campus and sector are two different groupings of the same cost centers, kept as separate hierarchies. This answers "how is Gippsland doing?" and "how is TAFE doing?" from one set of postings (reports 02 and 03). The cost is governance: two trees to keep complete and consistent, which the hierarchy control checks.

**Design choice, account-fund rules.** Putting allowed funds on the account stops restricted money being coded to general operating spend at the point of posting, which is the kind of error auditors and funders care about.

## 7. Carrying the HCM principles into Financials (hypothesis)

The case study credits standardisation, simplification, minimal customisation, a parking process for non-critical enhancements and internal champions for the HCM result [1]. My starting hypothesis is to keep the same principles for Financials, with a deliberate exception list. Finance is where the pressure to customise is highest (funder-specific reporting, fund rules), so I would define up front which fund and reporting needs justify configuration beyond standard.

## 8. Controls built into the design

Thirteen automated checks stand in for controls a design would specify: balancing per company, required dimensions, valid dimension combinations (cost center to company, fund to account, project to fund), hierarchy integrity, intercompany agreement, trial balance integrity, asset register tie-out, grant revenue not recognised beyond funding received, restricted funds not overspent, journal preparer and approver separation, security-group conflicts, AP and AR subledger tie-out, and budget-ledger dimension rules. In a live design some would be preventive rules at posting and others detective reports in the close calendar. `security_and_controls.md` classifies each. Approval thresholds, delegation and user lifecycle are not modelled.

## 9. Trade-offs I would put to the executive team

1. **Strict fund rules or flexibility.** Strict account-fund rules protect restricted money but add friction when budget holders need to reclassify. I would be strict on restricted and capital funds and lighter on general operating.
2. **One hierarchy or several.** Parallel hierarchies give richer reporting at the price of more governance. Name an owner for each.
3. **Separate entity or cost center for commercial activity.** A separate company gives clean legal and tax separation but adds intercompany work every close. Decide on legal need, not convenience.
4. **Savings program context.** With a cost-reduction target in play [2], early reporting wins (cost center and fund visibility) may matter more than full process coverage on day one. That argues for phasing R2R and reporting early.
5. **Integration with the student system.** Revenue accuracy depends on the student billing feed. Summary journals are simple but hide detail; a detailed feed is richer and costs more to build and reconcile.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Hierarchies drift out of step with the real organisation after restructures | Named owners, integrity check on every change, restructure treated as a data change with sign-off |
| Restricted funds overspent before it is noticed | Preventive account-fund rules plus a fund balance check in the close calendar |
| Legacy balances and mappings migrated incorrectly | Mapping workbook signed off by finance owners; trial balance tie-out at each load |
| Customisation creep under time pressure | Agreed principles and an enhancement parking process, as used on HCM [1] |
| Integration readiness | Sequence infrastructure and integration uplift before go-live, as the case study describes for the AWS migration [1] |

## 11. Suggested phasing (assumed)

1. **Foundation:** entity, chart of accounts, fund and cost center structures; record-to-report, procure-to-pay, assets.
2. **Grants and projects:** research grants, income in advance, project reporting.
3. **Student and integration:** student billing feed, reconciliation, analytics data feeds.

*Rationale:* get the ledger and reporting structure right first, then add the most restricted and audit-sensitive activity, then the heaviest integrations.

## 12. Open questions for discovery

- What is the real entity structure, including any controlled entities and their reporting obligations?
- Which funder or regulator reports must the ledger produce directly, and in what categories?
- Which student, HR and payroll systems feed the ledger, and at what level of detail?
- Do reports need historical restatement when cost center hierarchies change?
- Who owns the chart of accounts, fund list and each hierarchy after go-live?

## 13. Related design documents

| Document | What it covers |
|---|---|
| `workday_fdm_mapping.md` | How this model maps to Workday FDM constructs; balancing worktag decision |
| `process_design.md` | R2R, P2P, O2C, Expenses, Assets, Projects, Project billing, Accounting Center, Budgets, Reporting |
| `security_and_controls.md` | Segregation of duties, preventive and detective classification of the controls |
| `integrations_and_reporting.md` | Integration inventory, reconciliation, native reporting versus Prism |
| `design_governance.md` | Decision log, design review checklist, cross-module dependencies, post go-live ownership |
| `engagement_approach.md` | Discovery, sizing drivers, executive trade-off paper |

## 14. Sources

1. Cognizant, case study "Federation University transforms HCM systems to enable a unified platform" (cognizant.com).
2. Federation University, media release "Federation University 2024 Annual Report tabled in Victorian Parliament", 13 May 2025 (federation.edu.au).
3. The Courier, "Federation University 2024 annual report reveals $26.2m loss" (thecourier.com.au).
