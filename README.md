## This is a fork

Fork of [king-phisher](https://github.com/CrimsonForge-io/king-phisher) (formerly `rsmusllp/king-phisher`).
Upstream says right below that it's no longer maintained, and its own maintainer has confirmed on an open
bug report that a from-scratch King Phisher 2.0 is planned with none of this codebase carried over -- so
nothing here was going to get fixed upstream. This fork fixes what's actually broken on a current Python
without touching the campaign logic or the GTK client UI.

### This fork vs. upstream

| | Upstream `CrimsonForge-io/king-phisher` | This fork |
| --- | --- | --- |
| `smtp_server.py` on Python 3.12+ | Crashes on import (`asyncore`/`smtpd` removed by PEP 594) -- [issue #522](https://github.com/CrimsonForge-io/king-phisher/issues/522), confirmed abandoned by the maintainer | Rebuilt on `asyncio` via `aiosmtpd`, same public API, verified against a real SMTP client |
| `server.database.models` import | Crashes (`sqlalchemy.Binary` removed in SQLAlchemy 1.4+) | Fixed: swapped for `sqlalchemy.LargeBinary` (identical column type) |
| Dependency versions | `Pipfile` hard-pins ~40 packages to exact 2019 releases, no stated Python floor | `requirements.txt` with `>=` floors; verified every package installs and all 29 server submodules import cleanly on Python 3.14 |
| Dev environment | `install.sh` is a single `sudo bash` system-level installer, no venv story | `tools/devshell.sh`: creates/updates a `.venv`, activates it only inside a subshell -- nothing to manually deactivate |

### Fixed: `smtp_server.py` failed to import at all on Python 3.12+

It used the stdlib `asyncore`/`smtpd` modules, both removed by PEP 594 -- [upstream issue
#522](https://github.com/CrimsonForge-io/king-phisher/issues/522). Rebuilt on `asyncio` via `aiosmtpd`,
same public API, verified end-to-end against a real SMTP client on Python 3.14.

### Fixed: `sqlalchemy.Binary` (removed in SQLAlchemy 1.4+)

Broke importing the whole `king_phisher.server.database.models` module and a historical Alembic
migration. Swapped for `sqlalchemy.LargeBinary` (identical column type) in both places.

### Modernized: dependency floors

Added `requirements.txt` with the same ~40 packages upstream's `Pipfile` pins to exact 2019 versions,
switched to `>=` floors so pip resolves current wheels. Verified on Python 3.14: every package installs
cleanly and all 29 `king_phisher.server` submodules (plus the rest of the shared, non-client code) import
without error. One necessary cap: `setuptools<81`, because a transitive dependency (`smoke-zephyr`) still
imports the now-optional `pkg_resources` API -- documented inline in `requirements.txt`. The GTK client
itself needs system GObject-introspection libraries that are outside pip's scope and weren't available to
verify in the environment this fork was built in; that part of `INSTALL.md`/`tools/install.sh` is
unchanged.

### Added `tools/devshell.sh`: automated venv lifecycle

Upstream has no venv story at all (`install.sh` is a single `sudo bash` system installer). This script
creates `.venv/` on first run, installs/updates `requirements.txt` into it, and only ever activates the
venv inside a subshell -- so there's nothing to remember to deactivate; closing that shell, the tool it
ran, or the terminal all end it automatically. Usage: `tools/devshell.sh` for an interactive shell, or
`tools/devshell.sh <command>` to run one command and return.

---

![alt text](https://github.com/securestate/king-phisher/raw/master/data/king-phisher-logo.png "King Phisher")

# King Phisher [![Documentation Status][doc-status]][doc-link] [![GitHub Issues][issue-status]][issue-link] [![GitHub Downloads][downloads-status]][downloads-link] [![Slack Status][slack-status]][slack-link]
*Phishing Campaign Toolkit*

![alt text](https://raw.githubusercontent.com/securestate/king-phisher/screenshots/dashboard.png "Campaign Dashboard")

# King Phisher is no longer being maintained.

## Installation
For instructions on how to install, please see the
[INSTALL.md](https://github.com/securestate/king-phisher/blob/master/INSTALL.md)
file. After installing, for instructions on how to get started please see the
[wiki](https://github.com/securestate/king-phisher/wiki).

## Overview
King Phisher is a tool for testing and promoting user awareness by simulating
real world phishing attacks. It features an easy to use, yet very flexible
architecture allowing full control over both emails and server content.
King Phisher can be used to run campaigns ranging from simple awareness
training to more complicated scenarios in which user aware content is served
for harvesting credentials.

King Phisher is only to be used for legal applications when the explicit
permission of the targeted organization has been obtained.

Get the latest stable version from the
[GitHub Releases Page](https://github.com/securestate/king-phisher/releases) or
use git to checkout the project from source.

## Feature Overview
 * Run multiple phishing campaigns simultaneously
 * Send email with embedded images for a more legitimate appearance
 * Optional Two-Factor authentication
 * Credential harvesting from landing pages
 * SMS alerts regarding campaign status
 * Web page cloning capabilities
 * Integrated Sender Policy Framework (SPF) checks
 * Geo location of phishing visitors
 * Send email with calendar invitations

## Plugins
Both the client and server can be extended with functionality provided by
plugins. A small number of plugins are packaged with King Phisher and
additional ones are available in the [Plugins repository](https://github.com/securestate/king-phisher-plugins).

## Template Files
Template files for both messages and server pages can be found in the separate
King Phisher [Templates repository](https://github.com/securestate/king-phisher-templates).
Any contributions regarding templates should also be submitted via a pull
request to the templates repository.

## Documentation
Documentation for users of the application is provided on the project's
[wiki page](https://github.com/securestate/king-phisher/wiki). This includes
steps to help new users get started with their first campaigns. Additional
technical documentation intended for developers is kept separate as outlined
in section below.

### Code Documentation
King Phisher uses Sphinx for internal technical documentation. This
documentation can be generated from source with the command
```sphinx-build -b html docs/source docs/html```. The latest documentation is
kindly hosted on [ReadTheDocs](https://readthedocs.org/) at
[king-phisher.readthedocs.io][doc-link].

### Message Template Variables
The client message templates are formatted using the Jinja2 templating engine
and support a number of variables. These are included here as a reference, check
the templates [wiki page](https://github.com/securestate/king-phisher/wiki/Templates)
for comprehensive documentation.

Variable Name              | Variable Value
---------------------------|---------------
client.company\_name       | The target's company name
client.email\_address      | The target's email address
client.first\_name         | The target's first name
client.last\_name          | The target's last name
client.message\_id         | The unique tracking identifier (this is the same as uid)
sender.email               | The email address in the "Source Email (MIME)" field
sender.friendly\_alias     | The value of the "Friendly Alias" field
sender.reply\_to           | The value of the "Reply To" field
url.tracking\_dot          | URL of an image used for message tracking
url.webserver              | Phishing server URL with the uid parameter
url.webserver\_raw         | Phishing server URL without any parameters
tracking\_dot\_image\_tag  | The tracking image in a preformatted ```<img />``` tag
uid                        | The unique tracking identifier (this is the same as client.message_id)

The uid is the most important, and must be present in links that the messages
contain.

## License
King Phisher is released under the BSD 3-clause license, for more details see
the [LICENSE](https://github.com/securestate/king-phisher/blob/master/LICENSE) file.

## Credits
Special Thanks (QA / Beta Testing):

 - Jake Garlie - jagar
 - Jeremy Schoeneman - Shad0wman
 - Bryan Sfara
 - Ken Smith - p4tchw0rk
 - Brianna Whittaker

King Phisher Development Team:

 - Erik Daguerre - wolfthefallen ([@wolf_thefallen](https://twitter.com/wolf_thefallen))
 - Brandan Geise - coldfusion ([@coldfusion39](https://twitter.com/coldfusion39))
 - Jeff McCutchan - jamcut ([@jamcut](https://twitter.com/jamcut))
 - Spencer McIntyre - zeroSteiner ([@zeroSteiner](https://twitter.com/zeroSteiner))

[doc-link]: http://king-phisher.readthedocs.io/en/latest
[doc-status]: https://readthedocs.org/projects/king-phisher/badge/?version=latest
[downloads-link]: https://github.com/securestate/king-phisher/releases
[downloads-status]: https://img.shields.io/github/downloads/securestate/king-phisher/total.svg
[issue-link]: https://github.com/securestate/king-phisher/issues
[issue-status]: http://img.shields.io/github/issues/securestate/king-phisher.svg
[slack-link]: https://king-phisher-slackin.herokuapp.com/
[slack-status]: https://img.shields.io/badge/slack-join-brightgreen.svg
