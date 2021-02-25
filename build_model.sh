#!/usr/bin/env bash

BASEDIR=$(dirname "$0")

export PYTHONPATH="${PYTHONPATH}:${BASEDIR}/.venv/lib/"

source .venv/bin/activate

python nba_odds/application/build_models.py