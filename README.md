# CRBS
Campus Resource Booking System for Software Engineering Fundamentals

## Run (development)

```powershell
.venv\Scripts\Activate.ps1          # activate venv (Windows)
pip install -r requirements.txt     # first time only
flask run                           # http://127.0.0.1:5000
```

No `.env` is needed: the app falls back to a local SQLite file (`crbs.db`) and
seeds demo data on first start. To use PostgreSQL instead, copy `.env.example`
to `.env` and fill in the `DB_*` values. `python app.py` also works (debug mode).

### Demo accounts (password `password123`)

| Email | Role |
|---|---|
| student@mmu.edu.my | student |
| lecturer@mmu.edu.my | staff |
| manager@mmu.edu.my | manager |
| admin@mmu.edu.my | admin |

## API

| Method | Endpoint | Roles | Purpose |
|---|---|---|---|
| POST | `/api/user/login` `/logout` `/register` | all | Auth + session |
| GET  | `/api/user/me` | any signed-in | Current user / role |
| GET  | `/api/resource/search` | student, staff | Search & Book filter |
| GET  | `/api/resource` | any signed-in | List all resources |
| GET  | `/api/booking` | student, staff | My bookings |
| POST | `/api/booking` | student, staff | Create single booking |
| POST | `/api/booking/recurring` | student, staff | Create recurring series |
| PUT  | `/api/booking/<id>` | student, staff | Modify (24h policy) |
| DELETE | `/api/booking/<id>` | student, staff | Cancel (24h policy) |
| POST | `/api/booking/<id>/checkin` | student, staff | Confirm attendance |
| GET  | `/api/notification` | any signed-in | Bell feed + unread count |
| POST | `/api/notification/<id>/read`, `/read-all` | any signed-in | Mark read |
| GET/PUT | `/api/profile` | any signed-in | Profile settings |
