# AGENTS.md

Flask web chat UI wrapping LM Studio's OpenAI-compatible API. Model, LM Studio URL, and system prompt are env-configurable; defaults live in `app.py`. No model selector. Comments and UI text are in Spanish — keep changes consistent.

## Run

- Local: `pip install -r requirements.txt && python app.py` → http://localhost:5000.
- Docker: `./docker/scripts.sh up` (or `docker compose -f docker/docker-compose.yml up -d --build`). Other commands: `down`, `restart`, `logs [N|follow]`, `status`, `shell`.
- Runtime prerequisite: LM Studio must be running a Local Server with the configured model loaded, or `/chat` returns a connection error / 404.
- Tests, linters, typecheck, and CI do not exist in this repo. There is no test command to run.

## Configuration (env vars)

- `LM_STUDIO_URL` — default `http://localhost:1234/v1/chat/completions`.
- `LM_STUDIO_MODEL` — default `openai/gpt-oss-20b`.
- `SYSTEM_PROMPT` — default `Responde siempre en español.`; sent as the first `system` message. Set it to change language/tone.
- `TEMPERATURE` — default `0.7`; model-dependent (gpt-oss prefers ~1.0).
- `MAX_TOKENS` — default `8192`; raise for reasoning models (cannot exceed the model's loaded context in LM Studio).
- `LOAD_RETRY_SECONDS` — default `300`; how long `_stream_response` retries while LM Studio JIT-loads the model.
- `docker/docker-compose.yml` passes these; `app.py` reads them at import time.

## Layout

- `app.py` — all backend logic. Config constants at app.py:13-43 (`LM_STUDIO_URL`, `MODEL_NAME`, `SYSTEM_PROMPT`, `TEMPERATURE`, `MAX_TOKENS`, `LOAD_RETRY_SECONDS`). Routes: `GET /` renders `templates/index.html` passing `model`; `POST /chat` takes `{message}` and returns an SSE stream (`text/event-stream`), not JSON. Events: `data: {"delta": "..."}` per token, `data: {"status": "loading"|"ready"}` around JIT loading, terminal `data: [DONE]`; failures arrive as `data: {"error": "..."}` mid-stream, so HTTP status is 200 even on LM Studio errors. Empty message returns a 400 JSON error before streaming starts.
- `templates/index.html` — frontend; posts to `/chat` and incrementally renders `delta` chunks via `response.body.getReader()` (index.html:462). Markdown is rendered client-side with vendored `marked` + `DOMPurify` (throttled with `requestAnimationFrame`). Layout: title header on top, chat in the middle, connection status bar at the bottom (no sidebar).
- `static/` — vendored `marked.min.js` and `purify.min.js` (offline, no CDN). Loaded via `url_for('static', ...)`.
- Docker build context is the repo root (`context: ..` in `docker/docker-compose.yml`), even though compose/Dockerfile live in `docker/`. Dockerfile copies `requirements.txt`, `app.py`, `templates/`, `static/` into `/app`.

## Gotchas

- `app.py` extracts only `delta.content` (streaming) and ignores `reasoning_content`, so reasoning output is never shown. Keep this if you change models.
- R1 reasoning still consumes the `max_tokens` budget (`MAX_TOKENS`, app.py:38). Keep it generous (currently 8192) or the model can finish with `finish_reason: length` and zero `content`; `_stream_response` then emits an error instead of an empty reply.
- LM Studio JIT loading can return HTTP 400 `Failed to load model` while the model loads. `_stream_response` retries up to `LOAD_RETRY_SECONDS` and emits `status: loading`; don't treat every 400 as fatal.
- Stream lines are decoded as UTF-8 explicitly; `iter_lines(decode_unicode=True)` corrupts accents because LM Studio may not advertise a charset (requests then assumes ISO-8859-1). Don't "simplify" it back.
- `requirements.txt` lists `python-socketio` and `eventlet`, but the app is plain Flask with the dev server (no Socket.IO/eventlet usage). Don't assume async patterns.
- `network_mode: host` is required so the container can reach LM Studio on host `localhost:1234`; `EXPOSE 5000` is cosmetic under host networking.
- `docker/docker-compose.yml` has a commented `volumes:` mount for live `app.py` editing during development.
- README's project tree is stale (lists `.dockerignore` under `docker/`; actual file is at repo root).
