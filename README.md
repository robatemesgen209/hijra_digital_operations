# Hijra Bank Digital Operations Management System
**Django portfolio prototype** — an independent demonstration project inspired by digital-banking operations workflows. It is not an official Hijra Bank application and contains no real customer, account, transaction, or bank-system data.

## Features
- Dashboard with device and incident KPIs and a device-status chart
- Digital device/ATM register, search, filter, and edit
- Incident lifecycle with priorities, assignment, resolution details, and automatically generated incident IDs
- SLA target evaluation by incident type
- Preventive/corrective maintenance scheduling
- CSV incident report export
- Django admin interface and audit log records
- Login-protected operations pages
- Responsive desktop/mobile layout

## Requirements
- Python 3.10+
- pip

## Run on Windows
Open PowerShell in this folder.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate --run-syncdb
python manage.py seed_demo
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Demo login
- Username: `demo`
- Password: `Demo12345!`

The demo user is a Django staff user, so the Django admin is available at `/admin/`. The seed command creates only synthetic demo records.

## Main routes
- `/` — dashboard
- `/atms/` — digital devices
- `/incidents/` — incident management
- `/sla/` — SLA monitoring
- `/maintenance/` — maintenance
- `/reports/incidents.csv` — downloadable incident report
- `/admin/` — Django administration

## Data model
`District → Branch → ATM → Incident / Maintenance`, with `AuditLog` records for create/update actions performed through the UI.

## SLA rules in this prototype
| Incident type | Target |
|---|---:|
| Cash low | 2 hours |
| Network failure | 2 hours |
| Dispenser error | 4 hours |
| Card reader | 4 hours |
| Power failure | 4 hours |
| Software / other | 8 hours |

These are illustrative demo targets, not Hijra Bank policy. Change `Incident.sla_hours` in `ops/models.py` to adjust them.

## Before deployment
This is a local portfolio/demo build, not production-ready banking software. Before any real deployment:
1. Move `SECRET_KEY` to an environment variable and set `DEBUG=False`.
2. Configure production `ALLOWED_HOSTS`, HTTPS, secure cookies, logging, backups, and monitoring.
3. Use PostgreSQL or another managed production database.
4. Add formal role/permission policies, MFA, security testing, audit retention, and approval workflows.
5. Integrate only through approved, documented APIs and test environments.
6. Remove all demo credentials and seed data.
7. Obtain authorization before using any bank logo, name, internal data, or connecting to real systems.

## Portfolio presentation
Suggested project description:
> Designed and developed a Django-based digital operations prototype for device inventory, incident tracking, SLA monitoring, maintenance scheduling, and reporting. The project demonstrates relational data modeling, authenticated workflows, CRUD operations, server-rendered UI, business-rule implementation, and CSV reporting.

## Suggested next improvements
- Django REST Framework API endpoints and OpenAPI documentation
- Fine-grained Django Groups/Permissions and district-level access
- Unit tests for SLA calculations and incident transitions
- PostgreSQL, Docker, CI, and deployment
- Background notifications and approved monitoring-system integrations
