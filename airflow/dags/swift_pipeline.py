from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from pendulum import datetime, duration
from datetime import timedelta
import os
import requests, json

def dbt_failures():
    path = "/usr/local/airflow/include/swift_gold/target/run_results.json"
    try:
        with open(path) as f:
            results = json.load(f)
        failed = [
            f"{r['unique_id']}: {r['status']}"
            for r in results["results"]
            if r["status"] not in ("success", "pass")
        ]
        return "\n".join(failed) if failed else "no dbt failures recorded"
    except Exception as e:
        return f"could not read run_results.json: {e}"


def notify_failure(context):
    try:
        print(f"Context keys: {list(context.keys())}")
        ti = context["task_instance"]
        if ti.task_id == "dbt_build":
            error = dbt_failures()[:800]
        else:
            error = str(context.get("exception", "unknown"))[:800]
        message = (
            f"**SWIFT pipeline failed**\n"
            f"Task: `{ti.task_id}`\n"
            f"DAG: `{ti.dag_id}`\n"
            f"Run: `{context['run_id']}`\n"
            f"Try: {ti.try_number}\n"
            f"```{error}```"
        )
        requests.post(
            os.environ["DISCORD_WEBHOOK_URL"],
            json={"content": message},
            timeout=10,
        )
    except Exception as e:
        print(f"Failure notification failed: {e}")

default_args = {
    "retries": 3,
    "retry_delay": duration(minutes=5),
    "retry_exponential_backoff": True,
    "max_retry_delay": duration(minutes=30),
    "on_failure_callback": notify_failure
}

with DAG(
    dag_id="swift_pipeline",
    start_date=datetime(2026, 10, 14),
    schedule= timedelta(days=3),
    catchup= False,
    default_args=default_args,
    tags=["swift"],
):

    silver_parse = DatabricksRunNowOperator(
        task_id="silver_parse",
        databricks_conn_id="databricks_default",
        job_id=266398993463825,
    )

    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="cd /usr/local/airflow/include/swift_gold && dbt build --profiles-dir .",
    )

    silver_parse >> dbt_build