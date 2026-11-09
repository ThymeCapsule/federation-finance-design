-- Grant income in advance still held per research project (cash received, not yet recognised as revenue).
SELECT l.project, p.name AS project_name, p.fund_id,
       round(sum(l.credit_aud - l.debit_aud), 2) AS income_in_advance_aud
FROM v_lines l JOIN projects p ON p.project_id = l.project
WHERE l.ledger_account = '2100'
GROUP BY l.project, p.name, p.fund_id ORDER BY l.project;
