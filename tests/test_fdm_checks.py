"""Prove the controls work: clean data passes, and each injected defect is caught."""
import copy
import sys
import unittest
from decimal import Decimal
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fdm_checks as fc  # noqa: E402

CLEAN = fc.load_data(Path(__file__).resolve().parents[1] / "data")
BIG = Decimal("100000000")


def fresh():
    return copy.deepcopy(CLEAN)


def find(d, **m):
    return next(r for r in d["journal_lines"] if all(r[k] == v for k, v in m.items()))


def sibling(d, line, **m):
    return next(r for r in d["journal_lines"] if r["journal_id"] == line["journal_id"] and all(r[k] == v for k, v in m.items()))


class CleanData(unittest.TestCase):
    def test_all_checks_pass(self):
        for name, issues in fc.run_all(fresh()).items():
            self.assertEqual(issues, [], f"{name}: {issues[:3]}")


class DefectsAreCaught(unittest.TestCase):
    def test_unbalanced_journal(self):
        d = fresh()
        find(d, ledger_account="6100")["debit_local"] += Decimal("1.00")
        self.assertTrue(fc.check_journals_balance(d))
        self.assertTrue(fc.check_trial_balance(d))

    def test_missing_required_dimensions(self):
        for acct, field, text in [("6000", "cost_center", "cost center"), ("6000", "fund", "fund"),
                                  ("6400", "project", "project"), ("4300", "project", "project")]:
            d = fresh()
            find(d, ledger_account=acct)[field] = ""
            self.assertTrue(any(f"requires a {text}" in i for i in fc.check_required_worktags(d)), (acct, field))

    def test_missing_counter_company(self):
        d = fresh()
        find(d, ledger_account="1500")["counter_company"] = ""
        self.assertTrue(any("counter company" in i for i in fc.check_required_worktags(d)))

    def test_fund_not_allowed_on_account(self):
        d = fresh()
        find(d, ledger_account="4300")["fund"] = "F-OP"
        self.assertTrue(any("not allowed on account 4300" in i for i in fc.check_worktag_validity(d)))

    def test_fund_does_not_match_project(self):
        d = fresh()
        find(d, ledger_account="6400")["fund"] = "F-OP"
        self.assertTrue(any("does not match project fund" in i for i in fc.check_worktag_validity(d)))

    def test_cost_center_not_valid_for_company(self):
        d = fresh()
        find(d, ledger_account="6000", company_id="UNI")["cost_center"] = "COM-OPS"
        self.assertTrue(any("not valid for company" in i for i in fc.check_worktag_validity(d)))

    def test_hierarchy_cycle_and_unplaced_members(self):
        d = fresh()
        for r in d["hierarchy"]:
            if r["hierarchy_name"] == "CC_CAMPUS" and r["node_id"] == "BAL":
                r["parent_id"] = "BAL-HE"
        self.assertTrue(any("cycle" in i for i in fc.check_hierarchies(d)))
        d = fresh()
        d["hierarchy"] = [r for r in d["hierarchy"] if not (r["hierarchy_name"] == "CC_SECTOR" and r["node_id"] == "WIM-TAFE")
                          and not (r["hierarchy_name"] == "FUND" and r["node_id"] == "F-CAP")]
        issues = fc.check_hierarchies(d)
        self.assertTrue(any("CC_SECTOR" in i and "WIM-TAFE" in i for i in issues))
        self.assertTrue(any("FUND" in i and "F-CAP" in i for i in issues))

    def test_intercompany_mismatch(self):
        d = fresh()
        find(d, ledger_account="2500", company_id="COM")["credit_local"] -= Decimal("500.00")
        find(d, ledger_account="6500", company_id="COM")["debit_local"] -= Decimal("500.00")
        self.assertTrue(fc.check_intercompany(d))

    def test_depreciation_not_matching_register(self):
        d = fresh()
        dep = find(d, ledger_account="6200")
        sibling(d, dep, ledger_account="1710")["credit_local"] += Decimal("1.00")
        dep["debit_local"] += Decimal("1.00")
        self.assertTrue(any("Depreciation" in i for i in fc.check_fixed_assets(d)))

    def test_asset_cost_not_matching_register(self):
        d = fresh()
        d["assets"][0]["cost_local"] = str(Decimal(d["assets"][0]["cost_local"]) + 100)
        self.assertTrue(any("Asset cost" in i for i in fc.check_fixed_assets(d)))

    def test_grant_revenue_ahead_of_funding(self):
        d = fresh()
        rec = next(r for r in d["journal_lines"] if r["ledger_account"] == "2100" and r["debit_local"] > 0)
        rec["debit_local"] += BIG
        sibling(d, rec, ledger_account="4300")["credit_local"] += BIG
        self.assertTrue(fc.check_grant_income_in_advance(d))

    def test_restricted_fund_overspent(self):
        d = fresh()
        sch = find(d, ledger_account="6300")
        sch["debit_local"] += BIG
        sibling(d, sch, ledger_account="1000")["credit_local"] += BIG
        self.assertTrue(fc.check_restricted_fund_balances(d))


if __name__ == "__main__":
    unittest.main()
