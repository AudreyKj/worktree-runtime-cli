import argparse

from . import ports, runtime, state, worktrees
from . import __version__
from .config import load_config


def create_parser():
    parser = argparse.ArgumentParser(
        prog="wt-runtime",
        description="Allocate ports and run services for the current Git worktree.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def run():
    config = load_config()
    detected_worktree = worktrees.detect_current_worktree()
    allocated_ports = {}
    pids = {}

    for service, port_config in config["ports"].items():
        allocated_port = ports.allocate_port(
            detected_worktree,
            service,
            port_config["start"],
            port_config["end"],
        )
        allocated_ports[service] = allocated_port

    print(f"Allocated ports: {allocated_ports}")

    processes = {}
    try:
        for service, command in config["commands"].items():
            process = runtime.start_project(
                command, allocated_ports[service], allocated_ports
            )
            processes[service] = process
            pids[service] = process.pid

        state.save_state(detected_worktree, allocated_ports, pids)
        runtime.wait_for_projects(processes)
    finally:
        runtime.stop_projects(processes)


def main():
    parser = create_parser()
    parser.parse_args()
    run()


if __name__ == "__main__":
    main()
