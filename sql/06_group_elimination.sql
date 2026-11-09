-- Group view: intercompany income and expense should eliminate to ~0.
SELECT CASE WHEN is_intercompany = 1 THEN 'Intercompany (should be ~0)' ELSE 'External' END AS source,
       round(sum(credit_aud - debit_aud), 2) AS group_result_aud
FROM v_lines WHERE account_type IN ('Revenue', 'Expense') GROUP BY source;
