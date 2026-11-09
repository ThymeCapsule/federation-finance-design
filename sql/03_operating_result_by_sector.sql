-- Same activity viewed through the parallel CC_SECTOR hierarchy: a different cut of the same cost centers.
SELECT anc.ancestor_name AS sector,
       round(sum(CASE WHEN l.account_type = 'Revenue' THEN l.credit_aud - l.debit_aud ELSE 0 END), 2) AS revenue_aud,
       round(sum(CASE WHEN l.account_type = 'Expense' THEN l.debit_aud - l.credit_aud ELSE 0 END), 2) AS expense_aud,
       round(sum(l.credit_aud - l.debit_aud), 2) AS result_aud
FROM v_lines l
JOIN v_ancestors anc ON anc.hierarchy_name = 'CC_SECTOR' AND anc.leaf = l.cost_center AND anc.ancestor_type = 'sector'
WHERE l.account_type IN ('Revenue', 'Expense') AND l.is_intercompany = 0
GROUP BY anc.ancestor_name ORDER BY anc.ancestor_name;
