import os
from pathlib import Path

# Load environment variables from .env file in development
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # python-dotenv is optional for production
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings from environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'replace-me-in-production')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes', 'on')

# Parse ALLOWED_HOSTS from comma-separated string
allowed_hosts_str = os.environ.get('ALLOWED_HOSTS', '127.0.0.1,localhost')
ALLOWED_HOSTS = [host.strip() for host in allowed_hosts_str.split(',') if host.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    # تطبيقات المشروع
    'accounts',
    'dashboard',
    'offers',
    'orders',
    'products',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # مطلوب للسلة
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'atlasly.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # إن كان لديك مجلد templates عام
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                # إشعارات الجرس + عداد السلة
                'core.context_processors.notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'atlasly.wsgi.application'

# Database configuration with environment variables and SQLite fallback
MYSQL_ENGINE = os.environ.get('MYSQL_ENGINE')

if MYSQL_ENGINE == 'django.db.backends.mysql':
    # MySQL configuration from environment variables
    DATABASES = {
        'default': {
            'ENGINE': MYSQL_ENGINE,
            'NAME': os.environ.get('MYSQL_NAME', 'atlasly_db'),
            'USER': os.environ.get('MYSQL_USER', 'root'),
            'PASSWORD': os.environ.get('MYSQL_PASSWORD', ''),
            'HOST': os.environ.get('MYSQL_HOST', 'localhost'),
            'PORT': os.environ.get('MYSQL_PORT', '3306'),
            'OPTIONS': {
                'charset': 'utf8mb4',
                'use_unicode': True,
            }
        }
    }
else:
    # Default to SQLite for development
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# تحققات كلمات المرور
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# اللغة والمنطقة
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# الملفات الثابتة
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'core' / 'static',  # حيث يوجد static الخاص بك
]
# إن أردت استخدام collectstatic للإنتاج:
# STATIC_ROOT = BASE_DIR / 'staticfiles'

# الوسائط (الصور)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# إعدادات الدخول والخروج
LOGIN_URL = 'accounts:login'
# مهم: اجعل إعادة التوجيه بعد تسجيل الدخول للواجهة العامة حتى لا يفتح لوحة التحكم لكل المستخدمين
LOGIN_REDIRECT_URL = 'home'
LOGOUT_REDIRECT_URL = 'home'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# حدّ المخزون المنخفض الذي يولّد إشعار
LOW_STOCK_THRESHOLD = 5