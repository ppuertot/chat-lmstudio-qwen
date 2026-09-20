# AGENTS.md

Flask web chat UI wrapping LM Studio's OpenAI-compatible API. Single fixed model `deepseek/deepseek-r1-0528-qwen3-8b`; no model selector. Comments and UI text are in Spanish — keep changes consistent.

## Run

- Local: `pip install -r requirements.txt && python app.py` → http://localhost:5000.
- Docker: `./docker/scripts.sh up` (or `docker compose -f docker/docker-compose.yml up -d --build`). Other commands: `down`, `restart`, `logs [N|follow]`, `status`, `shell`.
- Runtime prerequisite: LM Studio must be running a Local Server on `localhost:1234` with `deepseek/deepseek-r1-0528-qwen3-8b` loaded, or `/chat` returns a connection error / 404.
- Tests, linters, typecheck, and CI do not exist in this repo. There is no test command to run.

## Layout

- `app.py` — all backend logic. Module-level `LM_STUDIO_URL` (app.py:11) and `DEFAULT_MODEL_NAME` (app.py:14). Routes: `GET /` renders `templates/index.html`; `POST /chat` takes `{message}` and returns `{success, reply, timestamp}`.
- `templates/index.html` — frontend; posts to `/chat` (index.html:410). `static/` is empty.
- Docker build context is the repo root (`context: ..` in `docker/docker-compose.yml`), even though compose/Dockerfile live in `docker/`. Dockerfile copies `requirements.txt`, `app.py`, `templates/` into `/app`.

## Gotchas

- The `LM_STUDIO_URL` env var set in `docker/docker-compose.yml` is never read — `app.py` hardcodes the URL. Changing the env var has no effect.
- `app.py` extracts only `message.content` and ignores `reasoning_content`, so reasoning output is never shown. Keep this if you change models.
- R1 reasoning still consumes the `max_tokens` budget (`MAX_TOKENS`, app.py:18). Keep it generous (currently 4096) or visible replies get truncated even though the model finished thinking.
- `requirements.txt` lists `python-socketio` and `eventlet`, but the app is plain Flask with the dev server (no Socket.IO/eventlet usage). Don't assume async patterns.
- `network_mode: host` is required so the container can reach LM Studio on host `localhost:1234`; `EXPOSE 5000` is cosmetic under host networking.
- `docker/docker-compose.yml` has a commented `volumes:` mount for live `app.py` editing during development.
- README's project tree is stale (lists `.dockerignore` under `docker/`; actual file is at repo root).
