def apply_defects(tx, party, defect):
    tx = dict(tx)
    if defect == "MISSING_COUNTRY":
        tx.pop(f"{party}_ctry", None)
        
    if defect == "MISSING_TOWN":
        tx.pop(f"{party}_twn_nm", None)
        
    if defect == "PLACEHOLDER_COUNTRY":
        tx[f"{party}_ctry"] = "NOTPROVIDED"

    if defect == "DUPLICATED_TOWN":
        tx[f"{party}_adr_line"] = [tx[f"{party}_twn_nm"]]

    if defect == "UNSTRUCTURED_ONLY":
        line1 = f"{tx[f'{party}_bldg_nb']} {tx[f'{party}_strt_nm']}"
        line2 = f"{tx[f'{party}_twn_nm']} {tx[f'{party}_pst_cd']}"
        line3 = "CANADA"
        for f in ("strt_nm", "bldg_nb", "pst_cd", "twn_nm", "ctry"):
            tx.pop(f"{party}_{f}", None)
        tx[f"{party}_adr_line"] = [line1, line2, line3]
    return tx