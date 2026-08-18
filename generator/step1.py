from pacs008 import generate_xml_string

TPL = "templates/pacs.008.001.08"

row = {
    "msg_id": "MSG-0001",
    "creation_date_time": "2026-07-29T10:00:00",
    "nb_of_txs": "1",
    "settlement_method": "CLRG",
    "end_to_end_id": "E2E-0001",
    "uetr": "8f2b6c1e-1a4d-4c3e-9b7a-2d5f8e1c4a90",
    "interbank_settlement_amount": "1500.00",
    "interbank_settlement_currency": "CAD",
    "charge_bearer": "SLEV",
    "debtor_name": "Priya Raman",
    "debtor_agent_bic": "WSPLCATTXXX",
    "debtor_strt_nm": "King Street West",
    "debtor_bldg_nb": "100",
    "debtor_pst_cd": "M5X1A9",
    "debtor_twn_nm": "Toronto",
    "debtor_ctry": "CA",
    "creditor_name": "Daniel Okafor",
    "creditor_agent_bic": "ROYCCAT2XXX",
    "creditor_account_iban": "CA12ROYC0000001234567890",
}

xml = generate_xml_string(
    data=[row],
    payment_initiation_message_type="pacs.008.001.08",
    xml_template_path=f"{TPL}/template.xml",
    xsd_schema_path=f"{TPL}/pacs.008.001.08.xsd",
)
print(xml)