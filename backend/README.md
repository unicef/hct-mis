# Development

## VSCode setup

```sh
python3.9 -m venv venv
docker-compose build
docker-compose run --rm backend poetry export -f requirements.txt --output venv/requirements.txt
python3.9 -m pip install -r venv/requirements.txt --require-hashes
```

CMD + Shift + P => `Python: Select interpreter`
Provide path to `./backend/venv/bin/python3`

Oneliner to refresh your packages (from `backend` dir):

```sh
sh -c ". ./venv/bin/activate ; docker-compose run --rm backend poetry export -f requirements.txt --output venv/requirements.txt ; python3.9 -m pip install -r venv/requirements.txt --require-hashes"
```

To ensure that your change will pass all the static checks, run this command:

```shell
docker-compose run --rm backend sh -c "black . && isort . && flake8 . && mypy ."
```

## Testing

To run tests, you call `pytest`. Example invocation:

```shell
docker-compose run --rm backend pytest --reuse-db -n logical
```

## Linting

To run linting, you use `flake8`. Example invocation:

```shell
docker-compose run --rm backend flake8 .
```

## Formatting

To run formatting, you use `black`. Example invocation:

```shell
docker-compose run --rm backend black .
```

## Isort

To run isort, you use `isort`. Example invocation:

```shell
docker-compose run --rm backend isort .
```

## Mypy

To run mypy, you use `mypy`. Example invocation:

```shell
docker-compose run --rm backend mypy .
```
