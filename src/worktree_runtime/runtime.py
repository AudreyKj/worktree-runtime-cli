import os
import re
import shlex
import signal
import subprocess
import time


def service_port_variable(service):
    normalized_service = re.sub(r"\W+", "_", service).upper()
    return f"{normalized_service}_PORT"


def start_project(command, port, allocated_ports):
    env = os.environ.copy()
    env["PORT"] = str(port)
    for service, allocated_port in allocated_ports.items():
        env[service_port_variable(service)] = str(allocated_port)

    process = subprocess.Popen(
        shlex.split(command),
        env=env,
        start_new_session=True,
    )

    return process


def stop_projects(processes):
    running_processes = [
        process for process in processes.values() if process.poll() is None
    ]
    for process in running_processes:
        os.killpg(process.pid, signal.SIGTERM)

    for process in running_processes:
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def wait_for_projects(processes):
    try:
        while True:
            for service, process in processes.items():
                return_code = process.poll()
                if return_code is not None:
                    raise RuntimeError(
                        f"Service '{service}' exited unexpectedly with code {return_code}."
                    )
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("\nStopping services...")
    finally:
        stop_projects(processes)
