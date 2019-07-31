package:
	rm -Rf dist
	python setup.py sdist bdist_wheel

install: package
	pip install -U dist/*.whl

install-pip-setuptools:
	python -m pip install -U "pip>=18.0, <19.0" "setuptools>=38.0, <39.0" wheel

lint:
	isort
	pylint -j 0 --disable=unnecessary-pass kedro_airflow
	pylint -j 0 --disable=missing-docstring,redefined-outer-name,no-self-use,invalid-name tests
	pylint -j 0 --disable=missing-docstring,no-name-in-module features
	flake8 kedro_airflow tests features

test:
	pytest tests

e2e-tests:
	behave

legal:
	python tools/license_and_headers.py

clean:
	rm -rf build dist pip-wheel-metadata .pytest_cache
	find . -regex ".*/__pycache__" -exec rm -rf {} +
	find . -regex ".*\.egg-info" -exec rm -rf {} +
