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

beat:
	./bin/generate_celery_beat_fixture.sh

migrations:
	venv/bin/python src/manage.py makemigrations

migrate:
	venv/bin/python src/manage.py migrate

graph:
	venv/bin/python src/manage.py graph_models -o data/models.png

clean:
	find ./log -name '*.log*' -exec rm -rf {} \;
