# CampusIQ — Student Success Intelligence

A Flask-based prototype for integrating student indicators, calculating a transparent Student Success Score, identifying academic and placement risk, grouping students into segments, and presenting data-backed recommendations.

## Features in this starter
- Dark, responsive HTML/CSS/JavaScript dashboard inspired by the supplied reference.
- Flask REST endpoints for students, analytics, and agent insights.
- SQLAlchemy student model.
- Transparent, inspectable prototype score and rule-based risk assessments.
- Actionable student segments and recommendation-agent endpoint.
- Synthetic demo data generator.
- PostgreSQL-compatible database configuration.

## Important model limitation
The current score and risk thresholds are transparent prototype heuristics, not a validated prediction of future student outcomes. Demo data is synthetic. Do not use the prototype to make consequential decisions about real students without institutional validation, fairness checks, privacy controls, and faculty review.

## Run locally (Windows PowerShell)
1. Install Python 3.11 or newer.
2. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
3. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and change `SECRET_KEY`.
5. Generate demo records:
   ```powershell
   python -m scripts.seed_demo_data
   ```
6. Start the app:
   ```powershell
   python run.py
   ```
7. Open http://127.0.0.1:5000

## API endpoints
- `GET /health`
- `GET /api/students`
- `GET /api/students/<student_id>`
- `POST /api/students`
- `GET /api/analytics/summary`
- `GET /api/agents/insights`
- `GET /api/agents/student/<student_id>`

## Next steps before production
Authentication and role-based authorization, robust input validation, CSV import preview, migrations, rate limiting, audit logs, model evaluation, privacy controls, integration tests, and production deployment configuration still need to be completed.

## Deployment
Vercel's Python runtime and routing constraints must be verified against the final app. Use a managed PostgreSQL database for production; do not rely on a local SQLite file in serverless deployment. If the full Flask application or ML dependencies do not fit the Vercel runtime, deploy Flask to a Python-friendly host and keep the frontend/API domain configured appropriately.
