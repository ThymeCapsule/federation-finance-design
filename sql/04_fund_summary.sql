-- Revenue, expense and balance by fund, with fund type from the FUND hierarchy.
SELECT t.ancestor_name AS fund_type, fu.fund_id, fu.name AS fund_name,
       round(sum(CASE WHEN l.account_type = 'Revenue' THEN l.credit_aud - l.debit_aud ELSE 0 END), 2) AS revenue_aud,
       round(sum(CASE WHEN l.account_type = 'Expense' THEN l.debit_aud - l.credit_aud ELSE 0 END), 2) AS expense_aud,
       round(sum(l.credit_aud - l.debit_aud), 2) AS fund_result_aud
FROM v_lines l
JOIN funds fu ON fu.fund_id = l.fund
JOIN v_ancestors t ON t.hierarchy_name = 'FUND' AND t.leaf = l.fund AND t.ancestor_type = 'fund_type'
WHERE l.account_type IN ('Revenue', 'Expense') AND l.is_intercompany = 0
GROUP BY t.ancestor_name, fu.fund_id, fu.name ORDER BY t.ancestor_name, fu.fund_id;
