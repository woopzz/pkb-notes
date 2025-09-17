# Notes API (PKB)

A part of the PKB app. The API provides endpoints to manage notes and tags.

### Features

- Create, update and delete notes.
- Create, update and delete tags.

### Development

Use devcontainer.

When you get into the dev container for the first time, you should apply database migrations:
```bash
./scripts/migrate
```

There are several helpful scripts:
```bash
# Run migrations.
./scripts/migrate

# Run all tests.
./scripts/test

# Run only the `test_read_note` test, capture the output, display SQL query info.
DB_ENGINE_ECHO=1 ./scripts/test -rA ./tests/test_note.py::test_read_note

# Run the Ruff linter.
./scripts/lint
```
