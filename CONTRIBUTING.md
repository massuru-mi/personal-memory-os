# Contributing

Contributions are welcome under the MIT License.

Keep provider-specific behavior behind the provider-neutral PMO protocol and preserve the storage ownership boundaries. New schema versions require migrations and tests. Changes that can modify user data must include rollback/backup considerations and fail-closed behavior.

Before submitting:

```bash
python -m pip install -e '.[dev]'
pytest
ruff check .
```
