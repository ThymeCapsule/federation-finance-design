"""Design-time and data-quality controls for the Financial Data Model.

Each check returns a list of issue strings (empty list = pass).
"""
import csv
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

IC_TOLERANCE_AUD = Decimal("1.00")
TABLES = ["companies", "ledger_accounts", "cost_centers", "projects", "funds", "assets", "fx_rates", "hierarchy", "journal_lines"]


def _read(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_data(folder="data"):
    d = Path(folder)
    data = {n: _read(d / f"{n}.csv") for n in TABLES}
    for r in data["journal_lines"]:
        r["debit_local"] = Decimal(r["debit_local"])
        r["credit_local"] = Decimal(r["credit_local"])
    data["fx"] = {r["currency"]: Decimal(r["rate_to_aud"]) for r in data["fx_rates"]}
    return data


def _ref(r):
    return f"{r['journal_id']} line {r['line_no']}"


def check_journals_balance(data):
    """Every journal must balance within each balancing dimension (Company)."""
    tot = defaultdict(Decimal)
    for r in data["journal_lines"]:
        tot[(r["journal_id"], r["company_id"])] += r["debit_local"] - r["credit_local"]
    return [f"Journal {j} is out of balance for company {c} by {v}" for (j, c), v in sorted(tot.items()) if v != 0]


def check_required_worktags(data):
    """Account-driven requirements: cost center, project, fund, counter company."""
    acc = {a["account_id"]: a for a in data["ledger_accounts"]}
    out = []
    for r in data["journal_lines"]:
        a = acc.get(r["ledger_account"])
        if a is None:
            continue
        if a["requires_cost_center"] == "1" and not r["cost_center"]:
            out.append(f"{_ref(r)}: account {a['account_id']} requires a cost center")
        if a["requires_project"] == "1" and not r["project"]:
            out.append(f"{_ref(r)}: account {a['account_id']} requires a project")
        if a["requires_fund"] == "1" and not r["fund"]:
            out.append(f"{_ref(r)}: account {a['account_id']} requires a fund")
        if a["is_intercompany"] == "1" and a["account_type"] in ("Asset", "Liability") and not r["counter_company"]:
            out.append(f"{_ref(r)}: intercompany account {a['account_id']} requires a counter company")
        if a["is_intercompany"] != "1" and r["counter_company"]:
            out.append(f"{_ref(r)}: counter company set on non-intercompany account {a['account_id']}")
    return out


def check_worktag_validity(data):
    """Values must exist and be valid together: cost center for company, fund for account, project for fund."""
    companies = {c["company_id"]: c["currency"] for c in data["companies"]}
    acc = {a["account_id"]: a for a in data["ledger_accounts"]}
    ccs = {c["cost_center_id"]: c["company_scope"] for c in data["cost_centers"]}
    projects = {p["project_id"]: p for p in data["projects"]}
    funds = {f["fund_id"] for f in data["funds"]}
    out = []
    for r in data["journal_lines"]:
        if r["company_id"] not in companies:
            out.append(f"{_ref(r)}: unknown company {r['company_id']}")
            continue
        a = acc.get(r["ledger_account"])
        if a is None:
            out.append(f"{_ref(r)}: unknown ledger account {r['ledger_account']}")
        if r["currency"] != companies[r["company_id"]]:
            out.append(f"{_ref(r)}: currency {r['currency']} differs from {r['company_id']} functional currency")
        if r["cost_center"]:
            scope = ccs.get(r["cost_center"])
            if scope is None:
                out.append(f"{_ref(r)}: unknown cost center {r['cost_center']}")
            elif scope != r["company_id"]:
                out.append(f"{_ref(r)}: cost center {r['cost_center']} is not valid for company {r['company_id']}")
        if r["fund"]:
            if r["fund"] not in funds:
                out.append(f"{_ref(r)}: unknown fund {r['fund']}")
            elif a and a["allowed_funds"] != "ANY" and r["fund"] not in a["allowed_funds"].split("|"):
                out.append(f"{_ref(r)}: fund {r['fund']} is not allowed on account {a['account_id']}")
        if r["project"]:
            p = projects.get(r["project"])
            if p is None:
                out.append(f"{_ref(r)}: unknown project {r['project']}")
            else:
                if p["company_id"] != r["company_id"]:
                    out.append(f"{_ref(r)}: project {r['project']} belongs to {p['company_id']}, not {r['company_id']}")
                if r["fund"] and p["fund_id"] != r["fund"]:
                    out.append(f"{_ref(r)}: fund {r['fund']} does not match project fund {p['fund_id']}")
        if r["counter_company"] and (r["counter_company"] not in companies or r["counter_company"] == r["company_id"]):
            out.append(f"{_ref(r)}: invalid counter company {r['counter_company']}")
    return out


def check_hierarchies(data):
    """Each hierarchy: one root, no orphans, no cycles, and every member placed."""
    out = []
    by_h = defaultdict(list)
    for r in data["hierarchy"]:
        by_h[r["hierarchy_name"]].append(r)
    for name, rows in by_h.items():
        parent = {r["node_id"]: r["parent_id"] for r in rows}
        roots = [n for n, p in parent.items() if not p]
        if len(roots) != 1:
            out.append(f"Hierarchy {name}: expected 1 root, found {len(roots)}")
        for n, p in parent.items():
            if p and p not in parent:
                out.append(f"Hierarchy {name}: node {n} has missing parent {p}")
            seen, cur = set(), n
            while cur and cur in parent:
                if cur in seen:
                    out.append(f"Hierarchy {name}: cycle detected at node {n}")
                    break
                seen.add(cur)
                cur = parent[cur]
    cc_ids = {c["cost_center_id"] for c in data["cost_centers"]}
    members = {"COMPANY": {c["company_id"] for c in data["companies"]}, "CC_CAMPUS": cc_ids, "CC_SECTOR": cc_ids,
               "FUND": {f["fund_id"] for f in data["funds"]}, "ACCOUNT": {a["account_id"] for a in data["ledger_accounts"]}}
    for name, expected in members.items():
        placed = {r["node_id"] for r in by_h.get(name, [])}
        for m in sorted(expected - placed):
            out.append(f"Hierarchy {name}: member {m} is not placed in the hierarchy")
    return out


def check_intercompany(data):
    """Intercompany receivable at A (counter B) must equal payable at B (counter A), in AUD, per period."""
    cur = {c["company_id"]: c["currency"] for c in data["companies"]}
    net = defaultdict(Decimal)
    for r in data["journal_lines"]:
        if r["ledger_account"] not in ("1500", "2500") or not r["counter_company"]:
            continue
        amt = (r["debit_local"] - r["credit_local"]) * data["fx"][cur[r["company_id"]]]
        period = r["posting_date"][:7]
        key = (period, r["company_id"], r["counter_company"]) if r["ledger_account"] == "1500" else (period, r["counter_company"], r["company_id"])
        net[key] += amt
    return [f"Intercompany mismatch {p} {a}->{b}: net difference {v:.2f} AUD" for (p, a, b), v in sorted(net.items()) if abs(v) > IC_TOLERANCE_AUD]


def check_trial_balance(data):
    """Total debits equal total credits in each company."""
    tot = defaultdict(Decimal)
    for r in data["journal_lines"]:
        tot[r["company_id"]] += r["debit_local"] - r["credit_local"]
    return [f"Trial balance for {c} does not net to zero: {v}" for c, v in sorted(tot.items()) if v != 0]


def check_fixed_assets(data):
    """Asset register must tie to the GL: cost to account 1700, and monthly depreciation to account 6200."""
    periods = sorted({r["posting_date"][:7] for r in data["journal_lines"]})
    exp_dep, reg_cost = defaultdict(Decimal), defaultdict(Decimal)
    for a in data["assets"]:
        cost, life = Decimal(a["cost_local"]), int(a["life_months"])
        charge = (cost / life).quantize(Decimal("0.01"), ROUND_HALF_UP)
        reg_cost[a["company_id"]] += cost
        for p in periods:
            if p > a["acquisition_date"][:7]:
                exp_dep[(a["company_id"], p)] += charge
    gl_dep, gl_cost = defaultdict(Decimal), defaultdict(Decimal)
    for r in data["journal_lines"]:
        net = r["debit_local"] - r["credit_local"]
        if r["ledger_account"] == "6200":
            gl_dep[(r["company_id"], r["posting_date"][:7])] += net
        elif r["ledger_account"] == "1700":
            gl_cost[r["company_id"]] += net
    out = [f"Asset cost for {c}: register {reg_cost[c]} vs GL {gl_cost[c]}" for c in sorted(set(reg_cost) | set(gl_cost)) if reg_cost[c] != gl_cost[c]]
    out += [f"Depreciation {c} {p}: register {exp_dep[(c, p)]} vs GL {gl_dep[(c, p)]}" for c, p in sorted(set(exp_dep) | set(gl_dep)) if exp_dep[(c, p)] != gl_dep[(c, p)]]
    return out


def check_grant_income_in_advance(data):
    """Grant revenue must not be recognised beyond cash received: income in advance (2100) never negative by project."""
    bal = defaultdict(Decimal)
    for r in data["journal_lines"]:
        if r["ledger_account"] == "2100":
            bal[r["project"]] += r["credit_local"] - r["debit_local"]
    return [f"Project {p}: income in advance is negative ({v}); revenue recognised beyond funding received" for p, v in sorted(bal.items()) if v < 0]


def check_restricted_fund_balances(data):
    """Restricted funds must not be overspent: cumulative revenue less expense >= 0 in every period."""
    types = {f["fund_id"]: f["fund_type"] for f in data["funds"]}
    acc_type = {a["account_id"]: a["account_type"] for a in data["ledger_accounts"]}
    by = defaultdict(lambda: defaultdict(Decimal))
    for r in data["journal_lines"]:
        if acc_type.get(r["ledger_account"]) in ("Revenue", "Expense") and types.get(r["fund"]) == "Restricted":
            by[r["fund"]][r["posting_date"][:7]] += r["credit_local"] - r["debit_local"]
    out = []
    for fund, per in sorted(by.items()):
        run = Decimal(0)
        for p in sorted(per):
            run += per[p]
            if run < 0:
                out.append(f"Restricted fund {fund}: cumulative balance negative at {p} ({run})")
                break
    return out


CHECKS = [check_journals_balance, check_required_worktags, check_worktag_validity, check_hierarchies, check_intercompany,
          check_trial_balance, check_fixed_assets, check_grant_income_in_advance, check_restricted_fund_balances]


def run_all(data):
    return {fn.__name__: fn(data) for fn in CHECKS}


if __name__ == "__main__":
    failed = 0
    for name, issues in run_all(load_data()).items():
        print(f"[{'PASS' if not issues else 'FAIL'}] {name}")
        for i in issues[:10]:
            print("     ", i)
        failed += bool(issues)
    raise SystemExit(1 if failed else 0)
