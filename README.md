# Course Project — Django Backend (game_backend)

This project is a ready-to-deploy Django REST backend for a Unity WebGL game.
It includes JWT authentication, player data APIs, leaderboard endpoints, and is
configured for deployment on Render (PostgreSQL).

## Features
- Register (POST /api/register/)
- Login (POST /api/login/) -> returns JWT tokens
- Refresh token (POST /api/token/refresh/)
- Player data (GET/POST /api/playerdata/) — requires Authorization: Bearer <token>
- Submit score (POST /api/score/) — stores score and updates leaderboard
- Leaderboard (GET /api/leaderboard/) — top scores

## Quick local setup (Windows 11)
1. Create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill values (SECRET_KEY, DATABASE_URL)
3. Run migrations and create superuser:
   ```
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
4. APIs:
   - POST /api/register/  {username,email,password}
   - POST /api/login/  {username,password}
   - GET /api/playerdata/  (Auth header required)
   - POST /api/playerdata/  {coins,level}
   - POST /api/score/  {score}
   - GET /api/leaderboard/

## Deploy to Render (recommended free student option)
- Create a new Web Service on Render, connect to this GitHub repo.
- Set Environment Variables from `.env` in Render dashboard.
- Use Procfile `web: gunicorn game_backend.wsgi`
- Render will provide a Postgres DATABASE_URL you can use.

## Unity (WebGL) example: register & login
Use `UnityWebRequest` to POST to the endpoints (example in README of repo).

