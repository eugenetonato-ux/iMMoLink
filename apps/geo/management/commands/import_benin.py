import json
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.geo.models import (
    Department,
    Commune,
    Arrondissement,
    Locality,
)


class Command(BaseCommand):
    help = "Importe la structure administrative du Bénin depuis benin.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="benin.json",
            help="Chemin vers le fichier JSON",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Supprime les données existantes avant l'import",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        json_file = Path(options["file"])

        if not json_file.exists():
            self.stdout.write(
                self.style.ERROR(f"Fichier introuvable : {json_file}")
            )
            return

        # Suppression des anciennes données si --clear est utilisé
        if options["clear"]:
            self.stdout.write(
                self.style.WARNING("Suppression des anciennes données...")
            )

            Locality.objects.all().delete()
            Arrondissement.objects.all().delete()
            Commune.objects.all().delete()
            Department.objects.all().delete()

        # Lecture du JSON
        self.stdout.write("Lecture de benin.json...")

        try:
            with open(json_file, "r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            self.stdout.write(
                self.style.ERROR(f"JSON invalide : {error}")
            )
            return

        # Ton fichier JSON contient directement la liste des départements
        if not isinstance(data, list):
            self.stdout.write(
                self.style.ERROR(
                    "Structure JSON incorrecte : une liste de départements est attendue."
                )
            )
            return

        department_count = 0
        commune_count = 0
        arrondissement_count = 0
        locality_count = 0

        # ==========================================================
        # DÉPARTEMENTS
        # ==========================================================

        for department_data in data:

            department_name = department_data.get("lib_dep")

            if not department_name:
                continue

            department, created = Department.objects.get_or_create(
                nom=department_name.strip()
            )

            if created:
                department_count += 1

            self.stdout.write(
                f"Département : {department.nom}"
            )

            # ======================================================
            # COMMUNES
            # ======================================================

            for commune_data in department_data.get("communes", []):

                commune_name = commune_data.get("lib_com")

                if not commune_name:
                    continue

                commune, created = Commune.objects.get_or_create(
                    nom=commune_name.strip(),
                    department=department,
                )

                if created:
                    commune_count += 1

                # ==================================================
                # ARRONDISSEMENTS
                # ==================================================

                for arrondissement_data in commune_data.get(
                    "arrondissements", []
                ):

                    arrondissement_name = arrondissement_data.get(
                        "lib_arrond"
                    )

                    if not arrondissement_name:
                        continue

                    arrondissement, created = (
                        Arrondissement.objects.get_or_create(
                            nom=arrondissement_name.strip(),
                            commune=commune,
                        )
                    )

                    if created:
                        arrondissement_count += 1

                    # ==============================================
                    # QUARTIERS
                    # ==============================================

                    for quartier_data in arrondissement_data.get(
                        "quartiers", []
                    ):

                        quartier_name = quartier_data.get("lib_quart")

                        if not quartier_name:
                            continue

                        locality, created = Locality.objects.get_or_create(
                            nom=quartier_name.strip(),
                            arrondissement=arrondissement,
                            defaults={
                                "locality_type": "quartier"
                            },
                        )

                        if created:
                            locality_count += 1

        # ==========================================================
        # RÉSULTAT
        # ==========================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "IMPORT DU BÉNIN TERMINÉ AVEC SUCCÈS"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "========================================"
            )
        )

        self.stdout.write(
            f"Départements ajoutés       : {department_count}"
        )

        self.stdout.write(
            f"Communes ajoutées          : {commune_count}"
        )

        self.stdout.write(
            f"Arrondissements ajoutés    : {arrondissement_count}"
        )

        self.stdout.write(
            f"Quartiers ajoutés          : {locality_count}"
        )

        self.stdout.write("")