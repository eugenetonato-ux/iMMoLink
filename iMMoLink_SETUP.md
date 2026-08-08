# iMMoLink — Mise en place du projet (Windows / PowerShell)

Ce guide applique l'architecture définie dans `iMMoLink_skills-app.md` (apps, flux locataire/propriétaire/admin, authentification Google OAuth + admin séparé) et suit ton workflow habituel.

---

## 1. Création du dossier et de l'environnement virtuel

```powershell
mkdir iMMoLink
cd iMMoLink
python -m venv env
env\Scripts\activate
```

Tu dois voir `(env)` apparaître devant ton prompt avant de continuer.

---

## 2. Installation des dépendances

```powershell
python -m pip install --upgrade pip

pip install django
pip install djangorestframework
pip install django-filter
pip install requests
pip install python-dotenv
pip install python-decouple
pip install django-cors-headers
pip install pillow

# Authentification Google OAuth
pip install django-allauth

# Export PDF/CSV des transactions (admin)
pip install reportlab

# Traitement asynchrone (notifications email, tâches différées)
pip install celery
pip install redis

# Base de données (SQLite en Phase 1, PostgreSQL prêt pour plus tard)
pip install psycopg2-binary

# Qualité de code
pip install black isort flake8
pip install pytest pytest-django factory-boy
```

Génère ton `requirements.txt` :

```powershell
pip freeze > requirements.txt
```

---

## 3. Démarrage du projet Django

```powershell
django-admin startproject config .
```

## 4. Création du dossier `apps/` et des applications

```powershell
mkdir apps
New-Item -Path apps\__init__.py -ItemType File

mkdir apps\accounts, apps\properties, apps\locations, apps\favorites, apps\payments, apps\notifications, apps\adminpanel, apps\api, apps\common, apps\website

python manage.py startapp accounts apps/accounts
python manage.py startapp properties apps/properties
python manage.py startapp locations apps/locations
python manage.py startapp favorites apps/favorites
python manage.py startapp payments apps/payments
python manage.py startapp notifications apps/notifications
python manage.py startapp adminpanel apps/adminpanel
python manage.py startapp api apps/api
python manage.py startapp common apps/common
python manage.py startapp website apps/website
```

### Corriger le `name` de chaque app

```python
# apps/properties/apps.py
from django.apps import AppConfig

class PropertiesConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.properties"   # ⚠️ à corriger dans chacune des 10 apps
```

Répète cette correction (`name = "apps.<nom_app>"`) dans les 10 fichiers `apps.py`.

---

## 5. Création des dossiers `templates/` et `static/`

```powershell
mkdir templates
mkdir templates\Base
mkdir templates\Website
mkdir templates\Tenant
mkdir templates\Owner
mkdir templates\Admin
mkdir templates\Emails

type nul > templates\Base\base.html
type nul > templates\Base\base_dashboard.html
type nul > templates\Website\home.html
type nul > templates\Website\recherche.html
type nul > templates\Website\annonce_detail.html
type nul > templates\Tenant\dashboard.html
type nul > templates\Tenant\favoris.html
type nul > templates\Owner\dashboard.html
type nul > templates\Owner\annonce_form.html
type nul > templates\Admin\dashboard.html
type nul > templates\Admin\annonces.html
type nul > templates\Admin\utilisateurs.html
type nul > templates\Admin\transactions.html

mkdir static\css, static\js, static\images, static\vendor
New-Item -Path static\css\style.css -ItemType File
New-Item -Path static\css\dashboard.css -ItemType File
New-Item -Path static\js\script.js -ItemType File
New-Item -Path static\js\recherche.js -ItemType File

mkdir media
mkdir media\properties, media\profiles

mkdir logs
mkdir backups
mkdir scripts
mkdir docs
```

---

## 6. Fichier `.env` (racine du projet)

```powershell
New-Item -Path .env -ItemType File
```

Contenu de `.env` :

```
DEBUG=True
SECRET_KEY=change-moi-en-production
ALLOWED_HOSTS=127.0.0.1,localhost

PLATFORM_NAME=iMMoLink
CURRENCY=XOF
COUNTRY=Benin

# Google OAuth
GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

# Admin séparé (jamais un compte utilisateur classique)
ADMIN_URL_PATH=cpanel_administrateur
ADMIN_USERNAME=
ADMIN_PASSWORD=

# Paiement (Sebpay - Moov Money / MTN Money)
SEBPAY_API_KEY=
SEBPAY_API_SECRET=
SEBPAY_CALLBACK_SECRET=

# Frais de contact par défaut (surchargé en base par l'admin)
DEFAULT_CONTACT_FEE=1000

# Email admin (mot de passe d'application Gmail)
DEFAULT_FROM_EMAIL=noreply@iMMoLink.app
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ADMIN_NOTIFICATION_EMAIL=
```

Ajoute `.env` dans `.gitignore` :

```powershell
New-Item -Path .gitignore -ItemType File
Add-Content .gitignore "env/`n.env`n__pycache__/`n*.pyc`nmedia/`ndb.sqlite3`nlogs/"
```

---

## 7. Configuration `config/settings.py`

### a) Imports en haut du fichier

```python
from pathlib import Path
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent
```

### b) Variables sensibles depuis `.env`

```python
SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="").split(",")
CURRENCY = config("CURRENCY", default="XOF")
PLATFORM_NAME = config("PLATFORM_NAME", default="iMMoLink")
ADMIN_URL_PATH = config("ADMIN_URL_PATH", default="cpanel_administrateur")
```

### c) `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Tiers
    "rest_framework",
    "corsheaders",
    "django_filters",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",

    # Apps iMMoLink
    "apps.accounts",
    "apps.properties",
    "apps.locations",
    "apps.favorites",
    "apps.payments",
    "apps.notifications",
    "apps.adminpanel",
    "apps.api",
    "apps.common",
    "apps.website",
]

SITE_ID = 1
```

### d) `MIDDLEWARE`

```python
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

### e) Authentification (Google OAuth pour locataires/propriétaires — admin séparé)

```python
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/compte/connexion/"
LOGIN_REDIRECT_URL = "/compte/choix-role/"
LOGOUT_REDIRECT_URL = "/"

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": ["profile", "email"],
        "AUTH_PARAMS": {"access_type": "online"},
    }
}
```

> Rappel : `role` (locataire/propriétaire) est choisi **après** la connexion Google, jamais `admin`. L'espace admin (`/cpanel_administrateur/`) utilise une vue de connexion dédiée, séparée du système `allauth`, vérifiant `ADMIN_USERNAME`/`ADMIN_PASSWORD` ou un modèle admin distinct.

### f) Templates

```python
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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
```

### g) Static / Media

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### h) Base de données (SQLite en Phase 1, PostgreSQL prêt pour plus tard)

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

### i) Django REST Framework

```python
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
}
```

---

## 8. Configuration `config/urls.py`

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from decouple import config

ADMIN_URL_PATH = config("ADMIN_URL_PATH", default="cpanel_administrateur")

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("api/v1/", include("apps.api.urls")),
    path("", include("apps.website.urls")),
    path("espace-locataire/", include("apps.accounts.urls_tenant")),
    path("espace-proprietaire/", include("apps.accounts.urls_owner")),
    path(f"{ADMIN_URL_PATH}/", include("apps.adminpanel.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## 9. Migrations et compte administrateur

```powershell
python manage.py makemigrations
python manage.py migrate
```

> ⚠️ L'administrateur n'est **pas** créé via `createsuperuser` classique lié à un rôle sélectionnable — il est soit défini en `.env` (`ADMIN_USERNAME`/`ADMIN_PASSWORD`), soit créé directement en base par un script dédié (`scripts/create_admin.py`), jamais via une inscription publique.

```powershell
python manage.py shell -c "from apps.accounts.models import User; print(User.objects.filter(role='admin').count())"
```

**Supprimer un compte admin (si besoin, en environnement de dev uniquement) :**

```powershell
python manage.py shell -c "from apps.accounts.models import User; User.objects.filter(role='admin').delete()"
```

⚠️ Vérifie toujours qu'il reste au moins un accès admin avant suppression.

```powershell
celery -A config worker --loglevel=info --pool=solo
```

---

## 10. Lancement du serveur

```powershell
python manage.py runserver
```

- Site public : `http://127.0.0.1:8000/`
- Espace locataire : `http://127.0.0.1:8000/espace-locataire/`
- Espace propriétaire : `http://127.0.0.1:8000/espace-proprietaire/`
- Espace admin : `http://127.0.0.1:8000/cpanel_administrateur/`

---

## 11. Ordre de développement recommandé (Phase 1)

1. `apps/accounts` — modèle `User` + Google OAuth (allauth) + choix de rôle + `OwnerProfile`/`TenantProfile`
2. `apps/locations` — villes, quartiers du Bénin
3. `apps/properties` — modèles `Property`, `PropertyImage`, `Amenity` + création d'annonce (propriétaire)
4. `apps/website` — site public (accueil, recherche, fiche annonce)
5. `apps/adminpanel` — authentification admin séparée + validation des annonces
6. `apps/favorites` — favoris locataire
7. `apps/payments` — intégration Sebpay + `ContactUnlock`
8. `apps/notifications` — emails admin (nouvelle inscription, nouvelle annonce)

---

## 12. Commandes utiles (rappel de ton workflow)

```powershell
# Vérifier les utilisateurs enregistrés par rôle
python manage.py shell
>>> from apps.accounts.models import User
>>> User.objects.filter(role="proprietaire").count()
>>> User.objects.filter(role="locataire").count()
>>> exit()

# Mise à jour GitHub
git status
git add .
git commit -m "mise a jour"
git push origin main
```
