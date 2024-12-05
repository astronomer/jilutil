#!/usr/bin/env just --justfile
set dotenv-load := true
SRC_DIR := "jilutil"
EXTRAS := "dev"
VERSION := `echo $(python3 -c 'from jilutil import __version__; print(__version__)')`
PYTHON := `which python || which python3`

default:
    @just --choose

# Print this help text
help:
    @just --list

# Install project and python dependencies (incl. pre-commit) locally
install EDITABLE='':
    {{ PYTHON }} -m pip install {{EDITABLE}} '.[{{EXTRAS}}]'

# Install pre-commit to local project
install-precommit: install
    pre-commit install

# Update the baseline for detect-secrets / pre-commit
update-secrets:
    detect-secrets scan  > .secrets.baseline  # pragma: allowlist secret

# Run pytests with config from pyproject.toml
test:
    {{ PYTHON }} -m pytest -c pyproject.toml

# Test and emit a coverage report
test-with-coverage:
    {{ PYTHON }} -m pytest -c pyproject.toml --cov=./ --cov-report=xml

# Run ruff and black (normally done with pre-commit)
lint:
    ruff check .

# Remove temporary or build folders
clean:
    rm -rf build dist site *.egg-info
    find . | grep -E "(__pycache__|\.pyc|\.pyo$$)" | xargs rm -rf

# Tag as v$(<src>.__version__) and push to Github
tag:
    # Delete tag if it already exists
    git tag -d v{{VERSION}} || true
    # Tag and push
    git tag v{{VERSION}}

# Push tag to Github
deploy-tag: tag
    git push origin v{{VERSION}}

# Push tag to Github
deploy: deploy-tag

# Build the project
build: install clean
    {{ PYTHON }} -m build

# Upload to TestPyPi for testing (note: you can only use each version once)
upload-testpypi: clean install build
    python -m twine check dist/*
    TWINE_USER=${TWINE_USER} TWINE_PASS=${TWINE_PASS} python -m twine upload --repository testpypi dist/*

# Upload to PyPi - DO NOT USE THIS, GHA DOES THIS AUTOMATICALLY
upload-pypi: clean install build
    python -m twine check dist/*
    TWINE_USER=${TWINE_USER} TWINE_PASS=${TWINE_PASS} python -m twine upload dist/*
