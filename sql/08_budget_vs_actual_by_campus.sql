-- Budget ledger versus actuals by campus (CC_CAMPUS hierarchy), operating result, external activity only.
-- The budget is simulated (a fixed perturbation of simulated actuals), so the variances show the report shape, not performance.
WITH act AS (
  SELECT anc.ancestor_name AS campus,
         sum(CASE WHEN l.account_type = 'Revenue' THEN l.credit_aud - l.debit_aud ELSE 0 END) AS revenue,
         sum(CASE WHEN l.account_type = 'Expense' THEN l.debit_aud - l.credit_aud ELSE 0 END) AS expense
  FROM v_lines l
  JOIN v_ancestors anc ON anc.hierarchy_name = 'CC_CAMPUS' AND anc.leaf = l.cost_center AND anc.ancestor_type = 'campus'
  WHERE l.account_type IN ('Revenue', 'Expense') AND l.is_intercompany = 0
  GROUP BY anc.ancestor_name
), bud AS (
  SELECT anc.ancestor_name AS campus,
         sum(CASE WHEN a.account_type = 'Revenue' THEN b.amount_local * f.rate_to_aud ELSE 0 END) AS revenue,
         sum(CASE WHEN a.account_type = 'Expense' THEN b.amount_local * f.rate_to_aud ELSE 0 END) AS expense
  FROM budget_lines b
  JOIN ledger_accounts a ON a.account_id = b.ledger_account
  JOIN companies c       ON c.company_id = b.company_id
  JOIN fx_rates f        ON f.currency = c.currency
  JOIN v_ancestors anc   ON anc.hierarchy_name = 'CC_CAMPUS' AND anc.leaf = b.cost_center AND anc.ancestor_type = 'campus'
  WHERE a.is_intercompany = 0
  GROUP BY anc.ancestor_name
)
SELECT act.campus,
       round(bud.revenue - bud.expense, 2)                              AS budget_result_aud,
       round(act.revenue - act.expense, 2)                              AS actual_result_aud,
       round((act.revenue - act.expense) - (bud.revenue - bud.expense), 2) AS variance_aud
FROM act JOIN bud ON bud.campus = act.campus
ORDER BY act.campus;
