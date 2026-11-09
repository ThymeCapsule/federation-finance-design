# Finance Data Model and Solution Design: Federation University Australia (modelled from public information)

A portfolio project that designs and tests a financial data model for a **real organisation whose next publicly stated Workday phase is Financials**, using only public information plus clearly labelled assumptions.

> **Scope note.** This is an independent exercise, not a Cognizant or Federation University document, and not a Workday configuration. I have no inside knowledge of either organisation. The entity structure, chart of accounts, funds, cost centers and projects are **assumed**, and all amounts are **simulated**. See section 1 of the design doc for what is public and what is assumed.

## Start here

**[docs/solution_design.md](docs/solution_design.md)**: public facts versus assumptions, drivers, scope by process area, entity architecture, dimension design, trade-offs for the executive team, risks, phasing, discovery questions and sources. The code is the working model behind it.

Supporting design documents:

| Document | Covers |
|---|---|
| [workday_fdm_mapping.md](docs/workday_fdm_mapping.md) | Model concepts mapped to Workday FDM constructs; the balancing worktag decision |
| [process_design.md](docs/process_design.md) | Each Workday Financials area: in the repo versus design only, coding rules, controls, dependencies |
| [security_and_controls.md](docs/security_and_controls.md) | Segregation of duties; each control classed as preventive or detective |
| [integrations_and_reporting.md](docs/integrations_and_reporting.md) | Integration inventory and reconciliation; native reporting versus Prism |
| [design_governance.md](docs/design_governance.md) | Decision log, design review checklist, cross-module dependencies, post go-live ownership |
| [engagement_approach.md](docs/engagement_approach.md) | Discovery, sizing drivers, executive trade-off paper |

## What is modelled

| Area | Implementation |
|---|---|
| Entities | University plus a hypothetical controlled commercial entity, with intercompany shared-services charging and elimination |
| Funds | Operating, research, scholarship and capital funds; **each account allows only certain funds** |
| Grants | Cash received in advance, revenue recognised as costs are incurred, tied to a project and the research fund |
| Parallel hierarchies | Cost centers rolled up two ways: by campus and by sector; plus fund type, account and company hierarchies |
| Assets | Register, capex, depreciation, capital grant, tied to the ledger |
| Procure-to-Pay and Order-to-Cash | AP and AR subledgers (supplier and capex invoices, payments, student and commercial billing, receipts) that must tie to the ledger |
| Journal sources | Every journal records its source module, preparer and approver |
| Security | Simulated users, security groups and segregation-of-duties conflict pairs |
| Budgets | A separate budget ledger on the same worktags, compared with actuals |
| Reports | Ten SQL reports: result by campus, sector and fund; intercompany; grant income in advance; budget versus actual; subledger reconciliation; journals by source |

Not built, design only: Expenses, project billing, Accounting Center, Prism, and Workday configuration itself. See [process_design.md](docs/process_design.md).

## Run it

Python 3.10+ only, no third-party packages.

```bash
python generate_data.py                       # build the simulated data
python fdm_checks.py                          # run the thirteen controls (exit code 1 on failure)
python -m unittest -v tests/test_fdm_checks.py
python build_reports.py                       # write reports/*.csv
```

## The thirteen controls

1. Journals balance within each company
2. Required dimensions present (cost center, project, fund, counter company), driven by the account
3. Valid combinations: cost center for company, **fund for account**, **project for fund**, currency
4. Hierarchy integrity: one root, no orphans, no cycles, every member placed in every hierarchy
5. Intercompany receivable equals payable per period (within tolerance)
6. Trial balance nets to zero per company
7. Asset register ties to the ledger (cost and monthly depreciation)
8. Grant revenue never recognised beyond funding received
9. Restricted funds never overspent
10. Every journal has a preparer and an approver who is a different, authorised user
11. No user holds security groups that the segregation-of-duties matrix keeps apart
12. AP and AR subledgers tie to the ledger at every period end
13. The budget ledger obeys the same dimension rules as actuals

The tests confirm clean data passes, then break the data in a specific way for each control (a restricted fund overspent, a fund coded to the wrong account, a journal approved by its preparer, a subledger that no longer ties, a hierarchy cycle, and others) and assert each is caught. See [tests/test_fdm_checks.py](tests/test_fdm_checks.py).

## Limitations

- Randomly generated, illustrative amounts. The campus and sector results mean nothing about Federation's real performance.
- Single currency, no accruals beyond grant income in advance, no tax, no student-system detail.
- The budget is a fixed perturbation of the simulated actuals, so budget variances show the report shape and nothing about performance. Users, roles and conflict pairs are invented.
- No Workday tenant was configured. Mappings to Workday constructs are my reading and are flagged where they need confirming.
- Reports load amounts into SQLite as floats; the controls use `Decimal`. SQL is SQLite and would need minor changes for Snowflake.
