# SettleSmart

SettleSmart is a full-stack group expense application. Admins create groups, invite temporary members, record shared expenses, and calculate an optimized set of settlement payments. Members get a simpler balance and messaging view without creating an account.

## Highlights

- Email and password admin authentication with PBKDF2 password hashing
- Expiring, database-backed admin and guest sessions
- Role-based authorization for group data and actions
- Shareable invite links with temporary member access
- Equal expense splitting with tax, tip, fees, and discounts
- Optimized debt settlement calculation
- Real-time group chat over authenticated WebSockets
- Persistent, validated group image uploads
- CAD and USD currency enforcement
- PostgreSQL persistence and Alembic migrations
- Responsive React interface and public landing page
- Docker development and production configurations

## Stack

- React, TypeScript, and Vite
- FastAPI, SQLAlchemy, and Pydantic
- PostgreSQL 16
- Alembic migrations
- Nginx production frontend and reverse proxy
- Pytest

## Local Development

Docker Desktop is required.

```bash
docker compose up --build
```

- Website: `http://localhost:5173`
- API documentation: `http://localhost:8000/docs`

No account is seeded. Open the website, choose **Log in**, and create the first admin account through the signup form.

Local PostgreSQL data and uploaded images are stored in named Docker volumes. `docker compose down` stops the application without deleting them. Do not run `docker compose down --volumes` unless you intend to erase local data.

## Tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest
```

Build the frontend separately with:

```bash
cd frontend
npm ci
npm run build
```

## Production Deployment

The production Compose configuration serves the compiled frontend through Nginx, proxies API and WebSocket traffic to FastAPI, keeps PostgreSQL private, runs migrations during backend startup, and persists database and upload data in named volumes.

1. Copy the production environment template.

```bash
cp .env.production.example .env.production
```

2. Set a long URL-safe database password, final HTTPS origin, and accepted hostname in `.env.production`.

3. Start the production stack.

```bash
docker compose --env-file .env.production -f docker-compose.prod.yml up --build -d
```

4. Put the service behind HTTPS using your hosting platform or an external TLS reverse proxy. The Compose service listens on host port `8080` by default.

5. Visit `/login` and create the first real admin account.

### Required Environment Values

- `POSTGRES_PASSWORD`: long URL-safe password used only by PostgreSQL
- `PUBLIC_ORIGIN`: final origin such as `https://expenses.example.com`
- `ALLOWED_HOSTS`: accepted API hostname, or comma-separated hostnames
- `APP_PORT`: optional host port; defaults to `8080`

Production API documentation is disabled. Uploaded images are limited to JPG, PNG, or WebP files up to 5 MB.

## Persistence and Backups

Back up both production volumes:

- PostgreSQL data contains accounts, sessions, groups, messages, and expenses.
- Upload data contains group images.

For a serious public deployment, use an automated PostgreSQL backup schedule and volume snapshots. Test restoring those backups before relying on them.

## Architecture Notes

Admin and guest access tokens are random server-side sessions stored in PostgreSQL. Guest sessions are scoped to one group and become invalid when a member is removed or the group is deleted. All group reads, expense data, settlements, messages, uploads, and WebSocket connections require an authorized session.

The current real-time connection manager is designed for one backend process. If the application is later scaled to multiple backend instances, add Redis pub/sub so messages can be broadcast across instances.
