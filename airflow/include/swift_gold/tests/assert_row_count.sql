SELECT COUNT(*) AS row_count
FROM {{ ref('fct_payment') }}
HAVING COUNT(*) != 448000