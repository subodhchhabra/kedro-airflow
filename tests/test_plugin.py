import os
from pathlib import Path

from kedro_airflow.plugin import commands, import_line


def a_function():  # pragma: no cover
    pass


def test_import_line(mocker):
    mocker.patch("kedro_airflow.plugin.get_project_context", return_value=a_function)
    assert import_line("bob") == "from tests.test_plugin import a_function as bob"


def test_create_airflow_dag(cli_runner, mocker):
    project_context = {
        "project_path": Path.cwd(),
        "get_config": a_function,
        "create_catalog": a_function,
        "create_pipeline": a_function,
        "project_name": "Hello '-_⛄_-' world !!!",
    }
    mocker.patch("kedro_airflow.plugin.get_project_context", project_context.get)
    result = cli_runner.invoke(commands, ["airflow", "create"])
    assert result.exit_code == 0
    assert (Path.cwd() / "airflow_dags" / "hello_world_dag.py").exists()


def test_deploy_airflow_dag(cli_runner, mocker):
    project_context = {
        "project_path": Path("/my_project"),
        "project_name": "Hello '-_⛄_-' world !!!",
    }
    mocker.patch("kedro_airflow.plugin.get_project_context", project_context.get)
    copy = mocker.patch("kedro_airflow.plugin.copy")
    mocker.patch.dict(os.environ, {"AIRFLOW_HOME": str(Path.cwd())})
    result = cli_runner.invoke(commands, ["airflow", "deploy"])
    assert result.exit_code == 0
    copy.assert_called_with(
        "/my_project/airflow_dags/hello_world_dag.py", str(Path.cwd() / "dags")
    )
