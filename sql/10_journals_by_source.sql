-- Journals by source module and preparer: which modules feed the ledger, who prepares them, and how many have no approver recorded.
SELECT h.source, h.created_by,
       count(DISTINCT h.journal_id)                                       AS journals,
       count(DISTINCT CASE WHEN h.approved_by = '' THEN h.journal_id END) AS journals_without_approver,
       round(sum(l.debit_aud), 2)                                         AS gross_debits_aud
FROM journals h JOIN v_lines l ON l.journal_id = h.journal_id
GROUP BY h.source, h.created_by ORDER BY h.source;
