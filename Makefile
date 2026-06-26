.PHONY: install test lint fetch-bronze

install:
	pip install -e packages/racedata
	pip install pytest ruff

test:
	pytest

lint:
	ruff check .

fetch-bronze:
	@echo "Copy the Cork results PDFs into data/bronze/cork/<year>/results_<distance>.pdf"
	@echo "(Phase 5 will replace this with racedata.scrape writing into the bronze store.)"
