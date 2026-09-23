SELECT
  COUNT(*) AS total_addresses,
  SUM(CASE WHEN k.defect = a.defect THEN 1 ELSE 0 END) AS agree,
  SUM(CASE WHEN k.defect != a.defect THEN 1 ELSE 0 END) AS disagree,
  ROUND(100.0 * SUM(CASE WHEN k.defect = a.defect THEN 1 ELSE 0 END) / COUNT(*), 2) AS pct_agree
FROM {{ source('swift', 'ref_answer_key') }} k
JOIN {{ ref('vw_address') }} a ON k.uetr = a.uetr AND k.party = a.party