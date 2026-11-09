-- Payables (2000) and receivables (1100): GL balance versus subledger balance at the last period, per company.
WITH gl AS (
  SELECT company_id,
         CASE ledger_account WHEN '2000' THEN 'AP' ELSE 'AR' END AS control,
         sum(CASE ledger_account WHEN '2000' THEN credit_local - debit_local ELSE debit_local - credit_local END) AS gl_balance
  FROM journal_lines WHERE ledger_account IN ('2000', '1100') GROUP BY 1, 2
), sl AS (
  SELECT company_id, 'AP' AS control, sum(amount_local) AS sl_balance FROM (
    SELECT company_id, amount_local FROM ap_invoices UNION ALL SELECT company_id, -amount_local FROM ap_payments) GROUP BY 1
  UNION ALL
  SELECT company_id, 'AR', sum(amount_local) FROM (
    SELECT company_id, amount_local FROM ar_invoices UNION ALL SELECT company_id, -amount_local FROM ar_receipts) GROUP BY 1
)
SELECT gl.company_id, gl.control, round(gl.gl_balance, 2) AS gl_balance, round(sl.sl_balance, 2) AS subledger_balance,
       round(gl.gl_balance - sl.sl_balance, 2) AS difference
FROM gl JOIN sl ON sl.company_id = gl.company_id AND sl.control = gl.control
ORDER BY gl.company_id, gl.control;
