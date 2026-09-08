from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, when, lit, array_contains, substring
import time
spark = SparkSession.builder.appName("silver").getOrCreate()

BRONZE = "data/bronze/ingest_date=*"
SILVER = "data/silver"

start = time.time()

def defect_rule(party):
    town = col(f"{party}_town")
    country = col(f"{party}_country")
    lines = col(f"{party}_adr_lines")
    return (
        when(town.isNull() & lines.isNotNull(), lit("UNSTRUCTURED_ONLY"))
        .when(country.isNull() & town.isNotNull(), lit("MISSING_COUNTRY"))
        .when(town.isNull() & country.isNotNull(), lit("MISSING_TOWN"))
        .when(country == "NOTPROVIDED", lit("PLACEHOLDER_COUNTRY"))
        .when(country == "UK", lit("INVALID_COUNTRY"))
        .when(lines.isNotNull() & array_contains(lines, town), lit("DUPLICATED_TOWN"))
        .otherwise(lit("CLEAN"))
    )
wide = spark.read.format("xml").option("rowTag", "FIToFICstmrCdtTrf").load(BRONZE)

silver = wide.select(
    col("GrpHdr.MsgId").alias("msg_id"),
    col("GrpHdr.CreDtTm").alias("creation_dt"),
    explode(col("CdtTrfTxInf")).alias("tx")
).select(
    "msg_id",
    "creation_dt",
    col("tx.PmtId.UETR").alias("uetr"),
    col("tx.PmtId.EndToEndId").alias("end_to_end_id"),
    col("tx.IntrBkSttlmAmt._VALUE").alias("amount"),
    col("tx.IntrBkSttlmAmt._Ccy").alias("currency"),
    col("tx.Dbtr.Nm").alias("debtor_name"),
    col("tx.DbtrAgt.FinInstnId.BICFI").alias("debtor_bic"),
    col("tx.Dbtr.PstlAdr.StrtNm").alias("debtor_street"),
    col("tx.Dbtr.PstlAdr.PstCd").alias("debtor_postcode"),
    col("tx.Dbtr.PstlAdr.TwnNm").alias("debtor_town"),
    col("tx.Dbtr.PstlAdr.Ctry").alias("debtor_country"),
    col("tx.Dbtr.PstlAdr.AdrLine").alias("debtor_adr_lines"),
    col("tx.Cdtr.Nm").alias("creditor_name"),
    col("tx.CdtrAgt.FinInstnId.BICFI").alias("creditor_bic"),
    col("tx.Cdtr.PstlAdr.StrtNm").alias("creditor_street"),
    col("tx.Cdtr.PstlAdr.PstCd").alias("creditor_postcode"),
    col("tx.Cdtr.PstlAdr.TwnNm").alias("creditor_town"),
    col("tx.Cdtr.PstlAdr.Ctry").alias("creditor_country"),
    col("tx.Cdtr.PstlAdr.AdrLine").alias("creditor_adr_lines"),
)

tagged = silver \
    .withColumn("debtor_defect", defect_rule("debtor")) \
    .withColumn("creditor_defect", defect_rule("creditor")) \
    .withColumn("corridor", substring(col("creditor_bic"), 5, 2))

clean = tagged.filter((col("debtor_defect") == "CLEAN") & (col("creditor_defect") == "CLEAN"))
quarantine = tagged.filter((col("debtor_defect") != "CLEAN") | (col("creditor_defect") != "CLEAN"))

clean.write.mode("overwrite").parquet(f"{SILVER}/payments")
quarantine.write.mode("overwrite").parquet(f"{SILVER}/quarantine")

print("clean:", clean.count(), "quarantine:", quarantine.count())
print("seconds:", round(time.time() - start, 1))