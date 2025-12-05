"""
Django settings for lms_final project - PRODUCCIÓN HESTIA CP
"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- SEGURIDAD ---
# ADVERTENCIA: Mantén esta clave secreta en producción.
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-pon-tu-clave-aqui')

# IMPORTANTE: False para producción en Hestia
DEBUG = os.getenv('DEBUG', 'False') == 'True'

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'aquienpasco.lat,www.aquienpasco.lat,51.222.156.179,localhost,127.0.0.1').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', 'https://aquienpasco.lat,https://www.aquienpasco.lat').split(',')

# Configuración de seguridad para producción
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_REFERRER_POLICY = 'same-origin'
    X_FRAME_OPTIONS = 'DENY'
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True

# --- APPS ---
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    # Third party apps
    'rest_framework',
    'corsheaders',
    'tinymce',
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
    'crispy_forms',
    'crispy_bootstrap5',
    # My apps
    'academy',
    'rest_framework.authtoken',
]

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# --- MIDDLEWARE ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware', # CORS va antes de Common
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'lms_final.urls'

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
                'academy.context_processors.notifications_processor', # Tu processor de notificaciones
            ],
        },
    },
]

WSGI_APPLICATION = 'lms_final.wsgi.application'

# --- DATABASE ---
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
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

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'es-pe'
TIME_ZONE = 'America/Lima'
USE_I18N = True
USE_TZ = True

# --- STATIC & MEDIA FILES (Configuración HestiaCP) ---
# URL para acceder a los estáticos desde el navegador
STATIC_URL = '/static/'

# Carpeta física donde collectstatic recopilará los archivos (Coincide con tu nginx location)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Archivos subidos por el usuario
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- REST FRAMEWORK CONFIG ---
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ]
}

# --- EXTRAS ---
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Seguridad CORS
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_ALL_ORIGINS = False
    CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

LOGIN_REDIRECT_URL = 'academy:dashboard'
LOGOUT_REDIRECT_URL = 'academy:login'

# Asegúrate también de que LOGIN_URL tenga el mismo formato si lo agregaste:
LOGIN_URL = 'academy:login'

# --- AUTHENTICATION ---
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]
SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': [
            'profile',
            'email',
        ],
        'AUTH_PARAMS': {
            'access_type': 'online',
        },
        'OAUTH_PKCE_ENABLED': True,
    }
}
ACCOUNT_ADAPTER = 'academy.adapters.MyAccountAdapter'
SOCIALACCOUNT_ADAPTER = 'academy.adapters.MySocialAccountAdapter'
ACCOUNT_EMAIL_VERIFICATION = 'none'

# --- EMAIL CONFIGURATION (Producción) ---
# Si no tienes SMTP configurado aún, mantén la consola para evitar errores 500,
# pero en producción deberías cambiar esto a SMTP.
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# --- TINYMCE CONFIGURATION ---
TINYMCE_DEFAULT_CONFIG = {
    'height': 360,
    'width': '100%',
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 20,
    'selector': 'textarea',
    'theme': 'silver',
    'license_key': 'gpl',
    'plugins': '''
        save link image media preview codesample
        table code lists fullscreen insertdatetime nonbreaking
        directionality searchreplace wordcount visualblocks
        visualchars code fullscreen autolink lists charmap
        anchor pagebreak
        ''',
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

SOCIALACCOUNT_LOGIN_ON_GET = True