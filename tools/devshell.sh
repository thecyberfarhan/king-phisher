#!/bin/bash
#
#  tools/devshell.sh
#
#  Automates the venv lifecycle for working on King Phisher: creates the
#  virtualenv on first run, installs/updates dependencies into it, then
#  drops you into (or runs a command in) a SUBSHELL with it activated.
#
#  Because the venv is only ever activated inside a child subshell, there is
#  nothing to remember to undo: closing that shell, exiting the tool it ran,
#  or closing the terminal window all end the subshell, which drops the
#  activation with it. Nothing is left active in your normal shell.
#
#  Usage:
#    tools/devshell.sh                 # open an interactive subshell with the venv active
#    tools/devshell.sh <command...>    # run one command in the venv, then return
#
#  Env:
#    KING_PHISHER_VENV   override the venv location (default: <repo>/.venv)
#
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
venv_dir="${KING_PHISHER_VENV:-$repo_dir/.venv}"
requirements="$repo_dir/requirements.txt"

if [ ! -d "$venv_dir" ]; then
	echo "[devshell] creating virtualenv at $venv_dir"
	python3 -m venv "$venv_dir"
	"$venv_dir/bin/pip" install -q --upgrade pip
fi

stamp="$venv_dir/.requirements.stamp"
if [ ! -f "$stamp" ] || [ "$requirements" -nt "$stamp" ]; then
	echo "[devshell] installing/updating dependencies"
	"$venv_dir/bin/pip" install -q -r "$requirements"
	touch "$stamp"
fi

if [ "$#" -gt 0 ]; then
	exec bash -c 'source "$1/bin/activate" && shift && exec "$@"' _ "$venv_dir" "$@"
else
	echo "[devshell] venv active in this subshell only -- type 'exit' when done, nothing to deactivate"
	exec bash --init-file <(echo "source '$venv_dir/bin/activate'; PS1='(king-phisher-venv) '\$PS1")
fi
