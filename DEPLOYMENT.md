# Free Managed Deployment

This guide deploys SettleSmart as three services:

- Neon: managed PostgreSQL
- Render: FastAPI, Alembic migrations, WebSockets, and temporary image files
- Vercel: React/Vite frontend and public portfolio URL

Deploy them in that order. The database URL is needed by Render, and the Render URL is needed by Vercel.

## 1. Database: Neon

1. Sign in to Neon and create a project named `settlesmart`.
2. Use the default Postgres database and select a region near the Render region you plan to use.
3. Open the project's **Connect** dialog.
4. Select the pooled connection option and copy the full connection string. It looks like:

   ```text
   postgresql://user:password@host-pooler.region.aws.neon.tech/database?sslmode=require
   ```

5. Keep this value private. It becomes Render's `DATABASE_URL`; never add it to a committed file.

No manual table creation is required. The Render start command runs `alembic upgrade head` before starting FastAPI, so the first successful backend deployment initializes the schema. Every later deployment applies any new migrations before the application starts.

## 2. Backend: Render

The repository includes `render.yaml`, so a Render Blueprint can read most settings automatically. For a manual Web Service, enter these exact values:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/moazaamir7/settlesmart` |
| Branch | `main` |
| Root Directory | `backend` |
| Runtime | Python 3 |
| Plan | Free |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Health Check Path | `/health` |

Add these environment variables:

| Variable | Value |
| --- | --- |
| `DATABASE_URL` | The complete private Neon connection string |
| `ENVIRONMENT` | `production` |
| `PYTHON_VERSION` | `3.12.8` |
| `FRONTEND_URL` | Initially the expected Vercel URL; replace it with the exact final URL after Vercel deploys |
| `BACKEND_CORS_ORIGINS` | `http://localhost:5173` |
| `ALLOWED_HOSTS` | `*.onrender.com` |
| `UPLOAD_DIR` | `uploads` |

Deploy the service and wait for `/health` to return a successful response. Copy the resulting origin, for example:

```text
https://settlesmart-api.onrender.com
```

Use only the origin: no trailing slash and no `/api/v1`. Render's free service sleeps after inactivity, so the first request after a quiet period can take about a minute. A new WebSocket connection wakes it automatically.

### Free Render Image Limitation

The free Render filesystem is ephemeral. Group images upload and display normally, but a restart, redeploy, or idle spin-down can erase them. Accounts, groups, expenses, messages, invites, and sessions remain durable because they are stored in Neon. Durable images would require object storage such as Cloudinary, Supabase Storage, or S3, or a paid Render disk.

## 3. Frontend: Vercel

Import the same GitHub repository into Vercel and enter:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/moazaamir7/settlesmart` |
| Root Directory | `frontend` |
| Framework Preset | Vite |
| Install Command | `npm ci` |
| Build Command | `npm run build` |
| Output Directory | `dist` |

Add this Production environment variable:

| Variable | Value |
| --- | --- |
| `VITE_API_URL` | The Render origin, such as `https://settlesmart-api.onrender.com` |

Deploy the frontend. `frontend/vercel.json` sends client-side routes such as `/login`, `/app`, and `/join/:token` to `index.html`, so refreshing those routes does not produce a Vercel 404.

Vite embeds `VITE_API_URL` during the build. If it changes, update the Vercel variable and redeploy the frontend.

## Final CORS Step

After Vercel provides the final production origin, such as `https://settlesmart.vercel.app`:

1. Return to the Render service's environment settings.
2. Set `FRONTEND_URL` to that exact origin with no trailing slash.
3. Save the change and let Render redeploy.
4. Confirm that signup, login, group creation, invite joining, messages, and image upload work from the Vercel URL.

REST requests are restricted by FastAPI CORS. WebSocket connections independently validate the browser `Origin` header against the same configured origins. Authentication uses bearer tokens rather than cross-site cookies, so no `SameSite` or cookie-domain exception is needed.

## Updating The Deployment

Both services can auto-deploy from `main` after GitHub receives a push. Database migrations remain part of Render startup. For frontend environment-variable changes, trigger a new Vercel deployment because Vite variables are build-time values.
