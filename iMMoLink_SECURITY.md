# iMMoLink — SECURITY.md

## Objectif

Ce document définit les règles de sécurité à appliquer tout au long du développement d'**iMMoLink**, une plateforme web de location immobilière développée avec **Django, Django REST Framework, PostgreSQL, Redis/Celery**, mettant en relation propriétaires et locataires au Bénin, avec authentification Google OAuth côté utilisateurs et un espace administrateur totalement séparé (`cpanel_administrateur`).

---

# Rôle de l'auditeur IA

Tu agis comme un **Architecte Sécurité Senior** spécialisé dans Django, DRF, PostgreSQL, OAuth2, et les plateformes marketplace avec paiement en ligne.

Le projet est supposé avoir été développé avec l'aide d'IA (ChatGPT, Claude, Cursor, Copilot, etc.).

Tu dois :

- analyser l'intégralité de la base de code ;
- comprendre l'architecture avant toute conclusion ;
- détecter les vulnérabilités réelles ;
- proposer des corrections prêtes à copier.

Ne fais aucune supposition.

---

# Architecture de référence

```
Visiteur (public, sans compte)
   ↓
Site public (recherche, fiches logement) — lecture publique, annonces validées uniquement
   ↓
Connexion Google OAuth → choix du rôle (locataire / propriétaire)
   ↓
Espace Locataire  |  Espace Propriétaire (authentifiés)
   ↓
API REST (DRF)
   ↓
Services métier (services.py par app)
   ↓
PostgreSQL ←→ Redis (cache, sessions, quotas, files Celery)
   ↓
Stockage (media/S3) — photos logements, photos profil propriétaire
   ↓
Passerelle de paiement (Sebpay — Moov Money / MTN Money, XOF)
   ↓
Espace Administrateur — /cpanel_administrateur/ — authentification séparée (username + mot de passe défini en .env), JAMAIS via sélection de rôle utilisateur
```

Deux surfaces sont **critiques et prioritaires** au même titre :
1. Le **déblocage du contact propriétaire après paiement** — c'est le cœur économique de la plateforme, tout contournement (contact débloqué sans paiement confirmé) est une faille majeure.
2. L'**authentification et l'isolation de l'espace admin** — aucun utilisateur ne doit pouvoir obtenir ou s'auto-attribuer le rôle admin.

---

# Méthodologie

## Passage 1 — Compréhension

Avant toute conclusion :

- analyser les vues et serializers DRF ;
- analyser les `services.py` de chaque app ;
- analyser le flux d'authentification Google OAuth et l'attribution des rôles (locataire/propriétaire) ;
- analyser l'authentification admin (séparée, non liée à OAuth) ;
- analyser le flux de création et de validation des annonces (`properties`) ;
- analyser le flux de paiement et de déblocage de contact (`payments`, `contact_unlocks`) ;
- analyser la protection du numéro WhatsApp/téléphone avant paiement ;
- analyser la gestion des favoris et de la recherche (`favorites`, filtres) ;
- analyser le stockage média (`media/`, photos logements et profils) ;
- analyser les notifications (email admin via mot de passe d'application Gmail) ;
- analyser le journal d'activité (`admin_logs`) ;
- analyser les paramètres de plateforme (frais de contact, non codés en dur).

Ne conclure qu'après cette étape.

---

## Passage 2 — Audit

Chaque point reçoit obligatoirement un verdict :

- ✅ Conforme
- ❌ Vulnérable
- ⚠️ Partiel
- ⬜ Non applicable

Ne jamais regrouper plusieurs points.

---

# Checklist

## 1. Authentification (Google OAuth + Admin séparé)

- Le flux Google OAuth récupère uniquement prénom, nom, email, photo (si dispo) — jamais plus que nécessaire
- Après connexion Google, le choix du rôle (locataire / propriétaire) n'accorde **aucun privilège admin**, quel que soit le choix effectué côté front
- Aucune route ne permet à un utilisateur de définir lui-même `role = admin` (ni via un champ de formulaire, ni via l'API, ni via un payload manipulé)
- L'espace admin (`/cpanel_administrateur/`) utilise un système de connexion **totalement distinct** (username + mot de passe stockés en `.env` ou en base avec hash), sans lien avec le flux OAuth
- Protection contre le brute-force sur la page de connexion admin (limitation de tentatives, verrouillage temporaire)
- Sessions sécurisées (cookies `HttpOnly`, `Secure`, `SameSite`), expiration raisonnable, invalidation effective à la déconnexion
- Possibilité de révoquer/réinitialiser les sessions d'un utilisateur (admin) et de désactiver un compte

---

## 2. Base de données & modèles

- Validation des champs (prix, coordonnées GPS, numéro WhatsApp, montants) côté serveur, jamais uniquement côté client
- Contraintes d'unicité (email utilisateur, référence de transaction, numéro de reçu si applicable)
- Migrations propres, réversibles, testées
- Sauvegardes automatiques et testées — critique pour les annonces, les paiements et les logs admin

---

## 3. Annonces (properties) — création & validation

- Un propriétaire ne peut créer une annonce qu'après authentification et complétion de son profil (WhatsApp, ville, quartier, photo de profil)
- Toute nouvelle annonce est créée avec le statut `en_attente_validation` — **jamais visible publiquement** avant validation admin
- Le statut suit un flux contrôlé côté serveur : `brouillon → en_attente_validation → validee → publiee` (+ `refusee`, `suspendue`) — pas de saut arbitraire depuis le front
- Une annonce marquée `louee` ou `suspendue` n'apparaît plus dans les recherches publiques
- L'admin reçoit une notification email automatique (via mot de passe d'application Gmail) à chaque nouvelle annonce soumise
- Un propriétaire ne peut pas modifier le statut de validation de sa propre annonce (lecture seule côté propriétaire sur ce champ)

---

## 4. Paiement & déblocage du contact propriétaire (surface critique)

- Le montant des frais de contact est **configurable en base par l'admin** — jamais codé en dur dans le frontend ni le backend
- Une transaction est créée avec le statut `pending` **avant** tout appel au prestataire de paiement (Sebpay)
- Le contact du propriétaire (WhatsApp, téléphone) n'est débloqué **qu'après confirmation réelle du paiement** via le callback/webhook signé du prestataire — jamais sur simple redirection navigateur ni sur `pending`
- Une tentative de paiement non confirmée (`failed`, `cancelled`, `pending` expiré) ne débloque strictement rien
- Le webhook de confirmation Sebpay est vérifié (signature/clé secrète) pour éviter qu'un tiers ne simule un paiement réussi
- Chaque déblocage de contact (`ContactUnlock`) est lié de façon unique à un locataire + une annonce + une transaction — un paiement ne débloque pas le contact d'une autre annonce
- Idempotence : un même callback reçu plusieurs fois ne crée pas plusieurs déblocages ni ne facture deux fois

---

## 5. Protection du numéro WhatsApp / téléphone

- Le numéro WhatsApp et le téléphone du propriétaire ne sont **jamais présents dans le HTML/JSON public** de la fiche annonce avant paiement confirmé
- Le serializer DRF de la fiche annonce exclut ces champs pour tout utilisateur n'ayant pas de `ContactUnlock` validé sur cette annonce précise
- Le contrôle d'accès au contact est vérifié côté serveur à chaque requête (pas un simple `if` côté frontend qui masque visuellement le champ)
- Le lien "Contacter sur WhatsApp" n'est généré côté serveur qu'après vérification du déblocage

---

## 6. Rôles & permissions (RBAC)

- Séparation stricte : locataire, propriétaire, administrateur — un locataire ne peut pas agir comme propriétaire et inversement sans changement de rôle explicite et contrôlé
- Un propriétaire ne peut modifier/supprimer que ses propres annonces
- Un locataire ne peut voir que ses propres favoris, paiements et déblocages de contact
- Toutes les permissions sont vérifiées à chaque endpoint DRF (permission classes), jamais uniquement dans le frontend
- Aucune route ne permet l'escalade de privilèges (ex: un utilisateur ne peut pas modifier son propre champ `role` vers `admin` via l'API)

---

## 7. Photos & médias

- Validation du type MIME réel des fichiers uploadés (photos logement, photo de profil), pas seulement l'extension
- Limitation de la taille des fichiers, compression automatique
- La photo de profil propriétaire, si exigée obligatoire, ne peut pas être remplacée automatiquement par la photo Google — elle doit être uploadée manuellement
- Suppression/réorganisation des photos d'une annonce réservée au propriétaire propriétaire de l'annonce (ou à l'admin)
- Stockage sécurisé (media/S3), pas d'exécution de fichiers uploadés

---

## 8. Favoris & recherche

- Les favoris sont strictement personnels — un locataire ne peut consulter que les siens
- La recherche géolocalisée ("logements autour de moi") ne stocke pas la position GPS de l'utilisateur au-delà du temps nécessaire à la requête, sauf consentement explicite
- Les filtres de recherche ne permettent pas d'exposer des annonces non publiées via manipulation de paramètres (ex: forcer un statut `en_attente_validation` dans l'URL)

---

## 9. API REST (DRF)

- Authentification obligatoire sur toutes les routes des espaces locataire/propriétaire/admin
- Les routes publiques (recherche, détail annonce validée) sont accessibles sans authentification, en lecture strictement limitée aux champs publics (jamais le contact propriétaire non débloqué)
- Permissions par rôle vérifiées à chaque endpoint
- Pagination systématique sur les listes (annonces, transactions, utilisateurs)
- `read_only_fields` explicites sur les champs sensibles (`role`, `statut_validation`, `whatsapp`, `montant` des frais de contact)
- Protection CORS limitée aux domaines autorisés

---

## 10. Notifications (email)

- Le mot de passe d'application Gmail est stocké en variable d'environnement, jamais en dur dans le code
- Pas d'injection possible dans le contenu des emails via les variables dynamiques (nom propriétaire, email, nom d'annonce)
- Limitation du taux d'envoi (anti-spam)
- Aucune donnée sensible d'un autre utilisateur dans une notification envoyée à un utilisateur

---

## 11. Journal d'activité (admin_logs)

- Connexions admin, validations/refus d'annonces, suspensions de comptes, changements de rôle, paiements journalisés
- Journaux non modifiables a posteriori (append-only)
- Aucune donnée sensible en clair dans les logs (pas de mot de passe, pas de token de session, pas de numéro de carte)

---

## 12. Confidentialité des données utilisateurs

- Seules les données nécessaires sont collectées (email, nom, WhatsApp pour propriétaire, localisation générale)
- Les informations privées (email, téléphone non débloqué, historique de paiement) ne sont jamais indexées par les moteurs de recherche
- Les logements marqués loués/suspendus n'apparaissent pas dans les résultats publics
- Politique de conservation limitée à ce qui est nécessaire au service

---

## 13. Paramètres de plateforme

- Le montant des frais de contact, la devise (XOF), les méthodes de paiement actives (Moov Money, MTN Money via Sebpay) sont configurables depuis l'admin, jamais codés en dur
- Toute modification de paramètre sensible (frais de contact) est journalisée (`admin_logs`)

---

## 14. Préparation évolutions futures

Vérifier que l'architecture permet d'ajouter, **sans modifier les autres modules** :

- Paiement du loyer entre propriétaire et locataire (distinct des frais de mise en relation)
- Système de réservation avec dépôt de garantie
- Vérification renforcée des propriétaires (KYC)
- Visite virtuelle / vidéo
- Multi-devise ou extension hors Bénin

---

# Format des vulnérabilités

Pour chaque vulnérabilité :

- Gravité
- Emplacement
- Description
- Impact
- Scénario d'exploitation
- Correctif prêt à copier
- Temps estimé

---

# Rapport final

Le rapport doit contenir :

1. Évaluation globale (🔴 🟠 🟡 🟢)
2. Vulnérabilités critiques
3. Corrections rapides (< 10 minutes)
4. Plan de remédiation priorisé
5. Bonnes pratiques déjà présentes
6. Résumé complet de la checklist

---

# Principes de sécurité iMMoLink

- Aucune confiance dans les données envoyées par le client (rôle, statut d'annonce, statut de paiement recalculés/vérifiés côté serveur)
- Le contact propriétaire (WhatsApp/téléphone) ne se débloque que sur confirmation réelle et vérifiée du paiement
- Le rôle admin ne s'attribue jamais depuis l'interface utilisateur — uniquement en base ou par un admin existant
- Espace admin totalement isolé, authentification séparée, accessible uniquement via `/cpanel_administrateur/`
- Une annonce n'est publique qu'après validation explicite d'un administrateur
- Pas de secrets dans le code source — tout en variables d'environnement
- Services à responsabilité unique (`services.py` par app)
- Journalisation sans fuite de données sensibles

Ce document est la référence de sécurité officielle du projet iMMoLink.
