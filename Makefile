include $(PWD)/.env
PYTHON=./.venv/bin/python3

init: venv install
venv:
	python3.11 venv --python /usr/bin/python3.11
install:
	$(PYTHON) -m pip install -e ".[dev,testing]"

lint: opt=
lint-fix: opt=--fix
lint lint-fix:
	$(PYTHON) -m ruff check $(opt) --config ./pyproject.toml ./

tests:
	$(PYTHON) -m pytest ./
