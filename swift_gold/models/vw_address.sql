SELECT uetr, corridor, channel, amount_cad, 'debtor' AS party, debtor_defect AS defect
FROM {{ ref('fct_payment') }}
UNION ALL
SELECT uetr, corridor, channel, amount_cad, 'creditor' AS party, creditor_defect AS defect
FROM {{ ref('fct_payment') }}