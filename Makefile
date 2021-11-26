setup: venv install

venv:
	python3 -m venv venv

install:
	venv/bin/python -m pip install -r requirements/dev.txt

compile:
	./bin/compile_dependencies.sh

schema:
	./bin/generate_schema.sh

admin:
	./bin/generate_admin_index_fixture.sh

