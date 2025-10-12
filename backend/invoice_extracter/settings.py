"""
Django settings for invoice_extractor project.

This is like the "CONFIGURATION MANUAL" for our Django project.
It tells Django how to behave - where files are, what apps to use, database info, etc.
"""
from pathlib import Path

# BASE_DIR = The root directory of our project (backend/invoice_extractor)
# This helps us build paths that work on any computer
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: A secret key for cryptographic signing
# In production, this should be a long, random string and kept secret!
SECRET_KEY = 'temp-key-change-in-production'

# DEBUG: When True, shows detailed error pages. Turn OFF in production!
DEBUG = True

# ALLOWED_HOSTS: Which domain names this Django site can serve
# For now, empty = only localhost
ALLOWED_HOSTS = []

# INSTALLED_APPS: Which "components" Django should use
# Think of apps like "plugins" or "modules" in our project
INSTALLED_APPS = [
    'django.contrib.auth',         # Handles user authentication
    'django.contrib.contenttypes', # Tracks database models
    'django.contrib.sessions',     # Manages user sessions
    'django.contrib.messages',     # Handles flash messages
    'django.contrib.staticfiles',  # Serves CSS, JS, images
    'rest_framework',              # Django REST Framework for APIs
]

# MIDDLEWARE: "Processing layers" that handle requests/responses
# Like security checks, session management, etc.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',           # Security headers
    'django.contrib.sessions.middleware.SessionMiddleware',    # User sessions
    'django.middleware.common.CommonMiddleware',               # URL processing
    'django.middleware.csrf.CsrfViewMiddleware',               # CSRF protection
    'django.contrib.auth.middleware.AuthenticationMiddleware', # User auth
    'django.contrib.messages.middleware.MessageMiddleware',    # Message handling
]

# ROOT_URLCONF: Which file contains the main URL routing
ROOT_URLCONF = 'invoice_extractor.urls'

# DATABASES: Database configuration
# We start with SQLite (file-based) for simplicity
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Database type
        'NAME': BASE_DIR / 'db.sqlite3',         # Database file location
    }
}

# INTERNATIONALIZATION: Language and timezone settings
LANGUAGE_CODE = 'en-us'      # English
TIME_ZONE = 'UTC'            # Universal Time Coordinated
USE_I18N = True              # Enable internationalization
USE_TZ = True                # Use timezone-aware datetimes

# STATIC FILES: CSS, JavaScript, images
STATIC_URL = 'static/'

# DEFAULT PRIMARY KEY: Type of primary key for models
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'