# SaaS API Platform

A complete SaaS API platform with Stripe integration, user management, and analytics.

## Features

- User Authentication & Management
- API Key Generation & Management
- Stripe Integration for Payments
- Usage Tracking & Analytics
- Admin Dashboard
- Frontend Components

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/saas-api-platform.git
cd saas-api-platform
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
alembic upgrade head
```

6. Run the development server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker Deployment

```bash
docker-compose up -d
```

## License

MIT