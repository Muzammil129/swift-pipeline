SELECT
  COUNT(*) AS total_payments,
  SUM(CASE WHEN f.is_failing THEN 1 ELSE 0 END) AS failing_now,
  SUM(CASE WHEN d.remediation_group = 'Needs source data'
             OR c.remediation_group = 'Needs source data'
           THEN 1 ELSE 0 END) AS failing_after_autofix
FROM {{ ref('fct_payment') }} f
JOIN {{ ref('dim_defect') }} d ON f.debtor_defect   = d.defect_code
JOIN {{ ref('dim_defect') }} c ON f.creditor_defect = c.defect_code