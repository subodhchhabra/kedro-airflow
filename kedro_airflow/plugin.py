""" Kedro plugin for running a project with Airflow """

import os
from pathlib import Path
from shutil import copy

import click
from click import secho
from jinja2 import Template
from kedro.cli import get_project_context
from slugify import slugify


@click.group(name="Airflow")
def commands():
    """ Kedro plugin for running a project with Airflow """
    pass


def import_line(name):
    """generate an import line for something in the project_context"""
    func = get_project_context(name)
    res = "from {} import {}".format(func.__module__, func.__name__)
    if func.__name__ != name:
        res = "{} as {}".format(res, name)
    return res


@commands.group(name="airflow")
def airflow_commands():
    """Run project with Airflow"""
    pass


def _get_dag_filename():
    project_path = get_project_context("project_path")
    project_name = get_project_context("project_name")
    dest_dir = project_path / "airflow_dags"
    return dest_dir / (slugify(project_name, separator="_") + "_dag.py")


@airflow_commands.command()
def create():
    """Create an Airflow DAG for a project"""

    src_file = Path(__file__).parent / "dag_template.py"
    dest_file = _get_dag_filename()
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    template = Template(
        src_file.read_text(encoding="utf-8"), keep_trailing_newline=True
    )
    dest_file.write_text(
        template.render(
            project_name=get_project_context("project_name"),
            import_get_config=import_line("get_config"),
            import_create_catalog=import_line("create_catalog"),
            import_create_pipeline=import_line("create_pipeline"),
            project_path=get_project_context("project_path"),
        ),
        encoding="utf-8",
    )

    secho("")
    secho("An Airflow DAG has been generated in:", fg="green")
    secho(str(dest_file))
    secho("This file should be copied to your Airflow DAG folder.", fg="yellow")
    secho(
        "The Airflow configuration can be customized by editing this file.", fg="green"
    )
    secho("")
    secho(
        "This file also contains the path to the config directory, this directory will need to "
        "be available to Airflow and any workers.",
        fg="yellow",
    )
    secho("")
    secho(
        "Additionally all data sets must have an entry in the data catalog.",
        fg="yellow",
    )
    secho(
        "And all local paths in both the data catalog and log config must be absolute paths.",
        fg="yellow",
    )
    secho("")


@airflow_commands.command()
def deploy():
    """Copy DAG to Airflow home"""
    airflow_home = Path(os.environ.get("AIRFLOW_HOME", "~/airflow"))
    dags_folder = airflow_home.resolve() / "dags"
    dag_file = _get_dag_filename()
    secho("Copying {} to {}".format(str(dag_file), str(dags_folder)))
    copy(str(dag_file), str(dags_folder))
