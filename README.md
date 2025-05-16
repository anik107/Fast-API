# FastAPI Todo Application

A robust Todo application built with FastAPI, SQLAlchemy, Jinja2 templates, and PostgreSQL, featuring user authentication, role-based access control, and comprehensive API endpoints.

## Features

- User registration and authentication with JWT
- Role-based access control (admin and regular users)
- CRUD operations for todo items
- Web interface using Jinja2 templates and Bootstrap
- RESTful API endpoints
- Database migrations using Alembic
- Comprehensive test suite

## Prerequisites

- Python 3.12+
- PostgreSQL
- Virtual environment tool (venv, virtualenv, etc.)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd fastapi
```

### 2. Set up a virtual environment

```bash
python -m venv fastapienv
source fastapienv/bin/activate  # On Windows: fastapienv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If the requirements.txt file doesn't exist, you can create one with the following dependencies:

```
fastapi>=0.110.0
uvicorn>=0.29.0
sqlalchemy>=2.0.27
pydantic>=2.6.1
alembic>=1.13.1
psycopg2-binary>=2.9.9
passlib>=1.7.4
python-jose>=3.3.0
python-multipart>=0.0.9
jinja2>=3.1.3
pytest>=8.3.5
httpx>=0.27.0
python-dotenv>=1.0.0
email-validator>=2.1.0
starlette>=0.36.1
```

### 4. Set up the database

1. Create a PostgreSQL database:

```bash
sudo -u postgres psql
postgres=# CREATE DATABASE todoAppdb;
postgres=# CREATE USER postgres WITH PASSWORD 'postgres';
postgres=# GRANT ALL PRIVILEGES ON DATABASE todoAppdb TO postgres;
postgres=# \q
```

2. Configure the database connection in `todoApp/database.py`:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:5432/todoAppdb'
```

You can modify this connection string according to your database configuration.

3. Run database migrations:

```bash
cd todoApp
alembic upgrade head
```

## Running the Application

1. Start the application:

```bash
cd /home/cg/Documents/Workspace/fastapi
uvicorn todoApp.main:app --reload
```

2. Access the application:
   - Web Interface: http://localhost:8000/
   - API Documentation: http://localhost:8000/docs or http://localhost:8000/redoc

## Project Structure

```
todoApp/
├── __init__.py
├── alembic.ini          # Alembic configuration
├── database.py          # Database connection and session management
├── main.py              # Application entry point
├── models.py            # SQLAlchemy models
├── alembic/             # Database migration files
├── routers/             # API routes
│   ├── __init__.py
│   ├── admin.py         # Admin routes
│   ├── auth.py          # Authentication routes
│   ├── todos.py         # Todo CRUD operations
│   └── users.py         # User management routes
├── static/              # Static files (CSS, JS)
│   ├── css/
│   └── js/
├── templates/           # Jinja2 HTML templates
└── test/                # Test suite
```

## API Endpoints

### Authentication

- `POST /auth/token`: Get access token (login)
- `GET /auth/login`: Login page
- `POST /auth/register`: Register a new user
- `GET /auth/register`: Registration page

### Todo Items

- `GET /todos/`: Get all todos
- `POST /todos/`: Create a new todo
- `GET /todos/{todo_id}`: Get a specific todo
- `PUT /todos/{todo_id}`: Update a todo
- `DELETE /todos/{todo_id}`: Delete a todo
- `GET /todos/todo-page`: Todo web interface

### User Management

- `GET /user/`: Get user information
- `PUT /user/password`: Change password
- `PUT /user/phoneNumber/{phone_number}`: Add/update phone number

### Admin

- `GET /admin/`: Admin dashboard
- `DELETE /admin/todo/{todo_id}`: Delete any todo (admin only)

## Running Tests

```bash
cd /home/cg/Documents/Workspace/fastapi
pytest -v
```

## Database Migrations

When making changes to the database models:

```bash
cd todoApp
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

## Environment Variables

For production, consider moving sensitive information to environment variables:

```python
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/todoAppdb")
```

## License

[MIT](LICENSE)

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request
