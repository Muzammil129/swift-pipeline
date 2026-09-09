from jinja2 import Environment, FileSystemLoader
from pacs008.xml.validate_via_xsd import validate_xml_string_via_xsd
from defects import apply_defects
import random, uuid, os, csv
from datetime import date, timedelta

FIRST_NAMES = ["Priya", "Daniel", "Sarah", "Mohammed", "Chen", "Amara"]
LAST_NAMES = ["Raman", "Okafor", "Tremblay", "Singh", "Nguyen", "Belanger"]

CANADA_STREETS = ["King Street West", "Rue Sainte-Catherine", "Granville Street",
                  "Stephen Avenue", "Yonge Street", "Portage Avenue"]
CANADA_CITIES = [
    ("Toronto", "ON", "M5X1A9"),
    ("Montreal", "QC", "H3B4G5"),
    ("Vancouver", "BC", "V6C2T4"),
    ("Calgary", "AB", "T2P3N9"),
]

CORRIDORS = {
    "US": {
        "weight": 50,
        "currency": "USD",
        "bic": "CHASUS33XXX",
        "streets": ["Main Street", "Oak Avenue", "Park Boulevard", "Elm Street"],
        "cities": [("New York", "NY", "10001"), ("Los Angeles", "CA", "90001"),
                   ("Chicago", "IL", "60601"), ("Houston", "TX", "77001")],
        "defects": {"CLEAN": 80, "UNSTRUCTURED_ONLY": 8, "MISSING_COUNTRY": 4,
       "MISSING_TOWN": 3, "PLACEHOLDER_COUNTRY": 2, "DUPLICATED_TOWN": 2, "INVALID_COUNTRY": 1},
    },
    "PH": {
        "weight": 16,
        "currency": "PHP",
        "bic": "BOPIPHMMXXX",
        "streets": ["Rizal Avenue", "Ayala Avenue", "Katipunan Avenue", "Session Road"],
        "cities": [("Manila", "NCR", "1000"), ("Cebu City", "CEB", "6000"),
                   ("Davao City", "DAV", "8000"), ("Quezon City", "NCR", "1100")],
        "defects": {"CLEAN": 57, "UNSTRUCTURED_ONLY": 24, "MISSING_COUNTRY": 6,
       "MISSING_TOWN": 8, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 1, "INVALID_COUNTRY": 1},
    },
    "IN": {
        "weight": 11,
        "currency": "INR",
        "bic": "HDFCINBBXXX",
        "streets": ["MG Road", "Linking Road", "Brigade Road", "Anna Salai"],
        "cities": [("Mumbai", "MH", "400001"), ("Hyderabad", "TG", "500001"),
                   ("Delhi", "DL", "110001"), ("Chennai", "TN", "600001")],
        "defects": {"CLEAN": 55, "UNSTRUCTURED_ONLY": 25, "MISSING_COUNTRY": 6,
       "MISSING_TOWN": 8, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 2, "INVALID_COUNTRY": 1},
    },
    "PK": {
        "weight": 4,
        "currency": "PKR",
        "bic": "HABBPKKAXXX",
        "streets": ["Shahrah-e-Faisal", "Mall Road", "Jinnah Avenue"],
        "cities": [("Karachi", "SD", "74000"), ("Lahore", "PB", "54000"),
                   ("Islamabad", "IS", "44000")],
        "defects": {"CLEAN": 60, "UNSTRUCTURED_ONLY": 22, "MISSING_COUNTRY": 6,
       "MISSING_TOWN": 7, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 1, "INVALID_COUNTRY": 1},
    },
    "CN": {
        "weight": 4,
        "currency": "CNY",
        "bic": "ICBKCNBJXXX",
        "streets": ["Nanjing Road", "Wangfujing Street", "Beijing Road"],
        "cities": [("Shanghai", "SH", "200000"), ("Beijing", "BJ", "100000"),
                   ("Guangzhou", "GD", "510000")],
        "defects": {"CLEAN": 65, "UNSTRUCTURED_ONLY": 18, "MISSING_COUNTRY": 5,
       "MISSING_TOWN": 6, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 2, "INVALID_COUNTRY": 1},

    },
    "GB": {
        "weight": 3,
        "currency": "GBP",
        "bic": "BARCGB22XXX",
        "streets": ["High Street", "Church Lane", "Station Road", "Victoria Road"],
        "cities": [("London", "LND", "SW1A 1AA"), ("Manchester", "MAN", "M1 1AE"),
                   ("Birmingham", "BIR", "B1 1AA")],
        "defects": {"CLEAN": 82, "UNSTRUCTURED_ONLY": 7, "MISSING_COUNTRY": 3,
       "MISSING_TOWN": 2, "PLACEHOLDER_COUNTRY": 2, "DUPLICATED_TOWN": 2, "INVALID_COUNTRY": 2},
    },
    "MX": {
        "weight": 2,
        "currency": "MXN",
        "bic": "BCMRMXMMXXX",
        "streets": ["Avenida Juarez", "Calle Madero", "Paseo de la Reforma"],
        "cities": [("Mexico City", "CMX", "01000"), ("Guadalajara", "JAL", "44100")],
        "defects": {"CLEAN": 68, "UNSTRUCTURED_ONLY": 16, "MISSING_COUNTRY": 5,
       "MISSING_TOWN": 5, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 2, "INVALID_COUNTRY": 1},
    },
    "NG": {
        "weight": 2,
        "currency": "NGN",
        "bic": "FBNINGLAXXX",
        "streets": ["Broad Street", "Awolowo Road", "Allen Avenue"],
        "cities": [("Lagos", "LA", "100001"), ("Abuja", "FC", "900001")],
        "defects": {"CLEAN": 58, "UNSTRUCTURED_ONLY": 24, "MISSING_COUNTRY": 6,
       "MISSING_TOWN": 7, "PLACEHOLDER_COUNTRY": 3, "DUPLICATED_TOWN": 1, "INVALID_COUNTRY": 1},
    },
}

DEBTOR_WEIGHTS = {
    "CLEAN": 88,
    "UNSTRUCTURED_ONLY": 4,
    "MISSING_COUNTRY": 3,
    "MISSING_TOWN": 2,
    "PLACEHOLDER_COUNTRY": 1,
    "DUPLICATED_TOWN": 1,
    "INVALID_COUNTRY": 1,
}

CHANNELS = {
    "PAIN001_SCORE_PLUS": {"weight": 25, "delta": 19},
    "PROPRIETARY":        {"weight": 15, "delta": 14},
    "RETAIL_APP":         {"weight": 40, "delta": 4},
    "BRANCH":             {"weight": 8,  "delta": -1},
    "MT101_SCORE":        {"weight": 12, "delta": -31},
}


def pick_defect(rng, weights):
    names = list(weights)
    w = [weights[n] for n in names]
    return rng.choices(names, weights=w, k=1)[0]

def pick_corridor(rng):
    names = list(CORRIDORS)
    weights = [CORRIDORS[n]["weight"] for n in names]
    return rng.choices(names, weights=weights, k=1)[0]

def pick_channel(rng):
    names = list(CHANNELS)
    weights = [CHANNELS[n]["weight"] for n in names]
    return rng.choices(names, weights=weights, k=1)[0]

def adjusted_weights(corridor, channel):
    base = dict(CORRIDORS[corridor]["defects"])
    delta = CHANNELS[channel]["delta"]

    new_clean = base["CLEAN"] + delta
    if new_clean > 98:
        new_clean = 98
    if new_clean < 5:
        new_clean = 5

    shift = new_clean - base["CLEAN"]
    old_bad = 100 - base["CLEAN"]
    new_bad = 100 - new_clean

    out = {"CLEAN": new_clean}
    for name, weight in base.items():
        if name != "CLEAN":
            out[name] = weight * new_bad / old_bad
    return out

def make_payment(rng, n, corridor, channel):
    c = CORRIDORS[corridor]
    d_twn, d_prov, d_pst = rng.choice(CANADA_CITIES)
    c_twn, c_prov, c_pst = rng.choice(c["cities"])

    return {
        "end_to_end_id": f"E2E-{n:06d}",
        "uetr": str(uuid.uuid4()),
        "interbank_settlement_amount": f"{rng.uniform(100, 10000):.2f}",
        "interbank_settlement_currency": c["currency"],
        "instd_amount": f"{rng.uniform(100, 50000):.2f}",
        "instd_currency": "CAD",
        "charge_bearer": "SLEV",
        "pmt_tp_inf_lcl_instrm_cd": channel,

        "debtor_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "debtor_agent_bic": "WSPLCATTXXX",
        "debtor_strt_nm": rng.choice(CANADA_STREETS),
        "debtor_bldg_nb": str(rng.randint(1, 999)),
        "debtor_pst_cd": d_pst,
        "debtor_twn_nm": d_twn,
        "debtor_ctry": "CA",

        "creditor_name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
        "creditor_agent_bic": c["bic"],
        "creditor_account_iban": f"{corridor}{rng.randint(10,99)}{c['bic'][:4]}{rng.randint(10**11, 10**12-1)}",
        "creditor_strt_nm": rng.choice(c["streets"]),
        "creditor_bldg_nb": str(rng.randint(1, 999)),
        "creditor_pst_cd": c_pst,
        "creditor_twn_nm": c_twn,
        "creditor_ctry": corridor,
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
            corridor = pick_corridor(rng)
            channel = pick_channel(rng)
            tx = make_payment(rng, n, corridor, channel)
            defect = pick_defect(rng, DEBTOR_WEIGHTS)
            tx = apply_defects(tx, "debtor", defect)
            cdt_defect = pick_defect(rng, adjusted_weights(corridor, channel))
            tx = apply_defects(tx, "creditor", cdt_defect)
            answer_key.append({
                "uetr": tx["uetr"],
                "corridor": corridor,
                "party": "debtor",
                "defect": defect,
                "source_file": f"msgs-{file_no:06d}.xml",
            })
            answer_key.append({
                "uetr": tx["uetr"],
                "corridor": corridor,
                "party": "creditor",
                "defect": cdt_defect,
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
    writer = csv.DictWriter(f, fieldnames=["uetr", "corridor", "party", "defect", "source_file"])
    writer.writeheader()
    writer.writerows(answer_key)

broken_folder = "data/bronze/ingest_date=2026-07-15"
with open(f"{broken_folder}/msgs-truncated.xml", "w", encoding="utf-8") as f:
    f.write(xml[:800])