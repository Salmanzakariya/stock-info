# Indian Stock Market News App

A web application that delivers live, India-specific stock market news with AI-powered sentiment analysis and summaries.

## Features

- Live stock market news feed
- AI-powered sentiment analysis
- Trending stocks detection
- Search and filter functionality
- Daily news digest
- Clean, responsive UI with Tailwind CSS

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
Create a `.env` file in the project root with:
```
SECRET_KEY=your_django_secret_key
DEBUG=True
DATABASE_URL=your_postgres_url
DEEPSEEK_API_KEY=your_deepseek_api_key
```

4. Apply migrations:
```bash
python manage.py migrate
```

5. Create superuser (optional):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure

- `stocknews/` - Main Django project
- `news/` - News app containing models, views, and templates
- `static/` - Static files (CSS, JS, images)
- `templates/` - HTML templates
- `docs/` - Documentation files
