SELECT a.corridor, d.remediation_group, COUNT(*) AS addresses
FROM {{ ref('vw_address') }} a
JOIN {{ ref('dim_defect') }} d ON a.defect = d.defect_code
WHERE d.remediation_group != 'None'
GROUP BY a.corridor, d.remediation_group