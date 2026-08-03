# Docker Reference — AI Support System

All commands below are run from the **repo root** (`AI_Support_System/`), where your `.env` file lives.

## Day-to-day commands

**First run, or after changing a Dockerfile / `requirements.txt` / `package.json`:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml up --build
```

**Just resuming work, nothing changed in dependencies:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml up
```

**Fastest resume — containers already exist and are just stopped:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml start
```

**Stop everything (keeps containers/volumes, just stops them):**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml stop
```

**Tear down containers + network (keeps volumes, i.e. your Postgres data survives):**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml down
```

**Full nuke — also deletes volumes (your Postgres data is gone, only do this on purpose):**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml down -v
```

## Why `--env-file .env` every time

`docker-compose.yml` lives in `infra/`, but `.env` lives in the repo root. Compose only auto-loads a `.env` sitting *next to the compose file*, so without the flag, variables like `${POSTGRES_PASSWORD}` silently resolve to empty and Postgres refuses to start. The `--env-file .env` flag is what tells Compose "the file's actually here, one level up from the compose file."

## Avoiding the long command every time

Save this as `run.ps1` in the repo root:
```powershell
docker compose --env-file .env -f infra/docker-compose.yml up --build
```
Then just run `.\run.ps1`. (Don't commit build/rebuild logic differences into this script without a comment — future you will forget which script does what.)

## Logs & debugging

**Tail logs for everything:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml logs -f
```

**Just one service:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml logs -f backend
```

**Get a shell inside a running container:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml exec backend bash
docker compose --env-file .env -f infra/docker-compose.yml exec frontend sh
```

**Run a one-off command without starting a shell** (e.g. force-reinstall Node deps inside the container):
```powershell
docker compose --env-file .env -f infra/docker-compose.yml exec frontend npm ci
```

**Check Postgres is actually healthy from inside its own container:**
```powershell
docker compose --env-file .env -f infra/docker-compose.yml exec db pg_isready -U postgres
```

## Rebuilding a single service (not the whole stack)

```powershell
docker compose --env-file .env -f infra/docker-compose.yml up --build backend
```

## Common gotchas hit so far (keep this list growing)

| Symptom | Cause | Fix |
|---|---|---|
| `couldn't find env file` | Wrong relative path to `.env` | Path is relative to where you *run* the command, not where compose.yml lives |
| Postgres exits immediately, "must specify POSTGRES_PASSWORD" | `.env` not being read for variable substitution | Use `--env-file .env` flag |
| Frontend: `Cannot find native binding` (rolldown/Vite) | Host's `node_modules` (installed on Windows) overwrote the Linux-built one via the bind mount | Add `- /app/node_modules` as an anonymous volume under `frontend` in `docker-compose.yml` |
| Browser: `ERR_EMPTY_RESPONSE` on `localhost:5173`, log says "use --host to expose" | Vite binds to `localhost` inside the container by default, invisible from the host despite port mapping | `CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]` in `frontend/Dockerfile` |
| `uvicorn` crashes on startup, `ModuleNotFoundError` | Used dotted syntax instead of `module:attribute` | `CMD ["uvicorn", "app.main:app", ...]` — note the colon, not a dot |

## Ports reference

| Service | Container port | Host port |
|---|---|---|
| backend (FastAPI) | 8000 | 8000 → http://localhost:8000 |
| frontend (Vite) | 5173 | 5173 → http://localhost:5173 |
| db (Postgres) | 5432 | 5432 |
| redis | 6379 | 6379 |