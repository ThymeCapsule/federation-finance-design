-- Base views. Runs on SQLite; portable to Snowflake with minor syntax changes.
CREATE VIEW v_lines AS
SELECT j.*,
       substr(j.posting_date, 1, 7)                         AS period,
       a.account_type,
       a.is_intercompany,
       round(j.debit_local  * f.rate_to_aud, 2)             AS debit_aud,
       round(j.credit_local * f.rate_to_aud, 2)             AS credit_aud
FROM journal_lines j
JOIN fx_rates f        ON f.currency = j.currency
JOIN ledger_accounts a ON a.account_id = j.ledger_account;

-- Every node's ancestors (and itself) in each hierarchy: the basis for rollup reporting.
CREATE VIEW v_ancestors AS
WITH RECURSIVE path(hierarchy_name, leaf, node, parent) AS (
    SELECT hierarchy_name, node_id, node_id, parent_id FROM hierarchy
    UNION ALL
    SELECT p.hierarchy_name, p.leaf, h.node_id, h.parent_id
    FROM path p
    JOIN hierarchy h ON h.hierarchy_name = p.hierarchy_name AND h.node_id = p.parent
)
SELECT p.hierarchy_name, p.leaf, p.node AS ancestor, h.node_type AS ancestor_type, h.node_name AS ancestor_name
FROM path p
JOIN hierarchy h ON h.hierarchy_name = p.hierarchy_name AND h.node_id = p.node;
