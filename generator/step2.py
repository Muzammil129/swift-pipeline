from jinja2 import Environment, FileSystemLoader
from pacs008.xml.validate_via_xsd import validate_xml_string_via_xsd
from defects import apply_defects
import random, uuid, os, csv
from datetime import date, timedelta

FIRST_NAMES = ["Priya", "Daniel", "Sarah", "Mohammed", "Chen", "Amara"]
LAST_NAMES = ["Raman", "Okafor", "Tremblay", "Singh", "Nguyen", "Belanger"]
CITIES = [
    ("Toronto", "ON", "M5X1A9"),
    ("Montreal", "QC", "H3B4G5"),
    ("Vancouver", "BC", "V6C2T4"),
    ("Calgary", "AB", "T2P3N9"),
]

DEFECT_WEIGHTS = {
    "CLEAN": 80,
    "UNSTRUCTURED_ONLY": 8,
    "MISSING_COUNTRY": 5,
    "MISSING_TOWN": 3,
    "PLACEHOLDER_COUNTRY": 2,
    "DUPLICATED_TOWN": 2,
}

def pick_defect(rng):
    names = list(DEFECT_WEIGHTS)
    weights = [DEFECT_WEIGHTS[n] for n in names]
    return rng.choices(names, weights=weights, k=1)[0]

def make_payment(rng, n):
    twn, prov, pstcd = rng.choice(CITIES)
    return {
        "end_to_end_id": f"E2E-{n:06d}",
        "uetr": str(uuid.uuid4()),
        "interbank_settlement_amount": f"{rng.uniform(10, 50000):.2f}",
        "interbank_settlement_currency": "CAD",
        "charge_bearer": "SLEV",
        "debtor_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "debtor_agent_bic": "WSPLCATTXXX",
        "debtor_strt_nm": "King Street West",
        "debtor_bldg_nb": str(rng.randint(1, 999)),
        "debtor_pst_cd": pstcd,
        "debtor_twn_nm": twn,
        "debtor_ctry": "CA",
        "creditor_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "creditor_agent_bic": "ROYCCAT2XXX",
        "creditor_account_iban": "CA12ROYC0000001234567890",
        "creditor_strt_nm": "Rue Sainte-Catherine Ouest",
        "creditor_bldg_nb": str(rng.randint(1, 999)),
        "creditor_pst_cd": pstcd,
        "creditor_twn_nm": twn,
        "creditor_ctry": "CA",
    }

TPL_DIR = "templates/pacs.008.001.08"
XSD = f"{TPL_DIR}/pacs.008.001.08.xsd"

env = Environment(loader=FileSystemLoader(TPL_DIR), autoescape=True)

rng = random.Random(42)
START = date(2026, 7, 1)
PER_FILE = 500

n = 0
file_no = 0
answer_key = []

for day_offset in range(30):
    day = START + timedelta(days=day_offset)
    if day.weekday() >= 5:
        files_today = 2
    else:
        files_today = 40

    folder = f"data/bronze/ingest_date={day}"
    os.makedirs(folder, exist_ok=True)

    for i in range(files_today):
        file_no += 1
        transactions = []

        for j in range (PER_FILE):
            n += 1
            tx = make_payment(rng, n)
            defect = pick_defect(rng)
            tx = apply_defects (tx, "debtor", defect)
            answer_key.append({
                "uetr": tx["uetr"],
                "party": "debtor",
                "defect": defect,
                "source_file": f"msgs-{file_no:06d}.xml",
            })
            transactions.append(tx)

        message = {
            "msg_id": f"MSG-{file_no:06d}",
            "creation_date_time": f"{day}T10:00:00",
            "nb_of_txs": str(len(transactions)),
            "settlement_method": "CLRG",
            "transactions": transactions,
        }

        xml = env.get_template("template.xml").render(**message)
        open(f"{folder}/msgs-{file_no:06d}.xml", "w", encoding="utf-8").write(xml)

print("files:", file_no, "payments:", n)
with open("data/answer_key.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["uetr", "party", "defect", "source_file"])
    writer.writeheader()
    writer.writerows(answer_key)