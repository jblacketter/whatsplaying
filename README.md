# WhatsPlaying

A Django web app to track movies and TV shows across your streaming services.

## Features

- 🔍 Search movies and TV shows
- 🎭 Search by actors and directors
- 📺 Track what you want to watch
- 🎬 See where content is streaming
- 👤 Personalized for your streaming services

## Local Development

1. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your TMDb API key
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Create superuser:
```bash
python manage.py createsuperuser
```

6. Populate streaming services:
```bash
python manage.py populate_services
```

7. Run development server:
```bash
python manage.py runserver
```

## Deployment to Render

1. Push to GitHub
2. Connect to Render
3. Deploy using render.yaml configuration

## Environment Variables

- `SECRET_KEY`: Django secret key
- `TMDB_API_KEY`: Your TMDb API key
- `DATABASE_URL`: PostgreSQL connection string (for production)

## Tech Stack

- Django 5.2
- TMDb API
- PostgreSQL (production)
- SQLite (development)