# Finance Data Model and Solution Design: Federation University Australia (modelled from public information)

A portfolio project that designs and tests a financial data model for a **real organisation whose next publicly stated Workday phase is Financials**, using only public information plus clearly labelled assumptions.

> **Scope note.** This is an independent exercise, not a Cognizant or Federation University document, and not a Workday configuration. I have no inside knowledge of either organisation. The entity structure, chart of accounts, funds, cost centers and projects are **assumed**, and all amounts are **simulated**. See section 1 of the design doc for what is public and what is assumed.

## Start here

**[docs/solution_design.md](docs/solution_design.md)**: public facts versus assumptions, drivers, scope by process area, entity architecture, dimension design, trade-offs for the executive team, risks, phasing, discovery questions and sources. The code is the working model behind it.

## What is modelled

| Area | Implementation |
|---|---|
| Entities | University plus a hypothetical controlled commercial entity, with intercompany shared-services charging and elimination |
| Funds | Operating, research, scholarship and capital funds; **each account allows only certain funds** |
| Grants | Cash received in advance, revenue recognised as costs are incurred, tied to a project and the research fund |
| Parallel hierarchies | Cost centers rolled up two ways: by campus and by sector; plus fund type, account and company hierarchies |
| Assets | Register, capex, depreciation, capital grant, tied to the ledger |
| Reports | Result by campus, by sector and by fund; intercompany reconciliation; grant income in advance |

## Run it

Python 3.10+ only, no third-party packages.

```bash
python generate_data.py                       # build the simulated data
python fdm_checks.py                          # run the nine controls (exit code 1 on failure)
python -m unittest -v tests/test_fdm_checks.py
python build_reports.py                       # write reports/*.csv
```

## The nine controls

1. Journals balance within each company
2. Required dimensions present (cost center, project, fund, counter company), driven by the account
3. Valid combinations: cost center for company, **fund for account**, **project for fund**, currency
4. Hierarchy integrity: one root, no orphans, no cycles, every member placed in every hierarchy
5. Intercompany receivable equals payable per period (within tolerance)
6. Trial balance nets to zero per company
7. Asset register ties to the ledger (cost and monthly depreciation)
8. Grant revenue never recognised beyond funding received
9. Restricted funds never overspent

The tests confirm clean data passes, then inject 13 defects (a restricted fund overspent, a fund coded to the wrong account, depreciation that disagrees with the register, a hierarchy cycle, and others) and assert each is caught.

## Limitations

- Randomly generated, illustrative amounts. The campus and sector results mean nothing about Federation's real performance.
- Single currency, no accruals beyond grant income in advance, no tax, no budgets, no student-system detail.
- Reports load amounts into SQLite as floats; the controls use `Decimal`. SQL is SQLite and would need minor changes for Snowflake.
