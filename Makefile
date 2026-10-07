.PHONY: help setup check nb

help:
	@echo "setup     install the environment (uv sync)"
	@echo "check     verify your machine is ready for the cohort"
	@echo "nb        open the environment notebook (uv run jupyter notebook)"

setup:
	uv sync

# The same checks the environment notebook runs, without opening Jupyter.
check:
	@bash 00_Prerequisites/scripts/setup_check.sh

# Open the environment notebook. Run `make setup` first.
nb:
	uv run jupyter notebook 01_First_Steps/S1_Enterprise_Dev_Environment.ipynb
