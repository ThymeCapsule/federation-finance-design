-- Intercompany reconciliation per period: receivable (1500) vs payable (2500), in AUD.
WITH ic AS (
  SELECT period,
         CASE WHEN ledger_account = '1500' THEN company_id ELSE counter_company END AS creditor_co,
         CASE WHEN ledger_account = '1500' THEN counter_company ELSE company_id END AS debtor_co,
         ledger_account, debit_aud, credit_aud
  FROM v_lines WHERE ledger_account IN ('1500', '2500')
)
SELECT period, creditor_co, debtor_co,
       round(sum(CASE WHEN ledger_account = '1500' THEN debit_aud - credit_aud END), 2) AS receivable_aud,
       round(sum(CASE WHEN ledger_account = '2500' THEN credit_aud - debit_aud END), 2) AS payable_aud,
       round(sum(CASE WHEN ledger_account = '1500' THEN debit_aud - credit_aud END)
           - sum(CASE WHEN ledger_account = '2500' THEN credit_aud - debit_aud END), 2) AS difference_aud
FROM ic GROUP BY period, creditor_co, debtor_co ORDER BY period, debtor_co;
