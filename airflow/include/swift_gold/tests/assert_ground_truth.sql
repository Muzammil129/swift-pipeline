SELECT pct_agree
FROM {{ ref('rpt_ground_truth') }}
WHERE pct_agree != 100.00