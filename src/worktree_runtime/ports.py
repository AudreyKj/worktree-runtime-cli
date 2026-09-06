import socket

allocated_ports = {}
claimed_ports = set()


def is_port_available(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", port)) != 0


def allocate_port(worktree, service, start_port, end_port):
    # 1. Check whether this worktree/service already has a port
    key = (worktree, service)

    if key in allocated_ports:
        return allocated_ports[key]

    # 2. Find an available port
    for port in range(start_port, end_port + 1):
        if port not in claimed_ports and is_port_available(port):
            allocated_ports[key] = port
            claimed_ports.add(port)
            return port

    raise RuntimeError(
        f"No available ports for {service} "
        f"between {start_port} and {end_port}"
    )
