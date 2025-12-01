"""
Django settings for lms_final project - PRODUCCIÓN (LMP4)
"""
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD ---
SECRET_KEY = 'django-insecure-pon-tu-clave-aqui' 
DEBUG = False  # Apagado para producción
ALLOWED_HOSTS = ['aquienpasco.lat', 'www.aquienpasco.lat', '51.222.156.179', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = ['https://aquienpasco.lat', 'https://www.aquienpasco.lat']

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'tinymce',
    'academy',
]

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lms_final.urls'

# --- TEMPLATES (Con tus Notificaciones) ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'academy.context_processors.notifications_processor', # <--- AQUÍ ESTÁ
            ],
        },
    },
]

WSGI_APPLICATION = 'lms_final.wsgi.application'

# --- DATABASE ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# --- PASSWORD VALIDATION ---
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]

# --- INT. ---
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA ---
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- EXTRAS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
CORS_ALLOW_ALL_ORIGINS = True
LOGIN_REDIRECT_URL = 'academy:dashboard'
LOGOUT_REDIRECT_URL = 'login'

# --- TINYMCE ---
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'license_key': 'gpl',  # <--- ESTO QUITA EL AVISO DE EVALUACIÓN
    # Plugins actualizados (se eliminaron textcolor, contextmenu, print, hr)
    'plugins': '''
        save link image media preview codesample
        table code lists fullscreen insertdatetime nonbreaking
        directionality searchreplace wordcount visualblocks
        visualchars code fullscreen autolink lists charmap
        anchor pagebreak
        ''',
    # Toolbar actualizada
    'toolbar1': '''
        fullscreen preview bold italic underline | fontselect
        fontsizeselect | forecolor backcolor | alignleft alignright
        aligncenter alignjustify | indent outdent | bullist numlist table
        | link image media | codesample
        ''',
    'toolbar2': '''
        visualblocks visualchars |
        charmap pagebreak nonbreaking anchor | code
        ''',
    'contextmenu': 'formats | link image',
    'menubar': True,
    'statusbar': True,
}