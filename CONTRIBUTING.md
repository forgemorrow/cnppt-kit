# Contributing to `cnppt-kit`

Contributions to CJK layout rules, WPS/Office font compatibility profiles, scenario templates, and unit tests are welcome.

## Development Setup

```bash
pip install -e ".[dev]"
pytest -q
python scripts/benchmark_linter.py
```

## Guidelines

1. Keep all templates, themes, and OOXML generators 100% original and offline-safe (no CDN fonts or external network calls at build/preview time).
2. Avoid copying source code from third-party repositories (especially copyleft AGPL-3.0 projects). Cite reference inspirations cleanly in documentation instead.
3. Add pytest coverage inspecting the generated `.pptx` XML/shapes and CJK linter behavior for every layout or rule change.
4. Use Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `ci:`, `refactor:`, `chore:`).
