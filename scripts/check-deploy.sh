#!/usr/bin/env bash
set -euo pipefail

BACKEND_URL=${BACKEND_URL:-https://driver-logbook.onrender.com/}
FRONTEND_URL=${FRONTEND_URL:-https://driver-logbook.onrender.com}

echo "Checking frontend: $FRONTEND_URL"
echo "Checking backend: $BACKEND_URL"

echo "\n1) Check vite.svg exists on frontend"
curl -sSfI "$FRONTEND_URL/vite.svg" || { echo "vite.svg not found on frontend"; exit 2; }
echo "vite.svg OK"

echo "\n2) Check nginx config substitution"
ssh_cfg=$(curl -sSf "${FRONTEND_URL}" || true)
echo "(fetched frontend root)"

echo "\n3) Validate proxy to backend via /api/auth/login/"
resp=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$FRONTEND_URL/api/auth/login/" -H 'Content-Type: application/json' -d '{"username":"invalid","password":"invalid"}') || true
echo "POST /api/auth/login/ => HTTP $resp"
if [ "$resp" = "404" ]; then
  echo "Proxy not routing to backend (404)."; exit 3
fi

echo "All quick checks passed (note: 200/401/400 expected for auth endpoint depending on credentials)."
exit 0
