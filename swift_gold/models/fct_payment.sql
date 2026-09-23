{{ config(materialized='table') }}

SELECT
  uetr, creation_dt, amount_cad, corridor, channel,
  debtor_defect, creditor_defect,
  CASE WHEN debtor_defect != 'CLEAN' OR creditor_defect != 'CLEAN'
       THEN TRUE ELSE FALSE END AS is_failing
FROM {{ source('swift', 'silver_payments') }}

UNION ALL

SELECT
  uetr, creation_dt, amount_cad, corridor, channel,
  debtor_defect, creditor_defect,
  CASE WHEN debtor_defect != 'CLEAN' OR creditor_defect != 'CLEAN'
       THEN TRUE ELSE FALSE END AS is_failing
FROM {{ source('swift', 'silver_quarantine') }}