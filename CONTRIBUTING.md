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

## Commit Signing (Required)

All commits **must** be verified. Unverified commits will be flagged by CI.

### 1. Configure Git with your verified GitHub email

Use the email address that is verified in your GitHub account
(Settings → Emails):

```bash
git config --global user.email "you@example.com"
git config --global user.name  "Your Name"
```

### 2. Set up GPG commit signing

Generate a key (if you don't already have one):

```bash
gpg --full-generate-key   # choose RSA 4096, no expiry is fine
```

Find the key ID you just created:

```bash
gpg --list-secret-keys --keyid-format=long
# Look for the line that starts with "sec", e.g.:
# sec   rsa4096/3AA5C34371567BD2 2024-01-01 [SC]
# The key ID is the part after the slash: 3AA5C34371567BD2
```

Tell Git to use that key and sign all commits automatically:

```bash
git config --global user.signingkey 3AA5C34371567BD2
git config --global commit.gpgsign true
```

Export the public key and add it to your GitHub account
(Settings → SSH and GPG keys → New GPG key):

```bash
gpg --armor --export 3AA5C34371567BD2
```

For a full step-by-step guide (including Windows, macOS, and Linux
specifics) see [`docs/COMMIT_SIGNING.md`](docs/COMMIT_SIGNING.md).

### 3. Verify a commit before pushing

```bash
git log --show-signature -1
```

The output should contain `gpg: Good signature from …`. If it shows
`gpg: BAD signature` or nothing at all, revisit the steps above.

### Pull Requests

1. Keep PRs focused — one logical change per PR.
2. Write a clear description of **what** changed and **why**.
3. Ensure CI passes (linting + tests + commit verification).
4. All commits in the PR must be **verified** — the `verify-commits`
   workflow will fail otherwise.
5. Request a review from a maintainer.

## Reporting Issues

- Use the **Bug Report** or **Feature Request** issue templates.
- Provide enough detail to reproduce the problem or understand the request.

## Code of Conduct

Be respectful and constructive. We are building something meaningful together.
