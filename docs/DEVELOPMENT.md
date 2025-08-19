# AtlasLIBYA Development Setup

This guide provides step-by-step instructions for setting up the AtlasLIBYA development environment on Windows (PowerShell), macOS, and Linux.

## Prerequisites

- Python 3.8 or higher
- Git
- MySQL (optional - for production-like setup)
- VS Code (recommended)

## Quick Setup

### 1. Clone and Navigate to Project
```bash
git clone https://github.com/sulima2901/AtlasLIBYA.git
cd AtlasLIBYA
```

### 2. Create Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure VS Code Interpreter
1. Open VS Code in the project directory: `code .`
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
3. Type "Python: Select Interpreter"
4. Choose the interpreter from your `.venv` directory:
   - Windows: `.venv\Scripts\python.exe`
   - macOS/Linux: `.venv/bin/python`

This resolves Pylance import warnings for PyMySQL and other dependencies.

### 5. Database Setup

#### Option A: SQLite (Default - Recommended for Development)
The project uses SQLite by default. No additional configuration needed.

```bash
python manage.py makemigrations
python manage.py migrate
```

#### Option B: MySQL (Optional - Production-like Setup)
1. Install MySQL and create a database
2. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
3. Edit `.env` and uncomment/configure MySQL settings:
   ```
   MYSQL_ENGINE=django.db.backends.mysql
   MYSQL_NAME=atlasly_db
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   ```
4. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### 6. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to see your application.

## Environment Variables

Create a `.env` file based on `.env.example` to customize:

- `SECRET_KEY`: Django secret key (change for production)
- `DEBUG`: Set to `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `MYSQL_*`: MySQL database configuration (optional)

## Troubleshooting

### PyMySQL Import Warnings in VS Code
- Ensure you've selected the correct Python interpreter (`.venv`)
- Run `pip install -r requirements.txt` in your virtual environment
- Restart VS Code after changing the interpreter

### Database Connection Issues
- For SQLite: Check file permissions and disk space
- For MySQL: Verify connection settings and database exists

### Port Already in Use
```bash
python manage.py runserver 8001  # Use different port
```

## Production Deployment Notes

1. Set `DEBUG=False` in environment
2. Use a strong, unique `SECRET_KEY`
3. Configure `ALLOWED_HOSTS` for your domain
4. Use MySQL or PostgreSQL instead of SQLite
5. Set up proper static file serving
6. Consider using environment-specific settings files

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests: `python manage.py test`
4. Submit a pull request

For questions or issues, please create an issue in the GitHub repository.