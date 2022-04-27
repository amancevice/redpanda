PYFILES := $(shell find redpanda tests -name '*.py')
SDIST   := dist/$(shell python setup.py --fullname 2> /dev/null).tar.gz

all: test

build: $(SDIST)

clean:
	rm -rf dist

test: | .venv
	pipenv run pytest

upload: $(SDIST)
	git diff HEAD --quiet
	pipenv run twine upload $<

.PHONY: all build clean test upload

$(SDIST): $(PYFILES) | .venv
	pipenv run pytest
	python setup.py sdist

.venv: Pipfile
	mkdir -p .venv
	pipenv install --dev
	touch .venv
