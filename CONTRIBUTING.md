# Contributing to Arabic Engine

Thank you for your interest in contributing! Here are guidelines to help you get started.

## Getting Started

1. **Fork** the repository and clone your fork locally.
2. Create a **virtual environment** and install dev dependencies:

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Linux / macOS
   pip install -e ".[dev]"
   ```

3. Create a **feature branch** from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) conventions.
- Use **type hints** for all function signatures.
- Run the linter before committing:

  ```bash
  ruff check .
  ```

### Testing

- Add tests for any new functionality in the `tests/` directory.
- Run the test suite:

  ```bash
  pytest
  ```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` — a new feature
- `fix:` — a bug fix
- `docs:` — documentation only changes
- `test:` — adding or updating tests
- `refactor:` — code change that neither fixes a bug nor adds a feature
- `chore:` — maintenance tasks

Example: `feat: add morphological analyser for broken plurals`

### Pull Requests

1. Keep PRs focused — one logical change per PR.
2. Write a clear description of **what** changed and **why**.
3. Ensure CI passes (linting + tests).
4. Request a review from a maintainer.

## Reporting Issues

- Use the **Bug Report** or **Feature Request** issue templates.
- Provide enough detail to reproduce the problem or understand the request.

## Code of Conduct

Be respectful and constructive. We are building something meaningful together.
