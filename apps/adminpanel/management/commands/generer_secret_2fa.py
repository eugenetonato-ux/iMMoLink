"""
Génère un nouveau secret TOTP pour le 2FA admin.

Usage :
    python manage.py generer_secret_2fa

Copie la valeur ADMIN_TOTP_SECRET affichée dans .env, puis scanne le QR
(ou saisis l'URI manuellement) dans Google Authenticator / Authy.
À exécuter UNE SEULE FOIS (ou pour régénérer le secret en cas de perte
du téléphone — dans ce cas, remplacer la valeur dans .env sur le serveur).
"""
import pyotp
import qrcode
import io

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Génère un secret TOTP pour le 2FA de l'espace admin iMMoLink."

    def handle(self, *args, **options):
        secret = pyotp.random_base32()
        username = settings.ADMIN_USERNAME or "admin"
        uri = pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name="iMMoLink Admin")

        self.stdout.write(self.style.SUCCESS("\nSecret généré avec succès.\n"))
        self.stdout.write(f"Ajoute cette ligne dans ton fichier .env :\n")
        self.stdout.write(self.style.WARNING(f"ADMIN_TOTP_SECRET={secret}\n"))
        self.stdout.write("Puis scanne ce QR code dans Google Authenticator / Authy :\n")

        qr = qrcode.QRCode(border=1)
        qr.add_data(uri)
        qr.make()
        buf = io.StringIO()
        qr.print_ascii(out=buf, invert=True)
        self.stdout.write(buf.getvalue())

        self.stdout.write(f"\nOu saisis manuellement l'URI si le QR ne s'affiche pas bien :\n{uri}\n")