# Mini Dashboard

A small Django REST Framework + React mini-dashboard for client-filtered sales data and monthly goal editing.

## Backend

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r ..\requirements.txt
python manage.py migrate
python manage.py seed_demo_data
python manage.py runserver 127.0.0.1:8000
```

The backend loads the root `.env` automatically for local runs.

The protected endpoint is:

```text
GET/PATCH http://127.0.0.1:8000/api/dashboard/
Headers:
  X-API-Key: dev-dashboard-key
  X-Client-Id: 1
```

`GET` returns sales and target data for the client in `X-Client-Id`. `PATCH` accepts:

```json
{ "monthlyGoal": 12000 }
```

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

The React app reads these optional Vite environment variables:

```text
VITE_API_URL=/api/dashboard/
VITE_DASHBOARD_API_KEY=dev-dashboard-key
VITE_CLIENT_ID=1
```

Vite proxies `/api` to `http://127.0.0.1:8000` during local development.

## Docker Compose

Create a `.env` from `.env.example`, set real secrets, then run:

```powershell
docker compose --env-file .env up --build
```

The compose stack uses Postgres, runs Django migrations on backend startup, serves the React build through nginx, and proxies `/api` from the frontend container to the backend container. Open:

```text
http://127.0.0.1:3000
```

Demo clients and sales are seeded by default in Docker Compose so `VITE_CLIENT_ID=1`
has data immediately. Set `SEED_DEMO_DATA=0` if you want to disable demo seeding.

## Coolify

Use the repository `docker-compose.yml` as the Coolify compose file. Expose the `frontend` service on port `80`; keep `backend` and `db` internal. Configure these environment variables in Coolify:

```text
POSTGRES_DB
POSTGRES_USER
POSTGRES_PASSWORD
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
CSRF_TRUSTED_ORIGINS
CORS_ALLOWED_ORIGIN
DASHBOARD_API_KEY
VITE_API_URL
VITE_DASHBOARD_API_KEY
VITE_CLIENT_ID
FRONTEND_PORT
```

`DASHBOARD_API_KEY` and `VITE_DASHBOARD_API_KEY` must match for this demo header-protected API.

For `minidashboard-test.joween.dev`, use:

```text
DJANGO_ALLOWED_HOSTS=minidashboard-test.joween.dev
CSRF_TRUSTED_ORIGINS=https://minidashboard-test.joween.dev
CORS_ALLOWED_ORIGIN=https://minidashboard-test.joween.dev
VITE_API_URL=/api/dashboard/
```

Access the deployed system at:

```text
https://minidashboard-test.joween.dev
```

The compose file automatically appends `localhost`, `127.0.0.1`, and `backend`
to `DJANGO_ALLOWED_HOSTS` for internal container traffic.
