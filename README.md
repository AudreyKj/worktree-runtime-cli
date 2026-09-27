# Worktree Runtime

Running multiple Git worktrees locally often creates port conflicts.

`wt-runtime` solves that problem by dynamically finding a free port for each service in a worktree and starting the services, keeping them running until you stop them.

## Contents

- [Install](#install)
- [Configure a consumer project](#configure-a-consumer-project)
- [Run](#run)
- [Environment variables](#environment-variables)
- [Using it with agents and worktrees](#using-it-with-agents-and-worktrees)
- [Requirements and current behavior](#requirements-and-current-behavior)

## Install

Until the first PyPI release is published, install the CLI directly from
GitHub with `uv`:

```sh
uv tool install git+https://github.com/AudreyKj/worktree-runtime-cli.git
```

Or with `pipx`:

```sh
pipx install git+https://github.com/AudreyKj/worktree-runtime-cli.git
```

After the first PyPI release, the shorter published-package command will be:

```sh
uv tool install worktree-port-allocation-cli
```

Publication is tracked in
[GitHub issue #1](https://github.com/AudreyKj/worktree-runtime-cli/issues/1).

Install from a local checkout while developing it:

```sh
uv tool install --force --editable /path/to/worktree-runtime-cli
```

The command is then available as:

```sh
wt-runtime
```

`--editable` means changes to the local CLI source are used without another
installation step.

Check the installed version with:

```sh
wt-runtime --version
```

## Configure a consumer project

Create a `.worktree-runtime.yml` file at the root of the consumer project and
commit it. Git worktrees only contain tracked files, so an untracked config file
will not appear in newly created worktrees.

```yaml
ports:
  frontend:
    start: 5000
    end: 5010
  backend:
    start: 8080
    end: 8090

commands:
  frontend: "npm run dev-client"
  backend: "npm run dev-server"
```

The service names under `ports` and `commands` must match exactly. A project
with only one service needs only one entry:

```yaml
ports:
  backend:
    start: 8080
    end: 8090

commands:
  backend: "npm run dev-server"
```

Add this generated file to the consumer project's `.gitignore`:

```gitignore
.worktree-runtime-state.json
```

## Run

From the consumer project's worktree root, run:

```sh
wt-runtime
```

Example output:

```text
Allocated ports: {'frontend': 5001, 'backend': 8081}
```

The command remains in the foreground while the services run. Press `Ctrl+C`
to stop every service started by that invocation. Allocation details and process
IDs are recorded in `.worktree-runtime-state.json` for reference.

## Environment variables

Every started command receives two kinds of port variables:

- `PORT` is that command's own listening port.
- `<SERVICE>_PORT` describes each configured service's allocated port.

With the example configuration above, both child processes receive:

```text
FRONTEND_PORT=5001
BACKEND_PORT=8081
```

The frontend command additionally receives `PORT=5001`; the backend command
receives `PORT=8081`. These variables exist only in processes launched by
`wt-runtime`; they do not alter your shell session or `.env` files.

This lets a frontend listen on its own port and proxy API requests to the
allocated backend port. For example, a Vite configuration can use:

```ts
server: {
  port: Number(process.env.PORT) || 5000,
  proxy: {
    "/api": {
      target: `http://localhost:${process.env.BACKEND_PORT || 8080}`,
    },
  },
}
```

## Using it with agents and worktrees

Give each agent a separate worktree and branch, then run `wt-runtime` in each
worktree. Each invocation selects free ports, so the services can run together
without sharing frontend or backend ports.

```sh
git worktree add ../my-project-agent-a -b agent/a
git worktree add ../my-project-agent-b -b agent/b
```

Each worktree needs the committed `.worktree-runtime.yml` file.

### Use with Codex / Claude

Add the following instructions in instruction files (`AGENTS.md` or `CLAUDE.md`) at the root
of a consumer project. Codex and Claude Code read these files to learn the
project's local workflow.

In Claude Code, create or switch to an isolated worktree with the `/worktree`
command, then run `wt-runtime` from that worktree's root.

```md
# Worktree setup

When creating a new Git worktree for a task:

1. Run `npm ci` from the worktree root.
2. Copy the root checkout's local `.env` file into the worktree as `.env` if
   it exists.
3. Run `wt-runtime` from the worktree root and leave it running.
4. Report the allocated frontend and backend ports to the user.
5. If startup fails, diagnose and report the blocker before continuing task
   work.
```

For a new task, ask the agent to create a uniquely named branch and worktree,
then follow the project instructions before making changes.

## Requirements and current behavior

- Python 3.11 or newer.
- A Git worktree or repository; the CLI uses Git to identify the worktree.
- Commands are started separately and receive the configured environment
  variables.
- Service names may contain letters, numbers, underscores, and hyphens.
- Port availability is checked before a service starts. A concurrently launched
  process outside `wt-runtime` can still claim a port in the short interval
  before the service binds it.
