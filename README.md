# FastAPI + Beanie(MongoDB) + Nginx Example

Features:
- FastAPI app using Beanie (MongoDB ODM)
- Pydantic v2 models using `Annotated` validation
- Async startup/shutdown using `asynccontextmanager` lifespan
- JWT authentication (python-jose)
- Full CRUD with soft delete (flag) and hard delete (superuser-only)
- Nginx as reverse proxy (Docker)
- Docker Compose for app + nginx

## Prerequisites
- Docker Desktop (Windows)
- docker-compose (bundled in Docker Desktop)
- Python 3.11 (only if running locally without Docker)

## Quick start with Docker (recommended)
1. Create `.env` and set `MONGODB_URI` or use local Mongo by leaving MONGODB_URI pointing to `mongodb://mongo:27017`.
2. From project root:
   ```bash
   docker-compose up --build
3. visit http://localhost -> proxied to FastAPI app.
4. FastAPI docs: http://localhost/docs


## Notes for Windows

Use Docker Desktop and ensure virtualization is enabled.

If using MongoDB Atlas, whitelist your Docker host IP (or 0.0.0.0/0 for dev).

To open logs: use Docker Desktop UI or docker-compose logs -f app.

## Development (without Docker)

1. Create virtualenv, install pip install -r requirements.txt.

2. Provide .env with MONGODB_URI and JWT_SECRET.
3. Run:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
4. If you want Nginx locally, run the nginx docker service from docker-compose and point it to your host app.


## Security & production

Use strong JWT secret, rotate keys, enable TLS (Let's Encrypt).

Limit CORS origins.

Use proper logging, request limits and monitoring.



---

# How it fits together / teaching tips
- `lifespan=lifespan` in `main.py` uses the `asynccontextmanager` defined in `db.py`. This is the modern, recommended approach and replaces FastAPI's deprecated `@app.on_event("startup")` patterns.
- `Beanie` uses Motor client under the hood. We call `init_beanie(...)` inside the lifespan so DB models are ready when the app starts.
- JWT `sub` payload stores the `user.id` (Beanie Document id). `get_current_user` decodes token and loads user.
- Soft delete: items have `deleted: bool`. List endpoints filter them out by default. Hard delete endpoint requires `require_superuser`.
- Nginx config proxies `/` to the `app` container. When you run Docker Compose, nginx resolves `app` to the fastapi service.

---

# Quick usage examples (curl)
Register:
```bash
curl -X POST http://localhost/auth/register -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"a@x.com","password":"supersecret"}'


** Get token: **
curl -X POST http://localhost/auth/token -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"supersecret"}'

** Create item (with token): **
curl -X POST http://localhost/items -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" -d '{"name":"thing","price":1.2}'
