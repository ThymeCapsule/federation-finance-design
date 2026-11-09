# Security and controls

> The security model here is **simulated**: 14 users, 10 security groups and 7 conflict pairs I made up to test the control logic. It is not a Workday security configuration. In Workday this is done with security groups, domain security policies and business-process steps; the repo shows what the rules should be and how to test them.

## 1. Segregation of duties

`data/sod_conflicts.csv` lists pairs of groups one person must not hold together. Check 11 fails if any user holds both halves of a pair.

| Group A | Group B | Risk |
|---|---|---|
| AP_ENTRY | AP_APPROVE | Enter and approve the same supplier invoice |
| AP_ENTRY | SUPPLIER_MASTER | Create a supplier and invoice it |
| SUPPLIER_MASTER | PAYMENT_RELEASE | Create a supplier and release payment |
| AP_APPROVE | PAYMENT_RELEASE | Approve an invoice and release the payment |
| AR_ENTRY | AR_CASH_APPLY | Raise an invoice and apply cash against it |
| JOURNAL_ENTRY | JOURNAL_APPROVE | Post and approve a manual journal |
| BUDGET_ENTRY | BUDGET_APPROVE | Set and approve a budget |

Check 10 applies the journal pair to actual postings: every journal has a recorded preparer and approver, they differ, and the approver is in JOURNAL_APPROVE.

**What I would do differently in a live design.** Small teams cannot always separate every pair. The usual answer is a documented exception with a compensating control (for example, a second reviewer on a monthly exception report), not silently allowing the conflict. The repo has no exception register; I would add one before go-live.

## 2. Preventive versus detective

| # | Control | Type in a live design | Where it would sit |
|---|---|---|---|
| 1 | Journals balance within each company | Preventive | Posting validation (Company is balancing) |
| 2 | Required dimensions present | Preventive | Account and category worktag rules |
| 3 | Valid combinations (cost center to company, fund to account, project to fund) | Preventive | Worktag restriction rules, plus load validation |
| 4 | Hierarchy integrity | Detective | Hierarchy change process and a scheduled check |
| 5 | Intercompany receivable equals payable | Detective | Close calendar |
| 6 | Trial balance nets to zero | Detective | Close calendar |
| 7 | Asset register ties to ledger | Detective | Close calendar, after depreciation run |
| 8 | Grant revenue not beyond funding received | Preventive for the posting rule, detective for the balance | Grant revenue recognition rule, grant balance report |
| 9 | Restricted funds not overspent | Detective, with a preventive budget check if funders require it | Fund balance report, commitment control if adopted |
| 10 | Journal preparer is not the approver; approver is authorised | Preventive | Business-process approval step and security group |
| 11 | No user holds conflicting groups | Detective | Access review each quarter and on every role change |
| 12 | AP and AR subledgers tie to GL | Detective | Close calendar |
| 13 | Budget ledger obeys the same dimension rules | Preventive | Same worktag rules applied to budget entry |

## 3. What the tests show

`tests/test_fdm_checks.py` first proves the clean data passes every control, then breaks the data in a specific way for each control and asserts the control catches it. A control that passes on clean data proves little on its own; the injected defects are what show it can fail.

## 4. Not modelled

Approval thresholds by amount, delegation of authority, emergency access, user lifecycle (joiners, movers, leavers), audit logging, and integration-user permissions beyond a single feed user. Each would be a design workshop topic.
