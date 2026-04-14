# Commit Signing Guide

This guide walks you through generating a GPG key, adding it to your
GitHub account, and configuring Git to sign every commit automatically —
on **Windows**, **macOS**, and **Linux**.

---

## Why signed commits matter

GitHub marks a commit as **Verified** only when the GPG (or SSH)
signature matches a public key registered against your account *and* the
committer email matches a verified email on that account. Unverified
commits are rejected by the `verify-commits` CI workflow in this
repository.

---

## Prerequisites

| Platform | Install GPG |
|----------|-------------|
| **Windows** | Download [Gpg4win](https://gpg4win.org/) and run the installer. The `gpg` command is then available in PowerShell and Git Bash. |
| **macOS** | `brew install gnupg` (requires [Homebrew](https://brew.sh/)) |
| **Linux (Debian/Ubuntu)** | `sudo apt-get install gnupg` |
| **Linux (Fedora/RHEL)** | `sudo dnf install gnupg2` |

Confirm the installation:

```bash
gpg --version
```

---

## Step 1 — Configure Git with your verified GitHub email

Go to **GitHub → Settings → Emails** and note the primary (verified)
email address. Use that exact address:

```bash
git config --global user.email "you@example.com"
git config --global user.name  "Your Name"
```

---

## Step 2 — Generate a GPG key

```bash
gpg --full-generate-key
```

When prompted:

1. **Key type** → `RSA and RSA` (option 1)
2. **Key size** → `4096`
3. **Expiry** → `0` (does not expire) — or choose a date you prefer
4. **Real name** → your name (can match GitHub display name)
5. **Email** → the verified GitHub email from Step 1
6. **Comment** → leave blank or add a note
7. Confirm with `O` (Okay) and enter a strong passphrase

---

## Step 3 — Find your key ID

```bash
gpg --list-secret-keys --keyid-format=long
```

Example output:

```
sec   rsa4096/3AA5C34371567BD2 2024-01-01 [SC]
      ABCDEF1234567890ABCDEF1234567890ABCDEF12
uid                 [ultimate] Your Name <you@example.com>
ssb   rsa4096/42B317FD4BA89E7A 2024-01-01 [E]
```

Your **key ID** is the hex string after the slash on the `sec` line —
`3AA5C34371567BD2` in the example above.

---

## Step 4 — Tell Git to use your key

```bash
git config --global user.signingkey 3AA5C34371567BD2
git config --global commit.gpgsign true
```

> **Windows / macOS extra step** — if Git cannot find the `gpg`
> binary, point it explicitly:
>
> ```bash
> # macOS (Homebrew)
> git config --global gpg.program $(which gpg)
>
> # Windows (Gpg4win — adjust path if needed)
> git config --global gpg.program "C:/Program Files (x86)/GnuPG/bin/gpg.exe"
> ```

---

## Step 5 — Export your public key and add it to GitHub

```bash
gpg --armor --export 3AA5C34371567BD2
```

Copy the entire output (starting with `-----BEGIN PGP PUBLIC KEY
BLOCK-----`), then:

1. Go to **GitHub → Settings → SSH and GPG keys**
2. Click **New GPG key**
3. Paste the key and click **Add GPG key**

---

## Step 6 — Verify your setup

Make a test commit and inspect the signature:

```bash
git commit --allow-empty -m "test: verify GPG signing"
git log --show-signature -1
```

You should see output similar to:

```
commit abc123...
gpg: Signature made Mon 01 Jan 2024 00:00:00 UTC
gpg:                using RSA key 3AA5C34371567BD2
gpg: Good signature from "Your Name <you@example.com>" [ultimate]
```

GitHub will then show a green **Verified** badge on the commit.

---

## Signing commits retroactively (before pushing)

If you have already made unsigned commits on a branch, re-sign them with
an interactive rebase:

```bash
# Replace <base-branch> with main (or the branch you forked from)
git rebase --exec 'git commit --amend --no-edit -S' <base-branch>
```

Then force-push:

```bash
git push --force-with-lease origin your-branch-name
```

---

## Troubleshooting

### `gpg: signing failed: No secret key`

Your `user.signingkey` does not match any key in your keyring. Re-run
`gpg --list-secret-keys --keyid-format=long` and copy the correct ID.

### `gpg: signing failed: Inappropriate ioctl for device`

GPG cannot open a passphrase prompt in a non-interactive terminal.
Fix it by adding the following to your shell profile (`~/.bashrc`,
`~/.zshrc`, etc.):

```bash
export GPG_TTY=$(tty)
```

Then reload: `source ~/.bashrc` (or open a new terminal).

### `error: gpg failed to sign the data`

On macOS, the agent may have timed out. Restart it:

```bash
gpgconf --kill gpg-agent
gpg-agent --daemon
```

### Commit still shows "Unverified" on GitHub

1. Confirm the email in the commit (`git log --format="%ae" -1`) exactly
   matches a **verified** email in GitHub Settings → Emails.
2. Confirm the GPG public key is added to your GitHub account (Step 5).
3. Check that the key has not expired (`gpg --list-keys`).

### Windows: passphrase dialog does not appear

Install [Gpg4win](https://gpg4win.org/) which includes **Kleopatra** — a
GUI pinentry that handles passphrase prompts properly in Windows
environments.

---

## Further reading

- [GitHub Docs — Managing commit signature verification](https://docs.github.com/en/authentication/managing-commit-signature-verification)
- [Git documentation — Signing your work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [GnuPG handbook](https://www.gnupg.org/documentation/)
