"""
Django settings for the box_selector project.

This is a small hiring-assignment project. Settings are kept intentionally
minimal - only what is needed to run the app, the admin site (useful for
manually inspecting/entering data) and the test suite.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# NOTE: This key is fine for a local hiring-assignment project. It would
# need to be replaced with a secret, environment-provided value for any
# real deployment. Not a concern for this assignment's scope.
SECRET_KEY = "django-insecure-hiring-assignment-secret-key-do-not-use-in-production"

DEBUG = True

ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "boxes",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "box_selector.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "box_selector.wsgi.application"

# SQLite is used for simplicity. This is an explicit assumption documented
# in README.md - appropriate for a small hiring assignment, not intended
# to imply a production database choice.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Authentication is not part of this assignment's requirements, so password
# validators are left at Django's default empty behaviour is not used here;
# the list is left empty deliberately since no user-facing auth/signup
# exists in this project.
AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
