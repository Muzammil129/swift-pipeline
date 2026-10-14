SELECT
  COUNT(*) AS total_payments,
  SUM(CASE WHEN is_failing THEN 1 ELSE 0 END) AS failing_payments,
  ROUND(100.0 * SUM(CASE WHEN is_failing THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_failing
FROM {{ ref('fct_payment') }}