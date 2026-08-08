# iMMoLink — Design System (Site Public + Espaces Locataire/Propriétaire + Admin)

Ce document définit l'identité visuelle de la plateforme, pensée **mobile-first** puisque la majorité des recherches de logement se feront depuis un smartphone.

Trois univers visuels cohérents :
- **Site public + espaces locataire/propriétaire** — moderne, rassurant, professionnel, orienté confiance (on parle de logement et d'argent).
- **Back-office admin** (`cpanel_administrateur`) — dashboard SaaS dense, sombre, orienté supervision et données.

---

## 1. Palette de couleurs

### Site public & espaces utilisateurs
| Rôle | Couleur | Usage |
|---|---|---|
| Primaire | `#1D7A74` (vert sarcelle du logo) | Boutons principaux, liens, éléments actifs |
| Primaire foncé | `#123A4A` (bleu marine du logo) | Hover, header |
| Accent | `#F59E0B` (orange chaleureux) | CTA secondaires, badges "Nouveau", mise en avant |
| Succès / disponible | `#10B981` (vert émeraude) | Statut "disponible", paiement confirmé |
| Attention / en attente | `#F59E0B` | Statut "en attente de validation" |
| Erreur / indisponible | `#EF4444` | Statut "loué", "refusée", erreurs |
| Fond clair | `#FFFFFF` / `#F9FAFB` | Fond général |
| Texte | `#111827` | Titres |
| Texte secondaire | `#6B7280` | Descriptions, labels |

### Back-office admin (`cpanel_administrateur`)
| Rôle | Couleur | Usage |
|---|---|---|
| Primaire | `#1E293B` (bleu nuit) | Sidebar |
| Accent primaire | `#1D7A74` | Boutons, montants clés, graphiques |
| Fond général | `#F1F5F9` | Fond de page |
| Cartes | `#FFFFFF` avec ombre douce | Blocs de contenu, statistiques |
| Succès | `#10B981` | Annonce publiée, paiement réussi |
| Attention | `#F59E0B` | En attente de validation |
| Erreur | `#EF4444` | Compte suspendu, paiement échoué |
| Texte | `#0F172A` | Titres |
| Texte secondaire | `#64748B` | Sous-titres, labels |

---

## 2. Typographie

- **Titres (H1-H3)** : sans-serif grasse (type *Sora* ou *Poppins* Bold/SemiBold) — gros titres sur la bannière héro, chiffres clés du dashboard admin.
- **Corps de texte** : sans-serif régulière (type *Inter*) — bonne lisibilité sur cartes d'annonces et formulaires.
- **Prix** : toujours en gras, suffixe **XOF** (ex: `45 000 XOF/mois`, jamais de décimale).

---

## 3. Site public — Composants

### 3.1 En-tête
- Logo à gauche ("iMMoLink" + icône maison/clé stylisée)
- Barre de recherche compacte (ville, quartier)
- Boutons : "Publier un logement" / "Se connecter avec Google"
- Icône favoris (❤️, badge avec nombre)

### 3.2 Bannière héro
- Grand bloc bleu avec photo de logement en avant-plan
- Titre impactant ("Trouvez votre prochain logement au Bénin") + sous-texte
- Barre de recherche avancée intégrée (ville, quartier, type, prix min/max, chambres)
- Boutons CTA "Trouver un logement" / "Publier un logement"

### 3.3 Villes / quartiers populaires
- Rangée de cartes avec photo représentative + nom de la ville/quartier + nombre d'annonces

### 3.4 Grille d'annonces
- Carte logement : photo principale, badge statut ("Nouveau", "Disponible"), titre, ville/quartier, prix + périodicité, icône ❤️ favoris
- Grille responsive : 1 colonne mobile, 2 tablette, 3-4 desktop

### 3.5 Fiche annonce (détail)
- Grande photo principale + galerie (swipe mobile)
- Titre, prix, type de logement, description, équipements
- Localisation (ville, quartier + carte)
- Bloc "Informations du propriétaire" — nom, photo, badge "✓ Vérifié" si applicable — **numéro WhatsApp masqué**
- Bouton principal : **"Contacter le propriétaire"** → ouvre le récapitulatif de paiement (1000 XOF)
- Après paiement confirmé : bouton devient **"Contacter sur WhatsApp"** (vert, icône WhatsApp)

### 3.6 Écran de paiement (frais de mise en relation)
- Encart clair : montant, méthode de paiement (Moov Money / MTN Money), conditions
- États visuels distincts : en attente / confirmé / échoué
- Aucune donnée de contact affichée avant confirmation explicite

---

## 4. Espace Locataire

- Dashboard avec cartes : recherches récentes, favoris, contacts débloqués, notifications
- Liste "Mes favoris" identique à la grille d'annonces publique
- Historique des paiements de mise en relation (montant, annonce, date, statut)
- Notifications : nouvelles annonces correspondant à ses critères/zone

## 5. Espace Propriétaire

- Dashboard avec cartes chiffrées : nombre de logements, annonces actives/en attente/refusées, consultations, demandes
- Formulaire de création d'annonce en plusieurs étapes (infos générales → prix → localisation → photos → aperçu)
- Badge de statut visible sur chaque annonce (`En attente`, `Validée`, `Publiée`, `Refusée`, `Louée`)
- Upload photo de profil obligatoire distinct de la photo Google

---

## 6. Back-office admin (`cpanel_administrateur`)

### 6.1 Sidebar (fixe, bleu nuit)
- Logo "iMMoLink Admin" en haut
- Navigation : **Dashboard**, **Utilisateurs**, **Propriétaires**, **Annonces**, **Transactions**, **Signalements**, **Statistiques**, **Paramètres**, **Logs**

### 6.2 En-tête dashboard
- Message d'accueil ("Bonjour, Administrateur")
- Barre de recherche (utilisateur, annonce, transaction)
- Icônes notifications (nouvelle annonce à valider, nouvelle inscription)

### 6.3 Cartes statistiques clés
- Cartes chiffrées : utilisateurs totaux, locataires, propriétaires, annonces publiées/en attente, revenus du jour/mois, paiements réussis/échoués
- Graphiques : évolution des inscriptions, évolution des annonces, revenus, logements par ville

### 6.4 File de validation des annonces
- Liste des annonces `en_attente_validation` avec aperçu photo, propriétaire, actions rapides : Approuver / Refuser / Demander modification

### 6.5 Gestion des utilisateurs
- Table avec recherche/filtre par rôle, badge statut (actif/suspendu), actions : voir profil, suspendre, réactiver

### 6.6 Transactions
- Table : référence, locataire, propriétaire, annonce, montant, méthode, statut, date
- Export CSV/PDF

### 6.7 Paramètres plateforme
- Champ "Frais de mise en relation" (XOF, modifiable, jamais codé en dur côté front)
- Gestion des villes/quartiers, méthodes de paiement actives

---

## 7. Composants transverses

- **Boutons** : coins arrondis (`border-radius: 12px`), ombre légère, état hover avec léger assombrissement
- **Cartes** : coins arrondis (`16-20px`), ombre douce (`0 4px 20px rgba(0,0,0,0.06)`)
- **Badges de statut** : pastille colorée + texte court (`En attente`, `Publiée`, `Louée`, `Refusée`, `Vérifié`)
- **Montants** : toujours affichés en gras avec le suffixe `XOF`
- **Skeleton loaders** sur les grilles d'annonces pendant le chargement
- **Toasts** de confirmation (paiement réussi, favori ajouté, annonce soumise)

---

## 8. Ton et contenu

- Ton rassurant, clair, orienté confiance sur le site public ("Logements vérifiés", "Contactez le propriétaire en toute sécurité")
- Ton fonctionnel et précis dans les espaces locataire/propriétaire (formulaires simples, messages d'erreur explicites)
- Ton neutre et factuel dans le back-office admin — priorité à la densité d'information et à la rapidité d'action
