SELECT corridor, defect, COUNT(*) AS addresses
FROM {{ ref('vw_address') }}
WHERE defect != 'CLEAN'
GROUP BY corridor, defect
