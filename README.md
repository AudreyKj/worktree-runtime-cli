# Worktree runtime

`wt-runtime` assigns an available port to each configured service, starts each
service with its assigned `PORT` environment variable, and records the ports and process IDs in 
`.worktree-runtime-state.json`.

Create `.worktree-runtime.yml` in the root of each consumer project, adding relevant services:

```yaml
ports:
  frontend:
    start: 3000
    end: 3010
  backend:
    start: 4000
    end: 4010

commands:
  frontend: npm run dev
  backend: npm run api
```

The names under `ports` and `commands` must match exactly. Run `wt-runtime`
from the consumer project's worktree root. Each command runs as a separate
process and receives its own `PORT` value. Every command also receives named
port variables for all services, such as `FRONTEND_PORT` and `BACKEND_PORT`.

`wt-runtime` stays running while the services run. Press `Ctrl+C` to stop all
of the services it started.
