# CRBS — Campus Resource Booking System

> A web application that lets a university community **find, book, and manage
> shared campus resources** — meeting rooms, labs, and equipment — with
> role-aware workflows for students, staff, managers, and admins.

CRBS is a Flask + vanilla-JavaScript prototype built for the **Software
Engineering Fundamentals** coursework. It demonstrates a complete booking
lifecycle: searching for a resource, reserving it, approval of specialised
resources, check-in, fault reporting, and management reporting — all backed by
a clean JSON API and a server-rendered, role-aware interface.

---

## Table of contents

- [Product overview](#product-overview)
- [Who uses it (roles)](#who-uses-it-roles)
- [Key features](#key-features)
- [How to launch](#how-to-launch)
- [Demo accounts](#demo-accounts)
- [Technical documentation](#technical-documentation)
  - [Technology stack](#technology-stack)
  - [Architecture](#architecture)
  - [Project structure](#project-structure)
  - [Data model](#data-model)
  - [API reference](#api-reference)
  - [Page routes](#page-routes)
  - [Core domain rules](#core-domain-rules)
  - [Configuration](#configuration)
- [Resetting & troubleshooting](#resetting--troubleshooting)


---

## Product overview

Universities share a finite pool of physical resources. Without a single
system, double-bookings, no-shows, and broken equipment go unnoticed. **CRBS
centralises the whole process:**

- **Find** an available room, lab, or piece of equipment that fits your needs.
- **Book** it for a one-off slot or a recurring series — the system blocks
  clashing reservations automatically.
- **Approve** bookings for specialised, high-demand resources before they are
  confirmed.
- **Check in** when you arrive so missed slots are released for others.
- **Report faults** with a photo so managers can act.
- **Report & analyse** usage as a downloadable PDF.

The interface is a lightweight server-rendered shell with a role-aware sidebar —
each user only sees the pages and actions their role allows. There is **no build
step**: open the app and it works out of the box on a local database seeded with
demo data.

## Who uses it (roles)

CRBS has four roles, each with a tailored experience:

| Role | Who they are | What they can do |
|------|--------------|------------------|
| **Student** | Undergraduate / postgraduate | Search & book resources, manage their bookings, check in, report faults |
| **Staff** | Lecturers & teaching staff | Everything a student can do, plus submit specialised-equipment requests |
| **Manager** | Resource & facilities managers | Manage resources and equipment, approve bookings/requests, generate reports |
| **Admin** | System administrators | Oversight across resources and equipment, reporting |

## Key features

- 🔎 **Smart search & booking** — filter resources by type, capacity, and
  availability, then book in a couple of clicks.
- 🔁 **Recurring bookings** — weekly or monthly series; the whole series is
  rejected if *any* generated slot clashes, so you never get a half-booked
  schedule.
- ✅ **Approval workflow** — *specialised* resources create a **pending**
  booking that a manager must approve; everything else is auto-**confirmed**.
- ⏰ **24-hour change lock** — bookings can't be modified or cancelled within 24
  hours of their start time, protecting the schedule from last-minute churn.
- 🚪 **Check-in & no-show handling** — users confirm attendance within a grace
  window; missed check-ins are automatically swept to **no-show**.
- 🛠️ **Equipment requests & management** — staff request specialised equipment;
  managers maintain the equipment catalogue.
- 🐞 **Fault reporting** — students/staff report broken resources with an
  optional photo upload.
- 🔔 **Notifications** — every user-facing action raises an in-app
  notification (bell feed), with an **optional** email channel.
- 📄 **PDF reporting** — managers/admins export usage reports generated on the
  fly with ReportLab.

> _Screenshots: add images to a `docs/screenshots/` folder and embed them here,
> e.g._ `![Dashboard](docs/screenshots/dashboard.png)`.

---

## How to launch

### Prerequisites

- **Python 3.11+** and `pip`
- Windows PowerShell (commands below) — equivalents work on macOS/Linux
- No database server required (SQLite is used by default)

### Quick start (Windows / PowerShell)

```powershell
# 1. Create and activate a virtual environment (first time only)
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies (first time only)
pip install -r requirements.txt

# 3. Run the app
flask run                 # http://127.0.0.1:5000   (production-style, no debug)
# or
python app.py             # same app with debug=True (auto-reload)
```

On macOS / Linux, swap the activation step for `source .venv/bin/activate`.

### What happens on first run

There is **zero setup**. With no `DB_*` environment variables present:

1. `config.py` falls back to a local SQLite file, **`crbs.db`**, created next to
   the project.
2. `create_app()` builds the full schema with `db.create_all()`.
3. `seed.py` populates demo users, resources, and equipment — **only when the
   `user` table is empty**.

Open <http://127.0.0.1:5000> and log in with one of the [demo accounts](#demo-accounts).

### Using PostgreSQL instead (optional)

Set the following in a `.env` file at the project root (psycopg2 is already
installed):

```dotenv
DB_USER=crbs
DB_PASS=yourpassword
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crbs
```

The app switches to PostgreSQL automatically when `DB_USER` is present.

## Demo accounts

All seeded accounts use the password **`password123`**.

| Email | Role |
|-------|------|
| `student@mmu.edu.my` | student |
| `lecturer@mmu.edu.my` | staff |
| `manager@mmu.edu.my` | manager |
| `admin@mmu.edu.my` | admin |

---

## Technical documentation

### Technology stack

| Layer | Technology |
|-------|------------|
| Web framework | **Flask 3** (app-factory pattern) |
| ORM / DB | **Flask-SQLAlchemy 3** over SQLAlchemy 2 — SQLite by default, PostgreSQL optional |
| Migrations | Flask-Migrate (wired up, but schema is built via `create_all()` at startup) |
| Auth | Hand-rolled **session-based** auth; passwords hashed with Werkzeug |
| Templating | Jinja2 server-rendered pages |
| Frontend | **Vanilla JS** + **Tailwind CSS** (CDN) + **Lucide** icons (CDN) — no bundler |
| Reporting | **ReportLab** (PDF generated in-memory and streamed) |
| Email (optional) | Standard-library SMTP via `email_service.py`, off by default |

### Architecture

- **App factory.** `app.py:create_app()` binds extensions, registers
  blueprints and centralised error handlers, then builds and seeds the database.
  Both `flask run` and `python app.py` use the module-level `app`.
- **`extensions.py` is the shared import hub.** It instantiates `db` and
  `migrate`, re-exports common Flask symbols, and defines the auth primitives
  used everywhere: `current_user_id()`, `current_role()`, `@login_required`, and
  `@role_required(*roles)`. The four roles are
  `ALL_ROLES = ("student", "staff", "manager", "admin")`.
- **Session-based auth (not Flask-Login).** `blueprints/user/user.py` sets
  `session["userId"]` and `session["role"]` on login/register. There is **no
  CSRF protection** (`WTF_CSRF_ENABLED = False`); the API relies on the
  same-origin session cookie.
- **Centralised error handling.** Handlers in `app.py` turn
  `abort(code, description=...)` into `{"error": ...}` JSON. `409` signals
  conflicts (booking overlap, capacity, duplicate email/id).
- **Thin routes, fat services.** Route handlers validate input, enforce roles,
  call a feature's `services.py`, and return `jsonify(...)`.

### Project structure

```
CRBS/
├── app.py                  # App factory, extension binding, error handlers
├── config.py               # DB URI selection, uploads, optional email config
├── extensions.py           # Shared db/migrate + auth primitives & role guards
├── models.py               # All SQLAlchemy models (one shared metadata)
├── seed.py                 # Demo data, loaded only when the user table is empty
├── storage.py              # Upload saving helpers (documents / images)
├── email_service.py        # Optional SMTP notification channel
├── requirements.txt
├── blueprints/
│   ├── __init__.py         # register_blueprints()
│   ├── views/              # Server-rendered HTML pages (no /api prefix)
│   ├── user/               # Login / register / logout / me
│   ├── userProfile/        # Profile read/update  (/api/profile)
│   ├── resource/           # Resource search & CRUD
│   ├── booking/            # Bookings, recurrence, check-in (core domain logic)
│   ├── equipment/          # Equipment listing + specialised requests
│   ├── equipment_manage/   # Manager equipment CRUD
│   ├── notification/       # Bell feed + read state
│   ├── dashboard/          # Role-aware dashboard metrics
│   ├── issue/              # Fault reports
│   └── report/             # PDF export (ReportLab)
├── templates/              # Jinja templates; base.html is the shell
├── static/js/              # api.js, app.js, pages.js + per-page scripts
└── uploads/                # Saved booking documents & issue images
```

### Data model

All models live in `models.py` and share one metadata. Every model exposes a
`to_dict()` that defines its JSON shape — **changing a `to_dict()` changes the
API contract.** Note the **camelCase** column names. `User.userId` is a string
PK; all other PKs are autoincrement integers.

| Model | Key fields | Notes |
|-------|------------|-------|
| **User** | `userId` (str PK), `name`, `email`, `password`, `role` | Roles: `student / staff / manager / admin` |
| **Resource** | `resourceId`, `name`, `type`, `capacity`, `location`, `status`, `isSpecialised` | `status`: `available / maintenance / faulty`; specialised resources need approval |
| **Booking** | `bookingId`, `resourceId`, `userId`, `startTime`, `endTime`, `status`, `isRecurring`, `recurrence`, `checkedInAt`, `documentPath` | `status`: `confirmed / pending / cancelled / checked_in / no_show` |
| **Notification** | `notificationId`, `userId`, `title`, `message`, `type`, `isRead` | `type`: `info / maintenance / checkin / approval` |
| **Maintenance** | `maintenanceId`, `resourceId`, `scheduledDate`, `completedDate`, `status`, `duration` | Maintenance scheduling record |
| **Equipment** | `equipmentId`, `resourceId`, `name`, `type`, `quantity`, `isSpecialised`, `condition` | `condition`: `good / degraded / faulty / broken` |
| **EquipmentRequest** | `requestId`, `userId`, `equipmentName`, `purpose`, `requestedDate`, `attendees`, `status` | Staff request to use specialised equipment; `status`: `pending / approved / rejected` |
| **IssueReport** | `reportId`, `userId`, `resourceId`, `bookingId`, `description`, `imagePath`, `status` | Fault report; `status`: `open / in_progress / resolved` |

### API reference

All API endpoints are JSON, prefixed `/api`, and protected by the session
cookie. **Roles** indicates who may call each route (`any` = any signed-in
user). Failures use `abort(code, description=...)` and return `{"error": ...}`.

#### Auth & profile

| Method | Endpoint | Roles | Purpose |
|--------|----------|-------|---------|
| POST | `/api/user/login` | public | Sign in, set session |
| POST | `/api/user/register` | public | Register a new account |
| POST | `/api/user/logout` | any | Clear session |
| GET | `/api/user/me` | any | Current user + role |
| GET | `/api/profile` | any | Read profile |
| PUT | `/api/profile` | any | Update name / email / password |

#### Resources

| Method | Endpoint | Roles | Purpose |
|--------|----------|-------|---------|
| GET | `/api/resource` | any | List all resources |
| GET | `/api/resource/search` | student, staff | Search & filter for booking |
| POST | `/api/resource` | manager | Create a resource |
| PUT | `/api/resource/<id>` | manager | Update a resource |
| DELETE | `/api/resource/<id>` | manager | Delete a resource |

#### Bookings

| Method | Endpoint | Roles | Purpose |
|--------|----------|-------|---------|
| GET | `/api/booking` | any | The signed-in user's bookings |
| POST | `/api/booking` | student, staff | Create a single booking |
| POST | `/api/booking/recurring` | student, staff | Create a recurring series |
| PUT | `/api/booking/<id>` | student, staff | Modify (subject to 24h lock) |
| DELETE | `/api/booking/<id>` | student, staff | Cancel (subject to 24h lock) |
| POST | `/api/booking/<id>/checkin` | student, staff | Confirm attendance |

#### Equipment

| Method | Endpoint | Roles | Purpose |
|--------|----------|-------|---------|
| GET | `/api/equipment` | any | List equipment catalogue |
| POST | `/api/equipment/request` | staff, admin | Submit a specialised-equipment request |
| GET | `/api/equipment/request` | any | The signed-in user's requests |
| GET | `/api/equipment/manage` | any | List equipment (management view) |
| POST | `/api/equipment/manage` | manager | Create equipment |
| PUT | `/api/equipment/manage/<id>` | manager | Update equipment |
| DELETE | `/api/equipment/manage/<id>` | manager | Delete equipment |

#### Notifications, dashboard, issues & reports

| Method | Endpoint | Roles | Purpose |
|--------|----------|-------|---------|
| GET | `/api/notification` | any | Bell feed + unread count |
| POST | `/api/notification/<id>/read` | any | Mark one as read |
| POST | `/api/notification/read-all` | any | Mark all as read |
| GET | `/api/dashboard` | any | Role-aware dashboard metrics |
| GET | `/api/issue` | any | List fault reports |
| POST | `/api/issue` | student, staff | File a fault report (optional image) |
| GET | `/api/report/export` | manager, admin | Download a usage PDF |

> Uploaded files (booking documents, issue images) are served to signed-in
> users from `/uploads/<filename>` and capped at **8 MB** per upload.

### Page routes

Server-rendered pages (no `/api` prefix). Access is enforced server-side via
`page_roles(...)`: anonymous users are redirected to login, wrong-role users to
the dashboard.

| Path | Roles | Page |
|------|-------|------|
| `/` | public | Login |
| `/signup` | public | Sign up |
| `/dashboard` | all | Dashboard |
| `/search` | student, staff | Search & book |
| `/bookings` | student, staff | Manage bookings |
| `/report-issue` | student, staff | Report a fault |
| `/resource` | manager, admin | Manage resources |
| `/equipment` | staff, manager, admin | Equipment |
| `/equipment/manage` | manager, admin | Manage equipment |
| `/approvals` | manager, admin | Approvals |
| `/profile` | all | Profile settings |

### Core domain rules

The domain logic worth knowing lives in `blueprints/booking/services.py`:

- **Conflict detection** — `has_conflict()` rejects overlapping bookings,
  considering only slots in `ACTIVE_STATUSES = (confirmed, pending, checked_in)`.
- **Approval routing** — bookings for **specialised** resources are created
  `pending` (manager approval required); all others are auto-`confirmed`.
- **Recurring series are all-or-nothing** — `recurrence_dates()` generates the
  weekly/monthly slots, and the whole series is aborted if *any* slot conflicts.
- **24-hour change lock** — `within_lock_window()` blocks modify/cancel within
  `MODIFY_LOCK_HOURS = 24` of a booking's start.
- **Check-in & no-show sweep** — check-in is allowed up to
  `CHECKIN_EARLY_MINUTES = 15` before start; `sweep_no_shows()` lazily flips
  missed bookings to `no_show` when the bookings list is viewed.
- **Notifications** — user-facing actions emit a `Notification` via the single
  `notify()` helper, which also triggers the optional email channel.

### Configuration

Configuration is read from environment variables (via `.env`) in `config.py`.
All have safe defaults so the app runs with no `.env` at all.

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | `dev-secret-change-me` | Flask session signing key |
| `DB_USER` / `DB_PASS` / `DB_HOST` / `DB_PORT` / `DB_NAME` | _(unset → SQLite)_ | PostgreSQL connection; when `DB_USER` is set, Postgres is used |
| `MAIL_ENABLED` | `false` | Turn the email notification channel on |
| `MAIL_SERVER` / `MAIL_PORT` / `MAIL_USE_TLS` / `MAIL_USE_SSL` | `587` / TLS on | SMTP server settings |
| `MAIL_USERNAME` / `MAIL_PASSWORD` / `MAIL_DEFAULT_SENDER` | _(unset)_ | SMTP credentials & sender |

Uploads are capped at **8 MB** (`MAX_CONTENT_LENGTH`) and saved under
`uploads/`. Email is **opt-in and off by default** — notifications still appear
in-app without any SMTP setup.

---

## Resetting & troubleshooting

- **Reset all data:** stop the app, delete `crbs.db`, and restart. The schema is
  rebuilt and demo data is re-seeded automatically.
- **Demo data didn't appear:** seeding runs only when the `user` table is empty.
  Delete `crbs.db` to force a fresh seed.
- **`flask run` can't find the app:** ensure the virtual environment is
  activated and you are in the project root (the app object is `app.py:app`).
- **Login keeps redirecting:** you're not signed in, or your role can't access
  that page — sign in with an account whose role allows it (see
  [page routes](#page-routes)).

---

