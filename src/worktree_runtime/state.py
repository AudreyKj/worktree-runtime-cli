import json
from pathlib import Path

STATE_FILE = Path(".worktree-runtime-state.json")


def load_state():
    if not STATE_FILE.exists():
        return {}

    with STATE_FILE.open("r") as file:
        return json.load(file)


def save_state(worktree, ports, pids):
    state = load_state()

    state[worktree] = {
        "ports": ports,
        "pids": pids,
    }

    with STATE_FILE.open("w") as file:
        json.dump(state, file, indent=2)
