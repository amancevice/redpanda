PYFILES := $(shell find redpanda tests -name '*.py')
SDIST   := dist/$(shell python setup.py --fullname).tar.gz

all: $(SDIST)

clean:
	rm -rf dist

upload: Brewfile.lock.json $(SDIST)
	pipenv run twine upload $(SDIST)

.PHONY: all clean upload

$(SDIST): $(PYFILES) Pipfile.lock
	pipenv run pytest
	python setup.py sdist

Brewfile.lock.json: Brewfile
	brew bundle

Pipfile.lock: Pipfile
	pipenv install --dev
