# Design governance

How I would keep a multi-module Workday Financials design coherent: a decision log, a review checklist for designs written by others, a list of cross-module dependencies, and what changes in the operating model after go-live. All entries are for the modelled organisation and are proposals for confirmation, not decisions anyone has made.

## 1. Decision log

| ID | Decision | Alternatives | Why | Cost of reversing later | Owner (role) | Status |
|---|---|---|---|---|---|---|
| DD-01 | Balance on Company only | Company and Fund | Reporting and control on restricted spend is the driver, not fund balance sheets (see `workday_fdm_mapping.md`) | High: touches every line and the load design | Chief Financial Officer or delegate | Proposed. Settle in the first workshop |
| DD-02 | Strict allowed-fund rules on restricted and capital accounts; lighter on general operating | Strict everywhere; none | Protects restricted money where funders and auditors look | Low to medium: rules are configuration | Financial Controller | Proposed |
| DD-03 | Campus and sector as two parallel hierarchies over cost centers | Tag lines with campus and sector; one hierarchy | A restructure is a data change, not re-coding | Medium | Head of Management Accounting | Proposed |
| DD-04 | Treat the commercial entity as a separate Company | A cost center in the University | Legal and tax separation, if a real entity exists (hypothetical here) | High | Chief Financial Officer, tax adviser | Open until entity facts are known |
| DD-05 | Student billing arrives as a detailed feed in the later phase; summary journals first | Detailed from day one | Gets reporting early under savings pressure; accepts less AR detail initially | Medium | Student systems owner | Proposed |
| DD-06 | Users pick spend and revenue categories; categories map to accounts | Users pick accounts | Keeps the chart of accounts out of everyday use | Medium | Financial Controller | Proposed (repo simplifies to accounts) |
| DD-07 | Budget is a separate ledger on the same worktags and rules as actuals | Budget in a spreadsheet or tool outside the ledger | Budget versus actual is a core management report | Medium | Head of Management Accounting | Proposed |
| DD-08 | Segregation-of-duties conflicts need a documented exception and compensating control | Allow silently; forbid absolutely | Small teams cannot always separate every pair | Low | Financial Controller, internal audit | Proposed |

## 2. Review checklist for a design produced by a project team

Questions I would ask of any module design before accepting it, each tied to something this repo tests:

1. Which worktags are required on every line this design creates, and which rule enforces that?
2. Which combinations are invalid (for example fund on account, project on fund), and where are they blocked?
3. Does it post only to leaf cost centers that exist in every reporting hierarchy?
4. Where does this module's balance sit in the ledger, and which report proves they agree (subledger tie-out)?
5. How does it behave across legal entities? What happens to intercompany?
6. Who initiates and who approves, and could one person do both?
7. What does it feed, and what feeds it? Who is told when a feed fails?
8. What changes in the budget and commitment view?
9. What happens when a hierarchy or cost center is restructured mid-year?
10. What is the opening balance and open-item conversion, and how is it tied out?
11. Does it deviate from standard configuration? If so, is it on the exceptions list with an owner?
12. What would I test to prove it works, and how would the test fail?

## 3. Cross-module dependencies and risks

| From | To | Dependency | Risk if missed | Early mitigation |
|---|---|---|---|---|
| Foundation data model | Every module | Worktag set, balancing choice, hierarchies | Late change forces rework everywhere | Settle DD-01 to DD-04 before module design |
| Procure-to-Pay | Assets | Capex invoice creates the asset | Register and ledger diverge | Check 7 and check 12 on every load |
| P2P and Expenses | Projects and grants | Costs carry project and fund | Grant revenue recognised without cost, or the reverse | Check 3 and check 8 |
| Projects | Order-to-Cash | Sponsor invoicing follows billable cost | Under or over-billing sponsors | Billing report reconciled to cost report |
| Student system | Order-to-Cash | Billing feed shape | Revenue accuracy | DD-05 and per-run reconciliation total |
| HCM and Payroll | R2R and Reporting | Costing by cost center and fund | Salary cost in the wrong fund | Costing allocation rules agreed with HR |
| Security | Every module | Roles and approvals | Conflicts introduced by role design | Check 11 on the proposed role matrix before build |
| All modules | Reporting | Hierarchies and worktags | Reports disagree with the ledger | Report tie-out to trial balance |

## 4. Lessons I carry in from the public record

The Federation HCM case study credits standardisation, simplification, minimal customisation, a process for parking non-critical enhancements and internal champions [1]. The principle I would carry to Financials, and apply with more care because finance is where the pressure to customise is greatest: keep a short, owned list of deliberate exceptions (funder-specific reporting, fund rules) and refuse the rest by default.

## 5. Operating model after go-live

| Object | Owner (role) | Change process |
|---|---|---|
| Chart of accounts and categories | Financial Controller | Request, impact check against reports and mappings, sign-off |
| Fund list and rules | Financial Controller with Research Office | Same, plus funder agreement reference |
| Cost center and campus/sector hierarchies | Head of Management Accounting | Restructure as a data change, run check 4 before and after |
| Project and grant set-up | Research Office | Created from award, fund and company validated |
| Security roles | Finance systems lead with internal audit | Run check 11 on every role change; quarterly access review |
| Integrations | Finance systems lead with each source owner | Reconciliation total per run; failures visible |
| Enhancements | A named design authority | Parking list reviewed each quarter |

## Source

[1] Cognizant, case study "Federation University transforms HCM systems to enable a unified platform" (cognizant.com).
