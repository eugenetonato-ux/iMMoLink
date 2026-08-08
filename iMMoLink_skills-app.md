# iMMoLink — Cahier des Charges Technique & Guide de Développement

**Stack technologique** : Django 5+ / Django REST Framework / PostgreSQL / Redis / Celery / django-allauth (Google OAuth)
**Objectif** : Plateforme web de location immobilière au Bénin — mise en relation propriétaires / locataires, avec site public, espace locataire, espace propriétaire, et espace administrateur totalement séparé.
**Authentification** :
- Site public : accès libre à la recherche et aux fiches annonces validées, sans compte.
- Locataires & propriétaires : **Google OAuth uniquement**, choix du rôle après connexion.
- Administrateur : authentification **séparée et sécurisée**, accessible uniquement via `/cpanel_administrateur/`, jamais attribuable via une sélection de rôle utilisateur.

---

## 🛠️ 1. Installation & Configuration Initiale

```bash
django-admin startproject config iMMoLink
cd iMMoLink
python -m venv venv && source venv/bin/activate
```

### Dépendances principales

```bash
pip install django djangorestframework django-filter django-allauth python-decouple pillow \
  reportlab psycopg2-binary django-cors-headers django-extensions \
  whitenoise gunicorn requests ipython pytest pytest-django factory-boy black isort flake8

pip install celery redis
```

### Variables d'environnement (`.env`)

```
DEBUG=False
SECRET_KEY=
DATABASE_URL=
REDIS_URL=

PLATFORM_NAME=iMMoLink
CURRENCY=XOF
COUNTRY=Benin

GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=

ADMIN_URL_PATH=cpanel_administrateur
ADMIN_USERNAME=
ADMIN_PASSWORD=

SEBPAY_API_KEY=
SEBPAY_API_SECRET=
SEBPAY_CALLBACK_SECRET=
DEFAULT_CONTACT_FEE=1000

DEFAULT_FROM_EMAIL=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
ADMIN_NOTIFICATION_EMAIL=
```

---

## 🏗️ 2. Architecture des dossiers

```
iMMoLink/
│
├── manage.py
├── requirements.txt
├── .env
├── .gitignore
│
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── celery.py
│
├── apps/
│   ├── accounts/             # User, rôles, OwnerProfile, TenantProfile, Google OAuth
│   ├── properties/           # Annonces, photos, équipements, validation
│   ├── locations/            # Villes, quartiers du Bénin
│   ├── favorites/            # Favoris locataire
│   ├── payments/             # Transactions Sebpay, ContactUnlock
│   ├── notifications/        # Emails (admin, locataire, propriétaire)
│   ├── adminpanel/           # Auth admin séparée, validation, logs, statistiques
│   ├── api/                  # API REST v1
│   ├── common/                # Utilitaires partagés
│   └── website/                # Site public (accueil, recherche, fiche annonce)
│
├── templates/
├── static/
├── media/
└── docs/
```

### Détail des apps critiques

**`accounts/`** : `User` (email, prénom, nom, photo, `role` parmi `locataire`/`proprietaire`/`admin` — `admin` jamais assignable depuis le front), `OwnerProfile` (WhatsApp, ville, quartier, adresse, photo de profil obligatoire uploadée manuellement), `TenantProfile`. Connexion via Google OAuth (`django-allauth`), sélection du rôle **après** la première connexion.

**`properties/`** : `Property` (titre, description, type, prix, périodicité, caution, ville/quartier, statut), `PropertyImage` (galerie, ordre, photo principale), `Amenity`/`PropertyAmenity` (équipements). Workflow de statut strict : `brouillon → en_attente_validation → validee → publiee` (+ `refusee`, `suspendue`, `louee`). Une annonce n'est visible publiquement qu'au statut `publiee`.

**`payments/`** : `Payment` (montant, référence unique, utilisateur, annonce, propriétaire, statut, méthode via Sebpay), `ContactUnlock` (lien 1-1 entre un `Payment` réussi, un locataire et une annonce). Le contact n'est débloqué qu'après confirmation du webhook Sebpay — jamais sur une simple tentative.

**`locations/`** : référentiel des villes et quartiers du Bénin utilisé par la recherche et la création d'annonce.

**`adminpanel/`** : authentification admin séparée (indépendante d'`allauth`), validation/refus/suspension des annonces, gestion des utilisateurs et propriétaires vérifiés, consultation des transactions, `AdminLog` (append-only), `VerificationRequest`.

---

## 🔄 3. Flux clés de la plateforme

### Côté locataire
```
Accueil
   ↓
Recherche (ville, quartier, type, prix, chambres, disponibilité)
   ↓
Consultation d'une fiche annonce (contact masqué)
   ↓
"Contacter le propriétaire"
   ↓
Connexion Google (si nécessaire) → choix du rôle locataire
   ↓
Paiement des frais de mise en relation (1000 XOF via Sebpay)
   ↓
Confirmation réelle du paiement (webhook)
   ↓
Déblocage du contact (WhatsApp / téléphone)
   ↓
Contact du propriétaire via WhatsApp (message préformaté)
```

### Côté propriétaire
```
Accueil
   ↓
"Publier un logement"
   ↓
Connexion Google → choix du rôle propriétaire
   ↓
Complétion du profil (WhatsApp, ville, quartier, adresse, photo obligatoire)
   ↓
Création d'une annonce (description, prix, périodicité, caution, photos)
   ↓
Envoi pour validation (statut en_attente_validation)
   ↓
Email automatique à l'admin (nouvelle annonce à valider)
   ↓
Validation / refus / demande de modification par l'admin
   ↓
Publication (visible publiquement)
```

### Côté administrateur
```
Connexion sécurisée séparée (/cpanel_administrateur/, username + mot de passe .env)
   ↓
Dashboard global (utilisateurs, annonces, transactions, revenus)
   ↓
Validation des propriétaires et des annonces
   ↓
Gestion des utilisateurs (suspendre / réactiver / supprimer)
   ↓
Gestion des transactions (export CSV/PDF)
   ↓
Configuration des paramètres (frais de contact, villes, quartiers, méthodes de paiement)
   ↓
Consultation des logs et de l'activité suspecte
```

---

## 📊 4. Modèles de données (extraits clés)

### `User` (accounts)
```python
class User(AbstractUser):
    ROLE_CHOICES = [("locataire", "Locataire"), ("proprietaire", "Propriétaire"), ("admin", "Administrateur")]
    email = models.EmailField(unique=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True)
    # role="admin" n'est jamais définissable via une vue publique/API — uniquement via script/DB
```

### `OwnerProfile` (accounts)
```python
class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    whatsapp = models.CharField(max_length=30)
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, blank=True)
    photo_profil = models.ImageField(upload_to="profiles/owners/")  # upload manuel obligatoire
    verifie = models.BooleanField(default=False)
```

### `Property` (properties)
```python
class Property(models.Model):
    TYPE_CHOICES = [("chambre", "Chambre"), ("studio", "Studio"), ("appartement", "Appartement"),
                     ("maison", "Maison"), ("villa", "Villa"), ("autre", "Autre")]
    PERIOD_CHOICES = [("mensuel", "Mensuel"), ("trimestriel", "Trimestriel"), ("annuel", "Annuel")]
    STATUT_CHOICES = [("brouillon", "Brouillon"), ("en_attente_validation", "En attente de validation"),
                       ("validee", "Validée"), ("publiee", "Publiée"), ("refusee", "Refusée"),
                       ("suspendue", "Suspendue"), ("louee", "Louée")]

    proprietaire = models.ForeignKey("accounts.OwnerProfile", on_delete=models.CASCADE)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type_logement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    prix = models.DecimalField(max_digits=12, decimal_places=0)  # XOF
    periodicite = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    caution = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True)
    ville = models.CharField(max_length=100)
    quartier = models.CharField(max_length=100)
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default="brouillon")
    disponibilite = models.CharField(max_length=30, default="disponible")
    created_at = models.DateTimeField(auto_now_add=True)
```

### `Payment` (payments)
```python
class Payment(models.Model):
    STATUT_CHOICES = [("pending", "En attente"), ("successful", "Réussi"),
                       ("failed", "Échoué"), ("cancelled", "Annulé"), ("refunded", "Remboursé")]

    locataire = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    annonce = models.ForeignKey("properties.Property", on_delete=models.PROTECT)
    proprietaire = models.ForeignKey("accounts.OwnerProfile", on_delete=models.PROTECT)
    montant = models.DecimalField(max_digits=10, decimal_places=0)  # XOF
    reference = models.CharField(max_length=64, unique=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="pending")
    methode = models.CharField(max_length=30, blank=True)  # moov_money / mtn_money
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
```

### `ContactUnlock` (payments)
```python
class ContactUnlock(models.Model):
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT)
    locataire = models.ForeignKey("accounts.User", on_delete=models.CASCADE)
    annonce = models.ForeignKey("properties.Property", on_delete=models.CASCADE)
    unlocked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("locataire", "annonce")
```

### `AdminLog` (adminpanel)
```python
class AdminLog(models.Model):
    admin = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)  # validation_annonce, suspension_compte, etc.
    cible = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # append-only : aucune vue d'édition/suppression exposée
```

---

## 🧠 5. Règles de développement (à respecter strictement)

- ❌ **INTERDIT** : logique métier dans les vues — tout passe par `services.py` de chaque app.
- ❌ **INTERDIT** : attribuer le rôle `admin` depuis une vue, un formulaire ou l'API — uniquement en base ou via un admin existant.
- ❌ **INTERDIT** : exposer le WhatsApp/téléphone du propriétaire dans une fiche annonce publique tant qu'un `ContactUnlock` valide n'existe pas pour ce locataire.
- ❌ **INTERDIT** : débloquer un contact sur un statut `pending` — uniquement sur `successful` confirmé par webhook signé.
- ❌ **INTERDIT** : publier une annonce sans validation admin explicite.
- ✅ **OBLIGATOIRE** : le montant des frais de contact est lu depuis la configuration plateforme, jamais codé en dur.
- ✅ **OBLIGATOIRE** : chaque webhook de paiement est traité de façon idempotente (pas de double déblocage/double log).
- ✅ **OBLIGATOIRE** : toute action admin sensible (validation, suspension, changement de paramètre) est journalisée dans `AdminLog`.
- ✅ **OBLIGATOIRE** : les frais de mise en relation, la réservation et un futur paiement de loyer restent des modules distincts et indépendants.

---

## 🚀 6. Checklist de développement

### Phase 1 — Socle fonctionnel
- [ ] Initialiser le projet Django + apps (`accounts`, `properties`, `locations`, `favorites`, `payments`, `notifications`, `adminpanel`, `api`, `common`, `website`)
- [ ] Google OAuth (django-allauth) + choix de rôle post-connexion
- [ ] Authentification admin séparée (`/cpanel_administrateur/`)
- [ ] Modèles `User`, `OwnerProfile`, `TenantProfile`, `Property`, `PropertyImage`, `Amenity`, `Location`
- [ ] Site public : recherche, filtres, fiche annonce (contact masqué)
- [ ] Espace propriétaire : création d'annonce + upload photos + envoi validation
- [ ] Espace admin : validation/refus/suspension des annonces et des propriétaires
- [ ] Favoris locataire

### Phase 2 — Paiement & contact
- [ ] Intégration Sebpay (Moov Money / MTN Money) — création de transaction
- [ ] Webhook de confirmation signé + `ContactUnlock`
- [ ] Déblocage du WhatsApp + lien de contact préformaté
- [ ] Dashboard admin : transactions, revenus, export CSV/PDF
- [ ] Notifications email (nouvelle inscription propriétaire, nouvelle annonce, paiement confirmé)

### Phase 3 — Évolutions futures
- [ ] Paiement du loyer entre propriétaire et locataire (module distinct)
- [ ] Réservation de logement avec dépôt de garantie
- [ ] Vérification renforcée des propriétaires (badge "Propriétaire vérifié")
- [ ] Carte interactive et recherche "autour de moi"
- [ ] Visite virtuelle / vidéo
