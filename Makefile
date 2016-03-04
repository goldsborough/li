.PHONY: clean-pyc clean-build docs clean

help:
	@echo "clean - remove all build, test, coverage and Python artifacts."
	@echo "clean-build - remove build artifacts."
	@echo "clean-pyc - remove Python file artifacts."
	@echo "clean-test - remove test and coverage artifacts."
	@echo "lint - check style with flake8."
	@echo "test - run tests quickly with the default Python."
	@echo "coverage - check code coverage quickly with the default Python."
	@echo "bump - bumps the version."
	@echo "test-register - register the project at TestPyPI."
	@echo "register - register the project at PyPI."
	@echo "test-upload - package and upload a releaes to TestPyPI."
	@echo "upload - package and upload a upload to PyPI."
	@echo "dist - package."
	@echo "install - install the package to the active Python's site-packages."

clean: clean-build clean-pyc clean-test

clean-build:
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

clean-test:
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/

lint:
	pylint license

test:
	python -m pytest tests

coverage:
	coverage run -m pytest
	coverage report -m
	coverage html
	open htmlcov/index.html

bump:
	python -m scripts.bump

dist: clean
	python setup.py sdist
	python setup.py bdist_wheel

test-register:
	python setup.py register -r test

register:
	python setup.py register

test-upload:
	twine upload -r test $(wildcard dist/*)

upload:
	twine upload $(wildcard dist/*)

install:
	python setup.py install
