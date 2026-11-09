"""Generate SIMULATED finance data for a model of Federation University Australia.

The structure is based on public information (see docs/solution_design.md, section 1) plus clearly
labelled assumptions. All amounts are invented. They are NOT Federation's results.
"""
import calendar
import csv
import random
import zlib
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

random.seed(11)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)


def q(x):
    return Decimal(x).quantize(Decimal("0.01"), ROUND_HALF_UP)


def write(name, rows, fields):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


# ---- Legal entities (the second is a HYPOTHETICAL controlled commercial entity, to exercise intercompany) ----
COMPANIES = [
    dict(company_id="UNI", name="University (modelled)", country="AU", currency="AUD"),
    dict(company_id="COM", name="Controlled commercial entity (hypothetical)", country="AU", currency="AUD"),
]
CUR = {c["company_id"]: c["currency"] for c in COMPANIES}
FX = {"AUD": Decimal("1")}

# ---- Funds ----
FUNDS = [
    dict(fund_id="F-OP", name="General Operating", fund_type="Unrestricted"),
    dict(fund_id="F-RES", name="Research and Grants", fund_type="Restricted"),
    dict(fund_id="F-RST", name="Donations and Scholarships", fund_type="Restricted"),
    dict(fund_id="F-CAP", name="Capital Works", fund_type="Capital"),
]

# ---- Ledger accounts: (id, name, type, normal, req_cc, req_project, req_fund, intercompany, allowed_funds) ----
A = [
    ("1000", "Cash", "Asset", "D", 0, 0, 0, 0, "ANY"),
    ("1100", "Student and Other Receivables", "Asset", "D", 0, 0, 0, 0, "ANY"),
    ("1500", "Intercompany Receivable", "Asset", "D", 0, 0, 0, 1, "ANY"),
    ("1700", "Property, Plant and Equipment at Cost", "Asset", "D", 1, 0, 0, 0, "ANY"),
    ("1710", "Accumulated Depreciation", "Asset", "C", 0, 0, 0, 0, "ANY"),
    ("2000", "Trade Payables", "Liability", "C", 0, 0, 0, 0, "ANY"),
    ("2100", "Grant Income in Advance", "Liability", "C", 0, 1, 1, 0, "F-RES"),
    ("2500", "Intercompany Payable", "Liability", "C", 0, 0, 0, 1, "ANY"),
    ("3000", "Accumulated Funds", "Equity", "C", 0, 0, 0, 0, "ANY"),
    ("4000", "Commonwealth Government Funding", "Revenue", "C", 1, 0, 1, 0, "F-OP"),
    ("4050", "State Government Funding (TAFE)", "Revenue", "C", 1, 0, 1, 0, "F-OP"),
    ("4100", "Student Contributions and Fees", "Revenue", "C", 1, 0, 1, 0, "F-OP"),
    ("4200", "International and Commercial Fees", "Revenue", "C", 1, 0, 1, 0, "F-OP"),
    ("4300", "Research Grant Revenue", "Revenue", "C", 1, 1, 1, 0, "F-RES"),
    ("4400", "Capital Grants", "Revenue", "C", 1, 0, 1, 0, "F-CAP"),
    ("4500", "Shared Services Income", "Revenue", "C", 1, 0, 1, 1, "F-OP"),
    ("4600", "Donations and Bequests", "Revenue", "C", 1, 0, 1, 0, "F-RST"),
    ("6000", "Academic Salaries", "Expense", "D", 1, 0, 1, 0, "F-OP"),
    ("6050", "Professional Staff Salaries", "Expense", "D", 1, 0, 1, 0, "F-OP"),
    ("6100", "Occupancy and Utilities", "Expense", "D", 1, 0, 1, 0, "F-OP"),
    ("6200", "Depreciation Expense", "Expense", "D", 1, 0, 1, 0, "F-OP"),
    ("6300", "Scholarships and Grants Paid", "Expense", "D", 1, 0, 1, 0, "F-RST|F-OP"),
    ("6400", "Research Costs", "Expense", "D", 1, 1, 1, 0, "F-RES"),
    ("6500", "Shared Services Charge", "Expense", "D", 1, 0, 1, 1, "F-OP"),
]
ACC_ROWS = [dict(account_id=a, name=n, account_type=t, normal_balance=nb, requires_cost_center=rc,
                 requires_project=rp, requires_fund=rf, is_intercompany=ic, allowed_funds=af)
            for a, n, t, nb, rc, rp, rf, ic, af in A]

# ---- Cost centers: (id, name, company scope, campus, sector). Generic units: the real org structure is NOT public here. ----
CCS = [
    ("BAL-HE", "Higher Education Delivery - Ballarat", "UNI", "BAL", "HE"),
    ("BAL-TAFE", "TAFE Delivery - Ballarat", "UNI", "BAL", "TAFE"),
    ("GIP-HE", "Higher Education Delivery - Gippsland", "UNI", "GIP", "HE"),
    ("GIP-TAFE", "TAFE Delivery - Gippsland", "UNI", "GIP", "TAFE"),
    ("BER-HE", "Higher Education Delivery - Berwick", "UNI", "BER", "HE"),
    ("WIM-TAFE", "TAFE Delivery - Wimmera", "UNI", "WIM", "TAFE"),
    ("ONL-HE", "Online Delivery", "UNI", "CEN", "HE"),
    ("RES-OFF", "Research Office", "UNI", "CEN", "RES"),
    ("COR-SVC", "Corporate and Student Services", "UNI", "CEN", "CORP"),
    ("COM-OPS", "Commercial Operations", "COM", "CEN", "COM"),
]
CC_ROWS = [dict(cost_center_id=i, name=n, company_scope=s) for i, n, s, _, _ in CCS]
HE = ["BAL-HE", "GIP-HE", "BER-HE", "ONL-HE"]
TAFE = ["BAL-TAFE", "GIP-TAFE", "WIM-TAFE"]
CAMPUS_CC = {"BAL": "BAL-HE", "GIP": "GIP-HE", "BER": "BER-HE", "WIM": "WIM-TAFE"}

PROJECTS = [
    dict(project_id="P-RES-01", name="Industry Research Partnership A (illustrative)", company_id="UNI", fund_id="F-RES"),
    dict(project_id="P-RES-02", name="Competitive Research Grant B (illustrative)", company_id="UNI", fund_id="F-RES"),
    dict(project_id="P-RES-03", name="Regional Innovation Grant C (illustrative)", company_id="UNI", fund_id="F-RES"),
]

# ---- Hierarchies: parallel cost center trees (campus and sector), funds, accounts, companies ----
H = []
def node(h, nid, parent, ntype, name):
    H.append(dict(hierarchy_name=h, node_id=nid, parent_id=parent, node_type=ntype, node_name=name))

node("COMPANY", "GRP", "", "root", "Group (modelled)")
for c in COMPANIES:
    node("COMPANY", c["company_id"], "GRP", "company", c["name"])

node("CC_CAMPUS", "CAMPUS-ROOT", "", "root", "All Campuses")
for cid, nm in [("BAL", "Ballarat"), ("GIP", "Gippsland"), ("BER", "Berwick"), ("WIM", "Wimmera"), ("CEN", "Central and Online")]:
    node("CC_CAMPUS", cid, "CAMPUS-ROOT", "campus", nm)
node("CC_SECTOR", "SECTOR-ROOT", "", "root", "All Sectors")
for sid, nm in [("HE", "Higher Education"), ("TAFE", "TAFE"), ("RES", "Research"), ("CORP", "Corporate"), ("COM", "Commercial")]:
    node("CC_SECTOR", sid, "SECTOR-ROOT", "sector", nm)
for i, n, s, campus, sector in CCS:
    node("CC_CAMPUS", i, campus, "cost_center", n)
    node("CC_SECTOR", i, sector, "cost_center", n)

node("FUND", "FUND-ROOT", "", "root", "All Funds")
for tid, nm in [("FT-UNR", "Unrestricted"), ("FT-RST", "Restricted"), ("FT-CAP", "Capital")]:
    node("FUND", tid, "FUND-ROOT", "fund_type", nm)
for f, tid in [("F-OP", "FT-UNR"), ("F-RES", "FT-RST"), ("F-RST", "FT-RST"), ("F-CAP", "FT-CAP")]:
    node("FUND", f, tid, "fund", next(x["name"] for x in FUNDS if x["fund_id"] == f))

node("ACCOUNT", "TOTAL", "", "root", "Chart of Accounts")
for cat, nm in [("ASSETS", "Assets"), ("LIABS", "Liabilities"), ("EQUITY", "Equity"), ("REV", "Revenue"), ("EXP", "Expenses")]:
    node("ACCOUNT", cat, "TOTAL", "category", nm)
CAT = {"Asset": "ASSETS", "Liability": "LIABS", "Equity": "EQUITY", "Revenue": "REV", "Expense": "EXP"}
for a, n, t, *_ in A:
    node("ACCOUNT", a, CAT[t], "account", n)

# ---- Fixed asset register (illustrative) ----
ASSETS = [
    dict(asset_id="FA-UNI-01", company_id="UNI", description="Teaching facilities fit-out", cost_local=q(2400000),
         acquisition_date="2026-01-31", life_months=240, cost_center="BAL-HE"),
    dict(asset_id="FA-UNI-02", company_id="UNI", description="TAFE workshop equipment", cost_local=q(900000),
         acquisition_date="2026-02-28", life_months=120, cost_center="BAL-TAFE"),
    dict(asset_id="FA-UNI-03", company_id="UNI", description="Laboratory and IT equipment", cost_local=q(1200000),
         acquisition_date="2026-03-31", life_months=60, cost_center="GIP-HE"),
    dict(asset_id="FA-COM-01", company_id="COM", description="Office fit-out", cost_local=q(150000),
         acquisition_date="2026-02-28", life_months=60, cost_center="COM-OPS"),
]

# ---- Journals ----
LINES = []
JOURNALS = []
jn = 0

# ---- Security model (SIMULATED): users, security groups, and segregation-of-duties conflicts ----
USERS = [
    dict(user_id="U01", description="Accounts payable clerk"),
    dict(user_id="U02", description="Accounts payable manager"),
    dict(user_id="U03", description="Accounts receivable clerk"),
    dict(user_id="U04", description="General ledger accountant"),
    dict(user_id="U05", description="Financial controller"),
    dict(user_id="U06", description="Grants accountant"),
    dict(user_id="U07", description="Treasury officer"),
    dict(user_id="U08", description="Asset accountant"),
    dict(user_id="U09", description="Procurement officer (supplier master data)"),
    dict(user_id="U10", description="Budget analyst"),
    dict(user_id="U11", description="Finance business partner (budget approver)"),
    dict(user_id="U12", description="Deputy financial controller"),
    dict(user_id="U13", description="Cash application officer"),
    dict(user_id="SYS-HCM", description="Integration user: HCM and payroll journal feed"),
]
ROLES = [
    ("U01", "AP_ENTRY"), ("U02", "AP_APPROVE"), ("U03", "AR_ENTRY"), ("U13", "AR_CASH_APPLY"),
    ("U04", "JOURNAL_ENTRY"), ("U05", "JOURNAL_APPROVE"), ("U12", "JOURNAL_APPROVE"), ("U06", "JOURNAL_ENTRY"),
    ("U07", "PAYMENT_RELEASE"), ("U08", "JOURNAL_ENTRY"), ("U09", "SUPPLIER_MASTER"),
    ("U10", "BUDGET_ENTRY"), ("U11", "BUDGET_APPROVE"), ("SYS-HCM", "JOURNAL_ENTRY"),
]
ROLE_ROWS = [dict(user_id=u, security_group=g) for u, g in ROLES]
# Pairs of groups that one person must not hold together.
SOD = [
    ("AP_ENTRY", "AP_APPROVE", "Same person could enter and approve a supplier invoice"),
    ("AP_ENTRY", "SUPPLIER_MASTER", "Same person could create a supplier and invoice it"),
    ("SUPPLIER_MASTER", "PAYMENT_RELEASE", "Same person could create a supplier and release payment"),
    ("AP_APPROVE", "PAYMENT_RELEASE", "Same person could approve an invoice and release the payment"),
    ("AR_ENTRY", "AR_CASH_APPLY", "Same person could raise an invoice and apply cash against it (concealment risk)"),
    ("JOURNAL_ENTRY", "JOURNAL_APPROVE", "Same person could post and approve a manual journal"),
    ("BUDGET_ENTRY", "BUDGET_APPROVE", "Same person could set and approve a budget"),
]
SOD_ROWS = [dict(group_a=a, group_b=b, risk=r) for a, b, r in SOD]

# Who prepares journals from each source module; the approver alternates between the two controllers.
SRC = ["R2R"]
CREATOR = dict(R2R="U04", O2C="U03", P2P="U01", GRANTS="U06", PAYROLL="SYS-HCM", ASSETS="U08", INTERCO="U04")
APPROVER = ["U05", "U12"]


def journal(date, parts, memo):
    """parts: (company, account, cost_center, project, fund, debit, credit, counter_company).
    A journal may span companies, but each company's lines must balance on their own."""
    global jn
    jn += 1
    jid = f"J{jn:05d}"
    src = SRC[0]
    JOURNALS.append(dict(journal_id=jid, source=src, created_by=CREATOR[src], approved_by=APPROVER[jn % 2]))
    for i, (co, acct, cc, pr, fund, dr, cr, cp) in enumerate(parts, 1):
        LINES.append(dict(journal_id=jid, line_no=i, posting_date=date, company_id=co, ledger_account=acct,
                          cost_center=cc, project=pr, fund=fund, currency=CUR[co], debit_local=q(dr),
                          credit_local=q(cr), counter_company=cp, memo=memo))
    return jid


AP_INV, AP_PAY, AR_INV, AR_REC = [], [], [], []


def sub(table, prefix, **kw):
    table.append(dict(**{f"{prefix}_id": f"{prefix.upper()}{len(table) + 1:05d}"}, **kw))


def spread(total, n):
    """Split total into n parts that sum exactly to total."""
    total = q(total)
    parts = [q(total * Decimal(random.randint(80, 120)) / Decimal(100 * n)) for _ in range(n - 1)]
    parts.append(total - sum(parts))
    return parts


def revenue_journal(date, cash_acct, rev_acct, ccs, total, memo):
    amts = spread(total, len(ccs))
    parts = [("UNI", cash_acct, "", "", "", sum(amts), 0, "")]
    parts += [("UNI", rev_acct, cc, "", "F-OP", 0, a, "") for cc, a in zip(ccs, amts)]
    journal(date, parts, memo)
    return sum(amts)


SRC[0] = "R2R"
journal("2026-01-01", [("UNI", "1000", "", "", "", 90_000_000, 0, ""), ("UNI", "3000", "", "", "", 0, 90_000_000, "")], "Opening funds")
journal("2026-01-01", [("COM", "1000", "", "", "", 5_000_000, 0, ""), ("COM", "3000", "", "", "", 0, 5_000_000, "")], "Opening funds")

for month in range(1, 7):
    eom = f"2026-{month:02d}-{calendar.monthrange(2026, month)[1]:02d}"
    period = f"2026-{month:02d}"

    # Funding and fees (order-to-cash)
    SRC[0] = "O2C"
    revenue_journal(eom, "1000", "4000", HE, random.randint(5_500_000, 7_000_000), "Commonwealth funding instalment")
    revenue_journal(eom, "1000", "4050", TAFE, random.randint(3_000_000, 4_000_000), "State TAFE funding instalment")
    billed = random.randint(2_000_000, 3_000_000)
    amts = spread(billed, len(HE))
    jid = journal(eom, [("UNI", "1100", "", "", "", sum(amts), 0, "")] + [("UNI", "4100", cc, "", "F-OP", 0, a, "") for cc, a in zip(HE, amts)],
                  "Student contributions billed")
    sub(AR_INV, "ari", company_id="UNI", customer_type="Student", invoice_date=eom, amount_local=q(sum(amts)), journal_id=jid)
    rec = q(sum(amts) * Decimal("0.90"))
    jid = journal(eom, [("UNI", "1000", "", "", "", rec, 0, ""), ("UNI", "1100", "", "", "", 0, rec, "")], "Student receipts")
    sub(AR_REC, "arr", company_id="UNI", receipt_date=eom, amount_local=rec, journal_id=jid)
    revenue_journal(eom, "1000", "4200", ["ONL-HE", "BAL-HE"], random.randint(1_000_000, 2_000_000), "International fees")

    # Research grants: cash in advance each quarter, revenue recognised as costs are incurred
    SRC[0] = "GRANTS"
    for p in PROJECTS:
        pid = p["project_id"]
        if month in (1, 4):
            adv = q(900_000)
            journal(eom, [("UNI", "1000", "", "", "", adv, 0, ""), ("UNI", "2100", "", pid, "F-RES", 0, adv, "")],
                    f"Grant instalment received {pid}")
        cost = q(random.randint(100_000, 250_000))
        journal(eom, [("UNI", "6400", "RES-OFF", pid, "F-RES", cost, 0, ""), ("UNI", "1000", "", "", "", 0, cost, ""),
                      ("UNI", "2100", "", pid, "F-RES", cost, 0, ""), ("UNI", "4300", "RES-OFF", pid, "F-RES", 0, cost, "")],
                f"Research spend and grant revenue {pid}")

    # Donations and scholarships (restricted fund)
    don = q(random.randint(150_000, 250_000))
    journal(eom, [("UNI", "1000", "", "", "", don, 0, ""), ("UNI", "4600", "COR-SVC", "", "F-RST", 0, don, "")], "Donations received")
    sch = q(random.randint(60_000, 140_000))
    journal(eom, [("UNI", "6300", "COR-SVC", "", "F-RST", sch, 0, ""), ("UNI", "1000", "", "", "", 0, sch, "")], "Scholarships paid")

    # Capital grant
    if month == 2:
        journal(eom, [("UNI", "1000", "", "", "", 3_000_000, 0, ""), ("UNI", "4400", "COR-SVC", "", "F-CAP", 0, 3_000_000, "")], "Capital grant received")

    # People and occupancy
    SRC[0] = "PAYROLL"
    for cc in HE + TAFE:
        pay = q(random.randint(800_000, 1_800_000))
        journal(eom, [("UNI", "6000", cc, "", "F-OP", pay, 0, ""), ("UNI", "1000", "", "", "", 0, pay, "")], "Academic payroll")
    for cc in ["COR-SVC", "RES-OFF", "BAL-HE"]:
        pay = q(random.randint(400_000, 900_000))
        journal(eom, [("UNI", "6050", cc, "", "F-OP", pay, 0, ""), ("UNI", "1000", "", "", "", 0, pay, "")], "Professional staff payroll")
    SRC[0] = "P2P"
    for cc in ["BAL-HE", "GIP-HE", "BER-HE", "WIM-TAFE"]:
        occ = q(random.randint(150_000, 300_000))
        jid = journal(eom, [("UNI", "6100", cc, "", "F-OP", occ, 0, ""), ("UNI", "2000", "", "", "", 0, occ, "")], "Campus occupancy")
        sub(AP_INV, "api", company_id="UNI", supplier=f"SUP-OCC-{cc}", invoice_date=eom, amount_local=occ, cost_center=cc, asset_id="", journal_id=jid)
        paid = q(occ * Decimal("0.85"))
        jid = journal(eom, [("UNI", "2000", "", "", "", paid, 0, ""), ("UNI", "1000", "", "", "", 0, paid, "")], "Supplier payment")
        sub(AP_PAY, "app", company_id="UNI", supplier=f"SUP-OCC-{cc}", payment_date=eom, amount_local=paid, journal_id=jid)

    # Assets: capex in acquisition month, depreciation from the month after
    for a in ASSETS:
        co, acq = a["company_id"], a["acquisition_date"][:7]
        if acq == period:
            SRC[0] = "P2P"
            jid = journal(eom, [(co, "1700", a["cost_center"], "", "", a["cost_local"], 0, ""), (co, "2000", "", "", "", 0, a["cost_local"], "")],
                          f"Capex {a['asset_id']}")
            sub(AP_INV, "api", company_id=co, supplier=f"SUP-CAPEX-{a['asset_id']}", invoice_date=eom, amount_local=a["cost_local"],
                cost_center=a["cost_center"], asset_id=a["asset_id"], journal_id=jid)
        elif acq < period:
            SRC[0] = "ASSETS"
            dep = q(a["cost_local"] / a["life_months"])
            journal(eom, [(co, "6200", a["cost_center"], "", "F-OP", dep, 0, ""), (co, "1710", "", "", "", 0, dep, "")],
                    f"Depreciation {a['asset_id']}")

    # Commercial entity, and shared services charged by the University (intercompany)
    SRC[0] = "O2C"
    com_rev = q(random.randint(400_000, 700_000))
    jid = journal(eom, [("COM", "1100", "", "", "", com_rev, 0, ""), ("COM", "4200", "COM-OPS", "", "F-OP", 0, com_rev, "")], "Commercial fees billed")
    sub(AR_INV, "ari", company_id="COM", customer_type="Commercial", invoice_date=eom, amount_local=com_rev, journal_id=jid)
    com_rec = q(com_rev * Decimal("0.90"))
    jid = journal(eom, [("COM", "1000", "", "", "", com_rec, 0, ""), ("COM", "1100", "", "", "", 0, com_rec, "")], "Commercial receipts")
    sub(AR_REC, "arr", company_id="COM", receipt_date=eom, amount_local=com_rec, journal_id=jid)
    SRC[0] = "PAYROLL"
    com_pay = q(random.randint(200_000, 350_000))
    journal(eom, [("COM", "6050", "COM-OPS", "", "F-OP", com_pay, 0, ""), ("COM", "1000", "", "", "", 0, com_pay, "")], "Commercial payroll")
    SRC[0] = "INTERCO"
    fee = 120_000
    journal(eom, [("UNI", "1500", "", "", "", fee, 0, "COM"), ("UNI", "4500", "COR-SVC", "", "F-OP", 0, fee, ""),
                  ("COM", "6500", "COM-OPS", "", "F-OP", fee, 0, ""), ("COM", "2500", "", "", "", 0, fee, "UNI")],
            "Shared services charge to COM")

# ---- Budget ledger (simulated): same worktags as actuals, revenue and expense accounts only ----
ACC_TYPE = {a: t for a, _, t, *_ in A}
actual = {}
for l in LINES:
    if ACC_TYPE[l["ledger_account"]] not in ("Revenue", "Expense") or not l["cost_center"]:
        continue
    key = (l["posting_date"][:7], l["company_id"], l["ledger_account"], l["cost_center"], l["project"], l["fund"])
    actual[key] = actual.get(key, Decimal(0)) + (l["credit_local"] - l["debit_local"] if ACC_TYPE[l["ledger_account"]] == "Revenue"
                                                  else l["debit_local"] - l["credit_local"])
BUDGET = []
for key, amt in sorted(actual.items()):
    factor = Decimal(93 + zlib.crc32("|".join(key).encode()) % 17) / Decimal(100)   # 0.93 to 1.09
    BUDGET.append(dict(budget_id=f"B{len(BUDGET) + 1:05d}", ledger="BUDGET-2026", period=key[0], company_id=key[1], ledger_account=key[2],
                       cost_center=key[3], project=key[4], fund=key[5], amount_local=q(amt * factor)))

write("companies.csv", COMPANIES, ["company_id", "name", "country", "currency"])
write("funds.csv", FUNDS, ["fund_id", "name", "fund_type"])
write("ledger_accounts.csv", ACC_ROWS, list(ACC_ROWS[0].keys()))
write("cost_centers.csv", CC_ROWS, ["cost_center_id", "name", "company_scope"])
write("projects.csv", PROJECTS, ["project_id", "name", "company_id", "fund_id"])
write("assets.csv", ASSETS, list(ASSETS[0].keys()))
write("fx_rates.csv", [dict(currency=k, rate_to_aud=v) for k, v in FX.items()], ["currency", "rate_to_aud"])
write("hierarchy.csv", H, ["hierarchy_name", "node_id", "parent_id", "node_type", "node_name"])
write("journals.csv", JOURNALS, ["journal_id", "source", "created_by", "approved_by"])
write("users.csv", USERS, ["user_id", "description"])
write("role_assignments.csv", ROLE_ROWS, ["user_id", "security_group"])
write("sod_conflicts.csv", SOD_ROWS, ["group_a", "group_b", "risk"])
write("ap_invoices.csv", AP_INV, ["api_id", "company_id", "supplier", "invoice_date", "amount_local", "cost_center", "asset_id", "journal_id"])
write("ap_payments.csv", AP_PAY, ["app_id", "company_id", "supplier", "payment_date", "amount_local", "journal_id"])
write("ar_invoices.csv", AR_INV, ["ari_id", "company_id", "customer_type", "invoice_date", "amount_local", "journal_id"])
write("ar_receipts.csv", AR_REC, ["arr_id", "company_id", "receipt_date", "amount_local", "journal_id"])
write("budget_lines.csv", BUDGET, list(BUDGET[0].keys()))
write("journal_lines.csv", LINES, list(LINES[0].keys()))
print(f"Wrote {len(LINES)} journal lines across {jn} journals to {OUT}")
