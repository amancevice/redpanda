.PHONY: all clean

all: Pipfile.lock

Pipfile.lock: Pipfile
	pipenv lock -r

clean:
	pipenv --rm
	rm Pipfile.lock
