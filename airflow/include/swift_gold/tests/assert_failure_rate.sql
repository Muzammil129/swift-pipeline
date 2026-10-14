SELECT ROUND(100.0 * SUM(CASE WHEN is_failing THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct
FROM {{ ref('fct_payment') }}
HAVING pct != 33.7