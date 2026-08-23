import ports
import worktrees
import runtime
import state
from config import load_config


def main():
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
    for service, command in config["commands"].items():
        process = runtime.start_project(
            command, allocated_ports[service], allocated_ports
        )
        processes[service] = process
        pids[service] = process.pid

    state.save_state(detected_worktree, allocated_ports, pids)
    runtime.wait_for_projects(processes)


if __name__ == "__main__":
    main()
