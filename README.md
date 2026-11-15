# King Phisher

> A phishing-campaign toolkit for security-awareness testing, kept running on a current Python
> after upstream stopped maintaining it.

![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![Fork](https://img.shields.io/badge/-fork-B4232C?style=flat-square)
![Upstream](https://img.shields.io/badge/upstream-unmaintained-444?style=flat-square)

## At a glance

| | |
| --- | --- |
| **Kind** | Fork |
| **Status** | Active |
| **Language** | Python |
| **Requires** | Python 3.12+ (server side) |
| **License** | BSD-3-Clause |
| **Upstream** | CrimsonForge-io/king-phisher |
| **Scope** | Authorized testing only |
| **Skill area** | Social engineering |

## Why

King Phisher runs phishing-simulation campaigns to measure and improve an organisation's
real-world susceptibility, with a GUI client, a server, and template-driven emails and landing
pages. Upstream has said outright it's no longer maintained, and the maintainer confirmed on an
open issue that King Phisher 2.0 is a from-scratch rewrite carrying none of this codebase over —
so nothing broken here was going to get fixed. This fork fixes what's actually broken on a current
Python, without touching the campaign logic or the GTK client UI.

## What this shows

- Social engineering: this is the toolkit I use for authorized phishing-simulation campaigns, and
  this fork is why it still runs.
- Diagnosing a dead import chain down to the exact removed stdlib module, then rebuilding the
  affected code on its modern replacement instead of patching around it.
- Verifying a fix actually works end-to-end (a real SMTP client, not just "it imports now") — see
  [What changed](#what-changed).

## Requirements

- Python 3.12 or newer for the server/dev side this fork touches
- System packages for the full client+server install: GTK, PostgreSQL (handled by
  `tools/install.sh`)
- Tried on: Arch Linux, Kali Linux, Parrot OS

## Install

Two paths: the full install (GTK client + server, needs system packages), or just the Python/dev
side this fork's fixes live in, which needs nothing beyond Python.

### Full install (client + server) — same command on Arch, Kali and Parrot

`tools/install.sh` detects your distro and installs whatever system packages it needs (GTK,
PostgreSQL, etc.). Unchanged from upstream — see `INSTALL.md` for the distro-specific detail:

```bash
git clone https://github.com/thecyberfarhan/king-phisher.git
cd king-phisher
sudo bash tools/install.sh
```

### Just the dev/Python side (this fork's fixes, no GTK needed)

Only touches `king_phisher.server` and the shared code this fork fixed and tested — the GTK
client itself still needs the full install above. Same command on Arch, Kali and Parrot once
`python3`, `pip` and `git` are installed:

```bash
git clone https://github.com/thecyberfarhan/king-phisher.git
cd king-phisher
tools/devshell.sh
```

That creates `.venv/`, installs `requirements.txt` into it, and drops you into a shell with it
active.

## Usage

### Open a dev shell with the fork's dependencies installed

```bash
tools/devshell.sh
```

### Run one command inside that environment without staying in it

```bash
tools/devshell.sh python3 -c "import king_phisher.server.database.models"
```

### Start the server (full install only)

```bash
king-phisher-server -c server_config.yml
```

See upstream's [wiki](https://github.com/securestate/king-phisher/wiki) for configuring a
campaign, the client, and template files — unchanged in this fork.

## Options

`tools/devshell.sh` itself takes no flags: run it alone for an interactive shell, or
`tools/devshell.sh <command>` to run one command inside the environment and return. Everything
else — the server config file, the GTK client, campaign and template options — is upstream's,
unchanged; see `INSTALL.md` and the wiki linked above.

## What's inside

| Part | What it is | Touched by this fork |
| --- | --- | --- |
| `king_phisher/server/` | Server: SMTP sending, database, web server for landing pages | Yes — the two fixes below |
| `king_phisher/client/` | GTK campaign-editor and dashboard UI | No |
| `tools/install.sh` | Upstream's full system installer | No |
| `tools/devshell.sh` | Venv lifecycle for the dev/Python side | Added by this fork |
| `requirements.txt` | Dependency floors for the server/dev side | Added by this fork |

## Comparison

| | Upstream `CrimsonForge-io/king-phisher` | This fork |
| --- | --- | --- |
| `smtp_server.py` on Python 3.12+ | Crashes on import (`asyncore`/`smtpd` removed by PEP 594) | Rebuilt on `asyncio` via `aiosmtpd`, same public API |
| `server.database.models` import | Crashes (`sqlalchemy.Binary` removed in SQLAlchemy 1.4+) | Fixed: swapped for `sqlalchemy.LargeBinary` |
| Dependency versions | `Pipfile` hard-pins ~40 packages to exact 2019 releases, no stated Python floor | `requirements.txt` with `>=` floors; verified installing and importing cleanly on Python 3.14 |
| Dev environment | `install.sh` is a single `sudo bash` system installer, no venv story | `tools/devshell.sh`: creates/updates a `.venv`, only ever active inside a subshell |

## What changed

### Fixed: `smtp_server.py` failed to import at all on Python 3.12+

It used the stdlib `asyncore`/`smtpd` modules, both removed by PEP 594 —
[upstream issue #522](https://github.com/CrimsonForge-io/king-phisher/issues/522), where the
maintainer confirmed the codebase is unmaintained and a from-scratch 2.0 is planned instead.
Rebuilt on `asyncio` via `aiosmtpd`, keeping the same public API, and verified end-to-end against a
real SMTP client on Python 3.14.

### Fixed: `sqlalchemy.Binary` (removed in SQLAlchemy 1.4+)

Broke importing the whole `king_phisher.server.database.models` module and a historical Alembic
migration. Swapped for `sqlalchemy.LargeBinary` — an identical column type, just renamed upstream —
in both places.

### Modernized: dependency floors

Added `requirements.txt` with the same roughly 40 packages upstream's `Pipfile` pins to exact 2019
releases, switched to `>=` floors so pip resolves current wheels. Verified on Python 3.14: every
package installs cleanly and all 29 `king_phisher.server` submodules, plus the rest of the shared
non-client code, import without error. One necessary cap: `setuptools<81`, because a transitive
dependency (`smoke-zephyr`) still imports the now-optional `pkg_resources` API — documented inline
in `requirements.txt`.

### Added `tools/devshell.sh`: automated venv lifecycle

Upstream has no venv story (`install.sh` is a single `sudo bash` system installer). This script
creates `.venv/` on first run, installs or updates `requirements.txt` into it, and only ever
activates the venv inside a subshell, so there's nothing to remember to deactivate — closing that
shell, the command it ran, or the terminal all end it automatically.

## Testing

This fork has no automated test suite of its own; the two fixes were verified directly:
`smtp_server.py` against a real SMTP client end-to-end, and `database.models` by confirming all 29
server submodules import cleanly on Python 3.14 after the dependency changes.

## Limitations

- The GTK client needs system GObject-introspection libraries that are outside pip's scope and
  weren't available to verify in the environment this fork was built in; that part of
  `INSTALL.md`/`tools/install.sh` is unchanged from upstream and untested by this fork.
- Campaign logic, templates, the web server for landing pages, and the rest of the server beyond
  the two fixes above are unchanged from upstream — including whatever else may not work on a
  Python this new, since upstream stopped testing against one.

## Responsible use

King Phisher sends real emails and serves real landing pages. Only run a campaign against an
organisation that has authorized the test, with scope agreed in advance.

## Credits

Built on [king-phisher](https://github.com/CrimsonForge-io/king-phisher) (formerly
`rsmusllp/king-phisher`), by SecureState and its contributors. The server, client, campaign logic
and templates are upstream's; the fixes above are this fork's.

## License

BSD-3-Clause, the same as upstream. See [LICENSE](LICENSE).
