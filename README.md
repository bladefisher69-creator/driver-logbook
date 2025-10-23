# Driver Logbook Management System

A comprehensive digital logbook solution for transport drivers and fleet managers, built with Django REST Framework, React, and MySQL.

> Developer note: expanded developer setup, troubleshooting, and recent change log are in `README_DETAILED.md` — see that file for step-by-step PowerShell commands, troubleshooting fixes, and advanced setup.

## Features

### Driver Features
- **Trip Logging**: Record trips with origin, destination, distance, and timing
- **Fuel Management**: Log refueling events with automatic reminders every 1,000 miles
- **Compliance Tracking**: Automatic calculation of work hours with 70-hour/8-day limit
- **Real-time Dashboard**: View current compliance status and remaining hours
- **Trip History**: Complete history of all trips with status tracking

### Admin Features
- **Fleet Overview**: Monitor all drivers and active trips
- **Compliance Reports**: Generate compliance reports for any date range
- **Driver Management**: View all drivers and their compliance status
- **Analytics Dashboard**: Real-time statistics on fleet operations

### Compliance Rules
- **70-hour limit** within any 8-day period
- **Mandatory refueling** every 1,000 miles
- **1-hour pickup time** (default)
- **1-hour drop-off time** (default)

## Tech Stack

### Backend
- Django 5.0
- Django REST Framework
- MySQL 8.0
- JWT Authentication
- Swagger/ReDoc API Documentation

### Frontend
- React 18
- TypeScript
- Tailwind CSS
- Lucide React Icons
- Vite

### Deployment
- Docker & Docker Compose
- Nginx

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd driver-logbook
```

### 2. Environment Setup

Copy the example environment files:

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

Edit `.env` files with your configuration (optional for local development).

### 3. Start with Docker Compose

```bash
docker-compose up --build
```

This will:
- Start MySQL database on port 3306
- Start Django backend on port 8000
- Start React frontend on port 80

### 4. Run Database Migrations

In a new terminal:

```bash
docker-compose exec backend python manage.py migrate
```

### 5. Create Sample Data (Optional)

```bash
docker-compose exec backend python manage.py seed_data
```

This creates:
- Admin user: `admin` / `admin123`
- Sample drivers: `john_doe`, `jane_smith`, `mike_wilson` / `driver123`
- Sample trips and fuel logs

### 6. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin
- **Swagger Docs**: http://localhost:8000/swagger
- **ReDoc Docs**: http://localhost:8000/redoc

## Manual Setup (Without Docker)

### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MySQL database:
```bash
mysql -u root -p
CREATE DATABASE driver_logbook;
CREATE USER 'logbook_user'@'localhost' IDENTIFIED BY 'logbook_password';
GRANT ALL PRIVILEGES ON driver_logbook.* TO 'logbook_user'@'localhost';
FLUSH PRIVILEGES;
exit;
```

4. Update `backend/.env` with your database credentials

5. Run migrations:
```bash
python manage.py migrate
```

6. Create superuser:
```bash
python manage.py createsuperuser
```

7. Seed sample data (optional):
```bash
python manage.py seed_data
```

8. Start the backend server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install dependencies:
```bash
npm install
```

2. Update `.env` with backend URL:
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

3. Start the development server:
```bash
npm run dev
```

4. Access at http://localhost:5173

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new driver
- `POST /api/auth/login/` - Login (get JWT tokens)
- `POST /api/auth/refresh/` - Refresh access token

### Drivers
- `GET /api/drivers/` - List all drivers (admin only)
- `GET /api/drivers/me/` - Get current driver profile
- `PUT /api/drivers/update_profile/` - Update profile
- `GET /api/drivers/{id}/compliance_status/` - Get compliance status

### Trips
- `GET /api/trips/` - List trips
- `POST /api/trips/` - Create new trip
- `GET /api/trips/{id}/` - Get trip details
- `POST /api/trips/{id}/complete/` - Complete a trip
- `POST /api/trips/{id}/cancel/` - Cancel a trip
- `GET /api/trips/active/` - Get active trips

### Fuel Logs
- `GET /api/fuel-logs/` - List fuel logs
- `POST /api/fuel-logs/` - Create fuel log
- `GET /api/fuel-logs/{id}/` - Get fuel log details

### Compliance Reports
- `GET /api/compliance-reports/` - List reports
- `POST /api/compliance-reports/generate/` - Generate new report

### Admin Dashboard
- `GET /api/dashboard/stats/` - Get dashboard statistics (admin only)

## Project Structure

```
driver-logbook/
├── backend/                    # Django backend
│   ├── config/                 # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── logbook/                # Main app
│   │   ├── models.py           # Database models
│   │   ├── serializers.py      # API serializers
│   │   ├── views.py            # API views
│   │   ├── urls.py             # URL routing
│   │   ├── admin.py            # Admin configuration
│   │   └── management/         # Management commands
│   ├── requirements.txt
│   └── Dockerfile
├── src/                        # React frontend
│   ├── api/                    # API client
│   ├── components/             # React components
│   │   ├── auth/               # Authentication
│   │   ├── dashboard/          # Dashboard views
│   │   ├── trips/              # Trip management
│   │   ├── fuel/               # Fuel logging
│   │   └── admin/              # Admin views
│   ├── context/                # React context
│   ├── types/                  # TypeScript types
│   └── App.tsx                 # Main app component
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
└── README.md
```

## Compliance Flow Examples

### Example 1: Hour Limit Warning
If a driver has logged 69 hours in the past 8 days and attempts to log a trip that would exceed 70 hours:
- System shows warning: "Driver near 70-hour limit"
- Trip is prevented if it would exceed the limit
- Driver must wait until the oldest hours roll off the 8-day window

### Example 2: Refueling Requirement
If a driver has driven 1,050 miles since last refuel:
- System prevents starting new trips
- Warning displayed: "Refueling required before next trip"
- Driver must log a fuel entry before continuing

## Development

### Run Tests
```bash
cd backend
python manage.py test
```

### Code Quality
```bash
# Backend
cd backend
flake8 .
black .

# Frontend
npm run lint
npm run typecheck
```

### Build for Production
```bash
# Build frontend
npm run build

# Collect static files (Django)
cd backend
python manage.py collectstatic
```

## Deployment

### Production Checklist
1. Set `DEBUG=False` in backend/.env
2. Generate secure `DJANGO_SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Update `CORS_ALLOWED_ORIGINS` with your frontend URL
5. Set strong database passwords
6. Configure proper backup strategy for MySQL
7. Set up SSL/TLS certificates
8. Configure production WSGI server (Gunicorn)

### Environment Variables

**Backend:**
- `DEBUG` - Debug mode (False in production)
- `DJANGO_SECRET_KEY` - Django secret key
- `DB_NAME` - Database name
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `ALLOWED_HOSTS` - Allowed hosts (comma-separated)
- `CORS_ALLOWED_ORIGINS` - CORS origins (comma-separated)

**Frontend:**
- `VITE_API_BASE_URL` - Backend API URL

## Troubleshooting

### Database Connection Issues
- Ensure MySQL is running: `docker-compose ps`
- Check database credentials in `.env`
- Wait for database health check to pass

### CORS Errors
- Verify `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check that backend is accessible from frontend

### Migration Issues
```bash
docker-compose exec backend python manage.py migrate --fake
docker-compose exec backend python manage.py migrate
```

## License

MIT License

## Support

For issues and questions, please open an issue on GitHub.

## Deployment notes for Render (frontend)

If you deploy the frontend on Render and the backend on a separate Render service, set the following environment variables for the frontend service:

- BACKEND_URL = https://driver-logbook.onrender.com/
- BACKEND_HOST = driver-logbook.onrender.com

The Dockerfile copies `default.conf.template` into the image and nginx will substitute these environment variables at runtime to proxy API requests to the backend. The template strips the `/api/` prefix so frontend requests to `/api/auth/...` are forwarded as `/auth/...` to the backend.

After deploying, run `scripts/check-deploy.sh` (or the curl commands listed below) to validate the setup.

Note for Windows PowerShell users: PowerShell defines `curl` as an alias for `Invoke-WebRequest`, which can behave differently.
If you paste bash-style curl commands into PowerShell, explicitly call `curl.exe` or use `Invoke-WebRequest`.
Example PowerShell-friendly forms:

```powershell
# Use the real curl executable when available
curl.exe -I "https://driver-logbook.onrender.com/vite.svg"

# Or use PowerShell's Invoke-WebRequest
Invoke-WebRequest -Uri "https://driver-logbook.onrender.com/vite.svg" -Method Head
```
