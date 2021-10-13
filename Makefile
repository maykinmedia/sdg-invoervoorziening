setup: venv install

venv:
	python3 -m venv venv

install:
	venv/bin/python -m pip install -r requirements/dev.txt

compile:
	./bin/compile_dependencies.sh

