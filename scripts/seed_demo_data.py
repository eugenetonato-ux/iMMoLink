"""
Génère des données de démonstration pour iMMoLink : villes/quartiers du Bénin,
équipements, un propriétaire vérifié et plusieurs annonces publiées avec des
photos générées localement (aucun téléchargement externe, aucune dépendance
réseau — juste Pillow).

Usage :
    env\\Scripts\\python.exe scripts\\seed_demo_data.py
"""
import os
import random
import sys
from io import BytesIO
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()

from django.core.files.base import ContentFile  # noqa: E402
from django.utils import timezone  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

from apps.accounts.models import OwnerProfile, User  # noqa: E402
from apps.common.models import PlatformSettings  # noqa: E402
from apps.locations.models import Quartier, Ville  # noqa: E402
from apps.properties.models import Amenity, Property, PropertyImage  # noqa: E402

VILLES = {
    "Cotonou": ["Akpakpa", "Fidjrossè", "Cadjèhoun", "Gbégamey", "Haie Vive", "Ganhi"],
    "Porto-Novo": ["Ouando", "Djègan-Daho", "Dowa", "Houinmè"],
    "Abomey-Calavi": ["Godomey", "Togba", "Zogbo", "Akassato"],
    "Parakou": ["Banikanni", "Titirou", "Zongo"],
    "Ouidah": ["Sogbadji", "Docomè"],
    "Bohicon": ["Avogbanna", "Passagon"],
}

AMENITIES = [
    # (nom, classe d'icône Font Awesome sans le préfixe fa-solid)
    ("Eau courante", "fa-shower"),
    ("Électricité (SBEE)", "fa-bolt"),
    ("Groupe électrogène", "fa-plug"),
    ("Climatisation", "fa-snowflake"),
    ("Cuisine équipée", "fa-kitchen-set"),
    ("Parking privé", "fa-square-parking"),
    ("Sécurité 24h/24", "fa-shield-halved"),
    ("Wifi", "fa-wifi"),
    ("Meublé", "fa-couch"),
    ("Forage", "fa-faucet-drip"),
]

TYPES = ["chambre", "studio", "appartement", "maison", "villa"]
PERIODES = ["mensuel", "trimestriel", "annuel"]

COULEURS = [
    (29, 122, 116), (18, 58, 74), (245, 158, 11),
    (16, 185, 129), (99, 102, 241), (14, 116, 144),
]

TITRES = [
    "Studio meublé proche de la plage", "Chambre calme dans quartier résidentiel",
    "Appartement 2 chambres avec balcon", "Maison familiale avec cour",
    "Villa moderne avec jardin", "Studio climatisé tout équipé",
    "Appartement standing centre-ville", "Chambre salon indépendante",
    "Maison 3 chambres proche université", "Villa avec vue dégagée",
    "Studio neuf entièrement carrelé", "Appartement lumineux 3 pièces",
]


def image_generee(texte, taille=(900, 600), seed=0):
    """Crée un visuel dégradé + libellé, sans dépendance réseau."""
    couleur = COULEURS[seed % len(COULEURS)]
    img = Image.new("RGB", taille, couleur)
    draw = ImageDraw.Draw(img)
    for y in range(taille[1]):
        ratio = y / taille[1]
        r = int(couleur[0] * (1 - ratio * 0.45))
        g = int(couleur[1] * (1 - ratio * 0.45))
        b = int(couleur[2] * (1 - ratio * 0.45))
        draw.line([(0, y), (taille[0], y)], fill=(r, g, b))
    try:
        font = ImageFont.truetype("arial.ttf", max(18, taille[0] // 22))
    except Exception:
        font = ImageFont.load_default()
    draw.text((taille[0] * 0.05, taille[1] * 0.85), texte, fill=(255, 255, 255), font=font)
    buf = BytesIO()
    img.save(buf, format="JPEG", quality=82)
    fichier = ContentFile(buf.getvalue())
    fichier.name = f"generee_{seed}.jpg"
    return fichier


def run():
    print("→ Paramètres plateforme…")
    PlatformSettings.get_solo()

    print("→ Villes & quartiers du Bénin…")
    villes_objs = {}
    for i, (nom, quartiers) in enumerate(VILLES.items()):
        ville, _ = Ville.objects.get_or_create(nom=nom, defaults={"est_populaire": i < 4, "ordre": i})
        villes_objs[nom] = ville
        for q in quartiers:
            Quartier.objects.get_or_create(ville=ville, nom=q)

    print("→ Équipements…")
    amenity_objs = []
    for nom, icone in AMENITIES:
        obj, _ = Amenity.objects.get_or_create(nom=nom, defaults={"icone": icone})
        amenity_objs.append(obj)

    print("→ Propriétaire de démonstration…")
    user, created = User.objects.get_or_create(
        email="demo.proprietaire@iMMoLink.app",
        defaults={
            "username": "demo_proprietaire",
            "first_name": "Aïcha",
            "last_name": "Dossou",
            "role": "proprietaire",
        },
    )
    if created:
        user.set_unusable_password()
        user.save()

    profil, _ = OwnerProfile.objects.get_or_create(
        user=user,
        defaults={"whatsapp": "+22997000000", "ville": "Cotonou", "quartier": "Akpakpa", "verifie": True},
    )
    if not profil.photo_profil:
        profil.photo_profil.save("demo_owner.jpg", image_generee("Aïcha D.", (300, 300), seed=1), save=True)

    print("→ Annonces de démonstration…")
    seed_i = 1
    villes_liste = list(VILLES.keys())
    for i, titre in enumerate(TITRES):
        ville_nom = villes_liste[i % len(villes_liste)]
        quartier_nom = random.choice(VILLES[ville_nom])
        annonce, created_annonce = Property.objects.get_or_create(
            titre=titre,
            proprietaire=profil,
            defaults={
                "description": (
                    f"{titre} situé à {quartier_nom}, {ville_nom}. Logement propre, sécurisé et "
                    "bien situé, à proximité des commodités (marché, transport, écoles)."
                ),
                "type_logement": TYPES[i % len(TYPES)],
                "prix": random.choice([25000, 35000, 45000, 60000, 85000, 120000, 180000]),
                "periodicite": random.choice(PERIODES),
                "caution": random.choice([None, 30000, 50000, 90000]),
                "chambres": random.randint(1, 4),
                "ville": ville_nom,
                "quartier": quartier_nom,
                "statut": "publiee",
                "disponibilite": "disponible" if i % 6 != 0 else "indisponible",
            },
        )
        if created_annonce:
            annonce.publiee_le = timezone.now()
            annonce.save(update_fields=["publiee_le"])
            annonce.amenities.set(random.sample(amenity_objs, k=random.randint(3, 6)))
            for photo_i in range(2):
                seed_i += 1
                PropertyImage.objects.create(
                    annonce=annonce,
                    fichier=image_generee(f"{ville_nom} — {quartier_nom}", seed=seed_i),
                    principale=(photo_i == 0),
                    ordre=photo_i,
                )

    print("→ Photos des villes populaires…")
    for ville in villes_objs.values():
        if not ville.photo:
            seed_i += 1
            ville.photo.save(f"ville_{ville.slug}.jpg", image_generee(ville.nom, (500, 360), seed=seed_i), save=True)

    print(f"✓ Données prêtes : {Property.objects.count()} annonces, {Ville.objects.count()} villes.")


if __name__ == "__main__":
    run()
