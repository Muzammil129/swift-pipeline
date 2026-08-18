from defects import apply_defects
tx = {
        "debtor_name" : "priya",
        "debtor_strt_nm": "King Street West",
        "debtor_bldg_nb": "100",
        "debtor_pst_cd": "M5X1A9",
        "debtor_twn_nm" : "Toronto",
        "debtor_ctry" : "CA"}

broken = apply_defects(tx, "debtor", "UNSTRUCTURED_ONLY")
print("original:", tx)
print("broken:  ", broken)