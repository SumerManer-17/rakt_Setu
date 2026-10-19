# 🩸 RaktSetu — Blood Donor Emergency Matcher

**RaktSetu** is a real-time blood donor emergency matching platform built for India. It connects patients in urgent need of blood with nearby, eligible, and active voluntary donors — using GPS-based proximity matching and instant WhatsApp alerts.

> "Real donors. Real availability. Real time."

---

## 📌 What problem it solves

During a blood emergency, finding the right blood group donor nearby is stressful and time-consuming. RaktSetu automates this:

1. A donor registers with their blood group, phone number, and location.
2. A requester posts an emergency blood request (hospital, blood group, units needed).
3. The system finds the **nearest 5 eligible donors** within 10 km and alerts them instantly via WhatsApp.
4. If no one responds within 10 minutes, the search radius automatically expands to 25 km, then 50 km.
5. A donor replies `HELP` on WhatsApp → the requester receives the donor's contact immediately.
6. Donors are pinged every 30 days to confirm availability, so inactive numbers are never called.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🩸 **Donor Registration** | Register with name, phone, blood group, pincode, city, and GPS location |
| 🆘 **Emergency Requests** | Post a blood emergency with hospital details and location |
| 📍 **GPS-Based Matching** | Haversine formula finds the nearest eligible donors (10 km → 25 km → 50 km) |
| 📱 **WhatsApp Alerts** | Donors receive instant WhatsApp template messages (Meta WhatsApp Cloud API) |
| ✅ **Donor Replies via Webhook** | `HELP`, `YES`, `NO`, `SKIP` replies update donor status and fulfill requests |
| ⏱️ **Auto-Expand Search** | Radius expands automatically after 10 minutes of no response |
| 📅 **Eligibility Window** | Donors must wait 90 days between donations (configurable) |
| 🔄 **Monthly Activity Ping** | Confirms donor availability every 30 days; marks stale donors inactive |
| 🗺️ **Live Map** | Leaflet.js map view of donors and emergency locations |
| 📊 **Admin Dashboard** | Donor/request stats, blood-group-wise breakdown, response rates |
| 📱 **Responsive Frontend** | Vanilla HTML/CSS/JS pages served by Flask (no separate frontend build) |

---

## 🛠️ Tech Stack

**Backend**
- Python 3.11.9
- Flask 3.0.0 (web framework)
- Flask-SQLAlchemy 3.1.1 (ORM)
- Flask-CORS 4.0.0 (cross-origin requests)
- APScheduler 3.10.4 (background jobs: monthly ping, expiry, inactive marking)
- Gunicorn 21.2.0 (production WSGI server)
- psycopg2-binary 2.9.9 (PostgreSQL adapter)
- python-dotenv 1.0.0 (environment variables)
- requests 2.31.0 (WhatsApp Cloud API calls)

**Database**
- PostgreSQL (hosted on Supabase in this project)

**Frontend**
- HTML5, CSS3, Vanilla JavaScript
- Leaflet.js (interactive maps)

**Communication**
- Meta WhatsApp Cloud API (template-based messages)

---

## 📂 Project Structure

```
rakt_Setu/
├── backend/
│   ├── app.py                      # Flask application factory & entry point
│   ├── config.py                   # Configuration (DB, WhatsApp, scheduler settings)
│   ├── database/
│   │   └── db.py                   # SQLAlchemy instance & init_db()
│   ├── models/
│   │   ├── __init__.py
│   │   ├── donor.py                # Donor model (donors table)
│   │   ├── donation.py             # DonationHistory model
│   │   ├── request.py              # EmergencyRequest model
│   │   └── alert.py                # DonorAlert model
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── donor_routes.py         # /api/donors (register, list, profile, toggle)
│   │   ├── request_routes.py       # /api/requests (emergency, status, open, cancel)
│   │   ├── webhook_routes.py       # /webhook (WhatsApp verification + message handling)
│   │   └── admin_routes.py         # /api/admin (stats, donors, requests, blood-groups)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── eligibility.py          # 90-day donation gap logic
│   │   ├── matching.py             # Haversine distance + donor matching + alerts
│   │   ├── whatsapp.py             # WhatsApp Cloud API message sender
│   │   └── scheduler.py            # Background jobs (ping, expiry, inactive check)
│   ├── static/                     # Frontend assets served by Flask
│   │   ├── index.html              # Landing page
│   │   ├── css/                    # style.css, map.css, dashboard.css, leaflet.css
│   │   ├── js/                     # api.js, register.js, emergency.js, map.js, dashboard.js, leaflet.js
│   │   └── pages/                  # register.html, emergency.html, map.html, dashboard.html, login.html, status.html, admin.html
│   └── utils/
│       ├── __init__.py
│       ├── helpers.py              # response helpers, phone formatter, freshness label
│       └── validators.py           # phone, blood group, pincode, donor/request validation
├── frontend/                       # (reserved for future SPA frontend)
├── .env                            # Environment variables (gitignored — never commit)
├── .gitignore                      # Ignores .env*, __pycache__, etc.
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version (python-3.11.9)
└── test_connection.py              # Script to verify PostgreSQL connection
```

---

## 🖥️ API Endpoints

### Donors
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/donors/register` | Register a new donor |
| `GET` | `/api/donors/active?blood_group=O+` | List active donors (optional blood group filter) |
| `GET` | `/api/donors/<phone>` | Get donor profile with eligibility & donation history |
| `PUT` | `/api/donors/<phone>` | Update donor profile |
| `PATCH` | `/api/donors/<phone>/toggle` | Toggle donor active/inactive status |

### Emergency Requests
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/requests/emergency` | Post a new emergency blood request |
| `GET` | `/api/requests/<id>/status` | Get request status + alert summary |
| `GET` | `/api/requests/open?blood_group=O+` | List open requests |
| `PATCH` | `/api/requests/<id>/cancel` | Cancel an open request |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/admin/stats` | Dashboard statistics |
| `GET` | `/api/admin/donors` | All donors |
| `GET` | `/api/admin/requests` | All requests |
| `GET` | `/api/admin/blood-groups` | Blood-group-wise donor stats |

### Webhook (WhatsApp)
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/webhook` | Meta webhook verification |
| `POST` | `/webhook` | Receive donor WhatsApp replies (`HELP`, `YES`, `NO`, `SKIP`) |

### Pages (served by Flask)
`/`, `/index.html`, `/dashboard.html`, `/login.html`, `/register.html`, `/admin.html`, `/map.html`, `/emergency.html`, `/status.html`

---

## 🖥️ How to Clone & Run on Another Machine

Follow these steps to set up RaktSetu on a fresh machine.

### Prerequisites

- **Python 3.11** (project uses `python-3.11.9`, see `runtime.txt`)
- **pip** (Python package installer)
- **Git**
- A **PostgreSQL database** (the project is configured for Supabase, but any PostgreSQL works)
- A **Meta WhatsApp Cloud API** account (for WhatsApp alerts; optional for local testing without alerts)

---

### Step 1 — Clone the Repository

Open your terminal/command prompt and run:

```bash
# Clone the repository
git clone https://github.com/SumerManer-17/rakt_Setu.git

# Enter the project directory
cd raktsetu
```

---

### Step 2 — Create a Virtual Environment

It is strongly recommended to use a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows (PowerShell):
venv\Scripts\Activate.ps1

# On Windows (Command Prompt):
venv\Scripts\activate.bat

# On macOS / Linux:
source venv/bin/activate
```

---

### Step 3 — Install Python Dependencies

```bash
pip install -r requirements.txt
```

This installs Flask, Flask-SQLAlchemy, Flask-CORS, psycopg2-binary, python-dotenv, requests, apscheduler, gunicorn, and other dependencies.

---

### Step 4 — Configure Environment Variables

The `.env` file is **gitignored** (not committed) for security. You must create your own:

1. Copy the example below into a new file named `.env` in the project root:

```env
# ─────────────────────────────────────────
# RaktSetu — Environment Variables
# NEVER push this file to GitHub
# ─────────────────────────────────────────

# PostgreSQL Database URL (Supabase or any PostgreSQL provider)
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Flask
SECRET_KEY=your_long_random_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# WhatsApp Cloud API (Meta) — required only for WhatsApp alerts
WHATSAPP_TOKEN=your_whatsapp_access_token_here
PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_API_VERSION=v18.0

# Webhook verification token (must match what you set in Meta dashboard)
VERIFY_TOKEN=raktsetu_webhook_secret_2024

# App URL
APP_URL=http://localhost:5000
```

2. Replace `DATABASE_URL` with your own PostgreSQL connection string.
3. Replace WhatsApp values with your Meta WhatsApp Cloud API credentials (or leave as placeholders if you only want to test the API locally without sending messages).

> ⚠️ **Security:** Never commit your `.env` file. It contains database credentials and secret keys.

---

### Step 5 — Set Up the Database

The database tables are created automatically when the app starts (`db.create_all()` in `init_db`). You do not need to run migrations manually.

To verify your database connection before running the app:

```bash
python test_connection.py
```

You should see:
```
✅ Connected successfully!
PostgreSQL version: ...
```

If it fails, check your `DATABASE_URL` in `.env` and ensure your database server allows connections from your IP.

---

### Step 6 — Run the Application

#### Option A: Development mode (recommended for local testing)

```bash
# From the project root (with venv activated)
python backend/app.py
```

Or:

```bash
flask --app backend/app run --debug
```

The server will start at **http://localhost:5000**.

#### Option B: Production mode (with Gunicorn)

```bash
gunicorn backend:app
```

Gunicorn will serve the app (default port 8000).

---

### Step 7 — Open the Application

Open your browser and go to:

```
http://localhost:5000
```

You will see the RaktSetu landing page. From there you can:
- **Register as a donor** → `/register.html`
- **Post an emergency** → `/emergency.html`
- **View live map** → `/map.html`
- **Dashboard / profile** → `/dashboard.html`
- **Admin panel** → `/admin.html`

---

## 📱 WhatsApp Integration (Optional but Recommended)

RaktSetu uses the **Meta WhatsApp Cloud API** to send template messages to donors:

1. Create a WhatsApp Business App in the [Meta for Developers dashboard](https://developers.facebook.com/).
2. Set up a phone number and obtain:
   - **Access Token** → `WHATSAPP_TOKEN`
   - **Phone Number ID** → `PHONE_NUMBER_ID`
3. Upload and approve message templates:
   - `emergency_blood_alert` — sent to donors when a match is found
   - `monthly_donor_ping` — monthly availability check
   - `donor_confirmed` — sent to requester when a donor accepts
   - `registration_success` — sent after donor registration
4. Configure the webhook URL `https://your-domain.com/webhook` in Meta dashboard with your `VERIFY_TOKEN`.
5. Add the values to your `.env` file.

**Donor replies:** When a donor replies `HELP`, `YES`, `NO`, or `SKIP`, Meta sends a POST to `/webhook`, which updates the donor status and/or fulfills the emergency request.

> Without WhatsApp credentials, the API routes still work, but alert-sending functions will catch exceptions and print errors to the console instead of sending messages.

---

## 🧪 Testing

### Verify Database Connection
```bash
python test_connection.py
```

### Manual API Tests (with curl or Postman)

Register a donor:
```bash
curl -X POST http://localhost:5000/api/donors/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Rahul Sharma","phone":"9876543210","blood_group":"O+","pincode":"110001","city":"Delhi","latitude":28.6139,"longitude":77.2090}'
```

Post an emergency request:
```bash
curl -X POST http://localhost:5000/api/requests/emergency \
  -H "Content-Type: application/json" \
  -d '{"requester_name":"City Hospital","requester_phone":"9123456780","blood_group":"O+","hospital_name":"City Hospital","hospital_address":"Connaught Place, Delhi","latitude":28.6139,"longitude":77.2090,"units_needed":2}'
```

Get open requests:
```bash
curl http://localhost:5000/api/requests/open
```

Get admin stats:
```bash
curl http://localhost:5000/api/admin/stats
```

---

## ⚙️ Configuration Reference (`backend/config.py`)

| Setting | Default | Description |
|---------|---------|-------------|
| `INITIAL_DONOR_BATCH` | 5 | Donors alerted in the first batch |
| `EXPAND_WAIT_MINUTES` | 10 | Minutes before expanding search radius |
| `INITIAL_RADIUS_KM` | 10 | First search radius |
| `EXPAND_RADIUS_KM` | 25 | Second search radius |
| `MAX_RADIUS_KM` | 50 | Maximum search radius |
| `DONATION_GAP_DAYS` | 90 | Minimum days between donations |
| `DONOR_PING_INTERVAL_DAYS` | 30 | Days between activity pings |
| `DONOR_INACTIVE_AFTER_HOURS` | 48 | Hours before marking donor inactive |

---

## 🚧 Deployment Notes

- **Database:** Use a managed PostgreSQL (Supabase, Railway, Render, Heroku Postgres, etc.). Update `DATABASE_URL` in `.env`.
- **HTTPS:** WhatsApp webhooks require a public HTTPS URL. Use a tunnel (ngrok) for local testing or deploy to a platform with HTTPS.
- **Production:** Run with `gunicorn` behind a reverse proxy (Nginx/Cloudflare). Set `FLASK_DEBUG=False` and use a strong `SECRET_KEY`.
- **Scheduler:** Background jobs (monthly ping, inactive marking, request expiry) run automatically when `start_scheduler(app)` is enabled in `app.py`. It is currently commented out — uncomment it if you need scheduled jobs.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m "Add your message"`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## 📄 License

This project is created for educational/social impact purposes to help connect blood donors with those in need.

---

## 🙏 Acknowledgments

- [Flask](https://flask.palletsprojects.com/)
- [Meta WhatsApp Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Leaflet.js](https://leafletjs.com/)
- [Supabase PostgreSQL](https://supabase.com/)

---

**Made with ❤️ to save lives — one blood donation at a time.**
