# Test settings for development
from .settings import *

# Use SQLite for testing instead of MySQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

# Disable MySQL-specific dependencies for testing
# INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'pymysql']

DEBUG = True
ALLOWED_HOSTS = ['*']