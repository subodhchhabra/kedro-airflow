import os
import sys
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from slugify import slugify

from kedro_airflow.runner import AirflowRunner

# Get our project source onto the python path
sys.path.append("{{ project_path }}/src")

# fmt: off
{{import_get_config}}  # isort:skip
{{import_create_catalog}}  # isort:skip
{{import_create_pipeline}}  # isort:skip
# fmt: on

# Path to Kedro project directory
project_path = "{{ project_path }}"


# Default arguments for all the Airflow operators
default_args = {
    "owner": "kedro",
    "start_date": datetime(2015, 6, 1),
    "depends_on_past": True,
    "wait_for_downstream": True,
    "email": ["airflow@example.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


# fetch arguments for specific Airflow operators
def operator_specific_arguments(task_id):
    return {}


# Injest Airflow's context, may modify the data catalog as necessary
def process_context(data_catalog, **kwargs):
    # drop unpicklable things
    for key in ["dag", "conf", "macros", "task", "task_instance", "ti", "var"]:
        del kwargs[key]

    data_catalog.add_feed_dict({"airflow_context": kwargs}, replace=True)

    return data_catalog


# Construct a DAG and then call into Kedro to have the operators constructed
dag = DAG(
    slugify("{{ project_name }}"),
    default_args=default_args,
    schedule_interval=timedelta(days=1),
)

config = get_config(project_path)
data_catalog = create_catalog(config)
pipeline = create_pipeline()

runner = AirflowRunner(
    dag=dag,
    process_context=process_context,
    operator_arguments=operator_specific_arguments,
)

runner.run(pipeline, data_catalog)
