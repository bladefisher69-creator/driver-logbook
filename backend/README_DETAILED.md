Project status, configuration, detailed setup and troubleshooting

This project is in active local-first development. The README in the repository root covers the standard quick start and deployment paths. This file documents recent changes, full configuration, exact commands used during development, known issues you may encounter, and detailed fixes/workarounds for common problems.

Summary of recent work (what's implemented)
- Trip pickup/destination coordinate fields (backend fields: `pickup_lat`, `pickup_lng`, `destination_lat`, `destination_lng`).
- `LocationUpdate` model and POST endpoint to record live GPS updates for trips.
- Address autocomplete and reverse-geocoding proxy endpoints (Mapbox + Google Places support) to keep API keys server-side.
- Websocket consumer and Channels wiring to broadcast trip location updates to `trip_<id>` groups.
- Frontend: Map picker, fuzzy address search, TripRouteMap preview, Geolocation tracker and LiveMapView components.
- Simulator management command to generate location updates for testing arrival detection and websockets.
- Unit test for the trip location endpoint and a test-only Django settings module for in-memory tests.

Important environment variables (full list)

Backend (set in environment or `backend/.env`):
- `DEBUG` (True/False)
- `DJANGO_SECRET_KEY`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`
- `MAP_PROVIDER` — `mapbox` or `google`
- `MAPBOX_TOKEN` or `GOOGLE_PLACES_API_KEY` depending on provider
- `REDIS_URL` (default `redis://127.0.0.1:6379`)

Frontend (root `.env` or local env):
- `VITE_API_BASE_URL` (e.g. `http://localhost:8000/api`)
- `VITE_MAP_PROVIDER` (optional, mirrors backend provider for dev-time UI)

Full local (no-Docker) setup — exact commands (Windows PowerShell examples)

1) Backend setup and dependencies

```powershell
cd 'C:/Users/Valued Customer/Desktop/project/backend'
python -m venv venv
& 'C:/Users/Valued Customer/Desktop/project/backend/venv/Scripts/Activate.ps1'
pip install -r requirements.txt
# If channels packages are not present, install them too:
pip install channels channels_redis
```

2) Set environment variables (PowerShell temporary example)

```powershell
$env:DB_NAME='driver_logbook'
$env:DB_USER='logbook_user'
$env:DB_PASSWORD='logbook_password'
$env:DB_HOST='127.0.0.1'
$env:DB_PORT='3306'
$env:REDIS_URL='redis://127.0.0.1:6379'
$env:MAP_PROVIDER='google'
$env:GOOGLE_PLACES_API_KEY='YOUR_KEY_HERE'
```

3) Create DB objects (if using MySQL locally)

```sql
CREATE DATABASE driver_logbook;
CREATE USER 'logbook_user'@'localhost' IDENTIFIED BY 'logbook_password';
GRANT ALL PRIVILEGES ON driver_logbook.* TO 'logbook_user'@'localhost';
FLUSH PRIVILEGES;
```

4) Generate and apply Django migrations (this fixes the "Unknown column" errors)

```powershell
cd 'C:/Users/Valued Customer/Desktop/project/backend'
& 'C:/Users/Valued Customer/Desktop/project/backend/venv/Scripts/Activate.ps1'
python manage.py makemigrations logbook
python manage.py migrate
```

Notes: If you see errors like `Unknown column 'trips.pickup_lat'`, it means the model was changed but migrations were not applied. Running the commands above will create and apply migrations such as `logbook.0002_trip_coords` and `logbook.0003_locationupdate`.

5) Start Redis (for Channels) — Docker quick start

```powershell
docker run -d --name local-redis -p 6379:6379 redis:7
```

6) Run backend server

```powershell
python manage.py runserver 0.0.0.0:8000
```

7) Frontend

```powershell
cd 'C:/Users/Valued Customer/Desktop/project'
npm install
setx VITE_API_BASE_URL "http://localhost:8000/api"
npm run dev
```

Run tests (use in-memory DB to avoid MySQL test DB permission issues):

```powershell
cd 'C:/Users/Valued Customer/Desktop/project/backend'
& 'C:/Users/Valued Customer/Desktop/project/backend/venv/Scripts/Activate.ps1'
python manage.py test --settings=config.test_settings
```

Common problems and exact fixes

- Unknown column 'trips.pickup_lat' (MySQL 1054)
  - Cause: missing migrations
  - Fix: `python manage.py makemigrations logbook` → `python manage.py migrate`

- ModuleNotFoundError: No module named 'channels'
  - Cause: channels not installed in the active venv
  - Fix: `pip install channels channels_redis` and add them to `requirements.txt`

- Tests failing with Access denied for test DB (MySQL 1044)
  - Cause: DB user lacks permission to create/destroy test DBs
  - Fix: run tests with `--settings=config.test_settings` (uses in-memory SQLite) or give the DB user appropriate privileges

- Frontend shows 500 with unreadable body
  - Cause: server raised an exception; the frontend couldn't parse the response
  - Fix: run backend in foreground to capture traceback; the `DriverViewSet.me` now logs the traceback and returns structured JSON. Copy the traceback and paste it into the issue/PR for diagnosis.

- ESLint crashes on load (TypeError reading 'allowShortCircuit')
  - Cause: mismatched versions between TypeScript and `@typescript-eslint`
  - Fix (recommended): update the parser/plugin to a version compatible with your TypeScript (`npm install --save-dev @typescript-eslint/parser@^6 @typescript-eslint/eslint-plugin@^6 eslint@^8`) and then run `npm run lint -- --fix`.

Developer conveniences and recommended extras

- Add Husky + lint-staged hooks to run linting before commit. Note: your workspace must be a git repo for Husky hooks to be installed. Example:
  - `npx husky-init && npm install`
  - `npx husky set .husky/pre-commit "npm run lint -- --fix"`

- Create a small `scripts/bootstrap-dev.ps1` script to automate venv creation, pip/npm install, migrations, and optional Redis docker start. I can scaffold this for you if you want.

Next recommended steps (I can do these for you):
- Add Playwright E2E scaffolding and one test for login + live map tracking.
- Harden serializers against unexpected model property errors (add safe guards to properties that run DB queries) and add unit tests for serializing `Driver` resources.
- Finish re-enabling `@typescript-eslint` rule set and fix remaining TypeScript issues.

If you want me to make any of the above changes (bootstrap script, Playwright tests, Husky wiring, safe-guards), tell me which one to do first and I'll implement it and run quick verification locally.
