# ELD Feature — design, runbook, and assumptions (M1)

Status
------
M1 implemented: route proxy + frontend preview (spike).

Overview
--------
This document tracks the ELD + routing feature. M1 implements a backend proxy to OpenRouteService and a frontend map preview component. Subsequent milestones will add the rules engine and ELD SVG/PDF rendering.

How to test M1
--------------
1. Set `OPENROUTESERVICE_API_KEY` in `.env` if you want live routing. If not set, the endpoint will return 502 when proxying to ORS.
2. Backend:
   - python -m venv venv
   - venv\Scripts\activate
   - pip install -r requirements.txt
   - python manage.py migrate
   - python manage.py seed_data
   - python manage.py runserver
3. Frontend:
   - npm install
   - npm run dev
4. In the UI, create a Trip and click "Show Route" to preview the route on the map.

Notes & Next steps
-------------------
- M2: Implement `ELDGenerator` to produce daily logs and a /api/eld/generate/ endpoint (currently a stub).
- M3: Implement frontend `ELDLogSheet` component to render SVG and add export options.
- M4: Add tests, CI checks, and polish.

Assumptions
-----------
- Default units: miles/gallons (documented). Times stored in UTC.
- Use OpenRouteService as the default routing provider (swap-able provider abstraction planned).
