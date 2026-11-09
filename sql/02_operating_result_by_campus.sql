-- Operating result by campus, rolled up the CC_CAMPUS hierarchy. External activity only (intercompany excluded).
-- All funds are included here; see 04_fund_summary for the split by fund.
SELECT anc.ancestor_name AS campus,
       round(sum(CASE WHEN l.account_type = 'Revenue' THEN l.credit_aud - l.debit_aud ELSE 0 END), 2) AS revenue_aud,
       round(sum(CASE WHEN l.account_type = 'Expense' THEN l.debit_aud - l.credit_aud ELSE 0 END), 2) AS expense_aud,
       round(sum(l.credit_aud - l.debit_aud), 2) AS result_aud
FROM v_lines l
JOIN v_ancestors anc ON anc.hierarchy_name = 'CC_CAMPUS' AND anc.leaf = l.cost_center AND anc.ancestor_type = 'campus'
WHERE l.account_type IN ('Revenue', 'Expense') AND l.is_intercompany = 0
GROUP BY anc.ancestor_name ORDER BY anc.ancestor_name;
