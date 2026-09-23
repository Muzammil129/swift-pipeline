SELECT
  f.channel, c.segment, c.format, c.migration_status,
  COUNT(*) AS payments,
  SUM(CASE WHEN f.is_failing THEN 1 ELSE 0 END) AS failing,
  ROUND(100.0 * SUM(CASE WHEN f.is_failing THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_failing
FROM {{ ref('fct_payment') }} f
JOIN {{ ref('dim_channel') }} c ON f.channel = c.channel
GROUP BY f.channel, c.segment, c.format, c.migration_status