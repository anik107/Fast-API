# FastAPI Todo App - Docker Setup

## Quick Start

1. **Start the application:**
   ```bash
   docker compose up --build
   ```

2. **Access the application:**
   - FastAPI App: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Stop the application:**
   ```bash
   docker compose down
   ```

## Database Access

Connect to PostgreSQL:
```bash
docker compose exec db psql -U postgres -d todoappdb
```

## Development

For development with auto-reload:
```bash
docker compose up --build
```

The application code is mounted as a volume for live editing.

## Docker Hub Rate Limits

If you encounter "Too Many Requests" errors:
- Wait 6 hours for rate limit reset, OR
- Login to Docker Hub: `docker login`

## Files Structure

- `Dockerfile` - Application container
- `docker-compose.yml` - Services configuration
- `requirements.txt` - Python dependencies
- `todoApp/` - FastAPI application code