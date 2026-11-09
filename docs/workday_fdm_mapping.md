# Mapping the model to Workday's Financial Data Model

> **Caveat.** I have not configured a Workday tenant and hold no Workday certification. This mapping is my reading of how Workday's Financial Data Model (FDM) constructs would carry the design in this repo. Construct names are Workday's as I understand them; setup details marked *confirm* would need checking in a tenant or against Workday documentation before being relied on.

## 1. Construct mapping

| This repo | Workday construct (as I understand it) | Notes |
|---|---|---|
| `companies` (UNI, COM) | **Company**, the legal entity and a balancing worktag | Company hierarchy rolls up to a group node |
| `ledger_accounts` (24) | **Ledger accounts**, with **spend categories** and **revenue categories** as the transaction-facing layer | Operational users usually pick a category, not an account. The repo posts straight to accounts, which is a simplification (section 3) |
| `cost_centers` (10) | **Cost Center** organisations | Each belongs to one company in the model (assumption, *confirm* how this is enforced) |
| `funds` (4) | **Fund** worktag, grouped by fund type | Fund type hierarchy is the FUND tree |
| `projects` (3 research grants) | **Grant** or **Project** worktag; real grant tracking would use Workday's grants management constructs (award, grant, sponsor) | The repo ties a project to one fund and one company, which is the part that matters for validation |
| `counter_company` | **Intercompany** transactions between companies, with Workday's intercompany accounting | The repo's receivable/payable plus reconciliation is the control; Workday's automatic balancing entries would replace the manual pair |
| CC_CAMPUS and CC_SECTOR hierarchies | Two reporting hierarchies over the same cost centers (for example cost center hierarchy plus a custom organisation or a second hierarchy, *confirm* which fits) | See decision DD-03 |
| `allowed_funds`, `requires_*` on accounts | Rules that make a worktag required or restricted for an account or category (*confirm* the exact configuration area) | These are the preventive controls; checks 2 and 3 are the detective test that the rules worked |
| `journals.source` | Journal **source** (for example manual, accounting-center or integration-fed journals) | Gives the module-by-module view in report 10 |
| `budget_lines` (ledger BUDGET-2026) | A **budget** ledger kept separate from actuals, using the same worktags | Report 08 compares it with actuals |
| `users`, `role_assignments`, `sod_conflicts` | **Security groups** and **domain security policies**, with business-process initiate and approve steps | Simulated; see `security_and_controls.md` |

## 2. Balancing worktags

The model balances on **Company only**. That is deliberate, and it is a real design question for a fund-accounting institution:

- **Company only.** Simple. Cash, receivables and payables carry no fund. Fund-level reporting is available for revenue and expense, not for a full balanced fund balance sheet.
- **Company and Fund.** Every line, including cash and payables, needs a fund, and transfers between funds need balancing entries. It supports a true fund-level trial balance and makes restricted-fund cash visible, at the cost of more coding and more clearing activity at every close.

I chose Company only because the stated driver is reporting and control on restricted spend, not fund-level statutory statements. If funders or the auditor require restricted-fund balance sheets, this decision reverses. It is logged as DD-01 in `design_governance.md`. I would settle it in the first design workshop because changing balancing worktags after go-live is expensive. *Confirm* in Workday documentation how balancing worktags are set and what can change later.

## 3. Simplifications to be explicit about

1. **Accounts, not categories.** A real design would define spend and revenue categories mapped to ledger accounts, so a requester never sees the chart of accounts.
2. **Cost center to company** is a one-to-one scope here. Workday organisations can be shared more flexibly, so the rule would be a design choice.
3. **No Workday-specific objects** such as business process definitions, calculated fields or custom reports are built. The repo shows the data design and the tests, not configuration.
4. **Single currency.** Foreign currency, revaluation and translation are not modelled.

## 4. How the model would be loaded

The CSV tables line up with how a Workday implementation stages conversion data: reference data first (companies, accounts, cost centers, funds, projects, hierarchies), then opening balances, then open items. `fdm_checks.py` is the shape of the pre-load validation: run it on each load file before submission, because every rule it enforces is one Workday would otherwise reject or accept silently and pass downstream.
