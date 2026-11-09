-- Trial balance by company and ledger account.
SELECT company_id, ledger_account, a.name AS account_name,
       round(sum(debit_local), 2)  AS debit,
       round(sum(credit_local), 2) AS credit,
       round(sum(debit_aud - credit_aud), 2) AS net_dr_cr_aud
FROM v_lines l JOIN ledger_accounts a ON a.account_id = l.ledger_account
GROUP BY company_id, ledger_account, a.name
ORDER BY company_id, ledger_account;
