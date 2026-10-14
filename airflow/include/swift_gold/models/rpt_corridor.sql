SELECT
  f.corridor, d.country_name, d.region, d.infra_status,
  COUNT(*) AS payments,
  SUM(CASE WHEN f.is_failing THEN 1 ELSE 0 END) AS failing,
  ROUND(100.0 * SUM(CASE WHEN f.is_failing THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_failing,
  ROUND(SUM(f.amount_cad) / 1000000, 1) AS total_value_m,
  ROUND(SUM(CASE WHEN f.is_failing THEN f.amount_cad ELSE 0 END) / 1000000, 1) AS failing_value_m
FROM {{ ref('fct_payment') }} f
JOIN {{ ref('dim_corridor') }} d ON f.corridor = d.corridor
GROUP BY f.corridor, d.country_name, d.region, d.infra_status