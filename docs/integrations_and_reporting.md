# Integrations and reporting

## 1. Integration inventory (assumed)

I have no knowledge of Federation University's real landscape beyond the public case study, which says HCM and Payroll are already on Workday and Workday integrations were being moved to AWS [1]. Everything else below is an assumption to confirm in discovery.

| Feed | Direction | Content | Frequency (assumed) | Reconciliation I would require |
|---|---|---|---|---|
| Student system to Financials | In | Student billing and receipts, summarised or detailed | Daily | Billed and received totals per run equal the AR subledger movement |
| HCM and Payroll to Financials | In | Payroll costing journals by cost center and fund | Each pay run | Journal total equals the payroll register costing total |
| Bank and payment files | In and out | Statements, supplier payment files, receipts | Daily | Bank reconciliation; payment file total equals approved invoices |
| Procurement or card feeds | In | Card transactions, if used | Daily or weekly | Feed total equals statement |
| Grants and research systems | In | Award and sponsor data | On change | Award value equals project funding in the ledger |
| Financials to data platform | Out | Ledger, subledgers, hierarchies, budgets | Daily | Row counts and trial balance tie-out after each load |

Design principles I would apply to every feed: a feed carries source identifiers so each journal can be traced back; one reconciliation total per run; failed records are held and visible rather than dropped; and worktags are derived by rule (Accounting Center where it fits) rather than supplied freehand by the sending system.

## 2. Reporting design

The repo already separates **data** from **views**: campus and sector are derived from hierarchies (`sql/00_views.sql`, `v_ancestors`), not tagged on lines, so a restructure is a hierarchy change and not a re-coding exercise.

| Report | Purpose | Decision it supports |
|---|---|---|
| 01 Trial balance | Integrity | Close sign-off |
| 02, 03 Result by campus, by sector | Responsibility | Savings program tracking |
| 04 Fund summary | Restriction | Funder and audit accountability |
| 05, 06 Intercompany and elimination | Group view | Close |
| 07 Grant income in advance | Grant position | Research office reporting |
| 08 Budget versus actual by campus | Performance | In-year management |
| 09 Subledger reconciliation | Integrity | Close sign-off |
| 10 Journals by source | Coverage and control | Design assurance |

### Native reporting or Prism

My starting position, to be tested in design:

- **Operational and close reporting** (trial balance, fund balances, drill to transaction): native Workday reporting. It is in the transaction context and respects security.
- **Blended analysis** (ledger with student, HR or research data from outside Workday) and **large-volume** history: Prism Analytics or an external platform, because that data is not in Financials.
- **Risk to watch:** two sources of truth. Whatever is built downstream must reconcile to the Workday trial balance and say so on the report. The same tie-out idea as check 6 applies.

### Portability

The SQL is SQLite. For a Snowflake or dbt target the hierarchy rollup (`v_ancestors`) and the report queries need only minor syntax changes, and the controls could become dbt tests. That is a build option, not a claim that it has been done.

## Source

[1] Cognizant, case study "Federation University transforms HCM systems to enable a unified platform" (cognizant.com).
