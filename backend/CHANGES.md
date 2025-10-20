# Changelog

## Fixes

- nginx: Rewrite and proxy rules updated in `default.conf.template` to strip `/api/` prefix and forward API requests to the backend URL defined by `$BACKEND_URL`. This ensures the frontend proxies `/api/auth/login/` to `/auth/login/` on the backend and prevents NGINX from trying to serve API paths as static files.

- nginx: `proxy_set_header X-Forwarded-Proto` changed to use `$scheme` in backend/nginx.conf to allow Django to correctly detect the original request scheme behind Render's TLS termination.

- Added `scripts/check-deploy.sh` to validate deployed frontend/backend connectivity and the presence of static assets (like `vite.svg`).

- README updated with Render environment variable instructions.
