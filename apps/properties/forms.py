from django import forms

from apps.geo.models import Commune, Department, Locality

from .models import Property


class PropertyForm(forms.ModelForm):
    # Champ purement UI : n'existe pas sur le modèle Property,
    # sert uniquement à filtrer le select "commune" côté cascade.
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(),
        required=True,
        label="Département",
        widget=forms.Select(attrs={"id": "id_department"}),
    )

    class Meta:
        model = Property
        fields = [
            "titre",
            "description",
            "type_logement",
            "prix",
            "periodicite",
            "caution",
            "chambres",
            "department",
            "commune",
            "quartier",
            "adresse",
        ]
        widgets = {
            "commune": forms.Select(attrs={"id": "id_commune"}),
            "quartier": forms.Select(attrs={"id": "id_quartier"}),
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Par défaut les selects commune / quartier sont vides :
        # ils sont remplis dynamiquement en JS via les endpoints AJAX de l'app geo.
        self.fields["commune"].queryset = Commune.objects.none()
        self.fields["quartier"].queryset = Locality.objects.none()

        instance = getattr(self, "instance", None)

        if instance and instance.pk:
            # Édition : préremplir les querysets pour que les valeurs
            # actuelles restent affichables/sélectionnables sans JS.
            if instance.commune_id:
                self.fields["department"].initial = instance.commune.department_id
                self.fields["commune"].queryset = Commune.objects.filter(
                    department_id=instance.commune.department_id
                )
            if instance.commune_id:
                self.fields["quartier"].queryset = Locality.objects.filter(
                    arrondissement__commune_id=instance.commune_id
                )
        elif self.data:
            # Soumission POST : reconstruire les querysets à partir des
            # valeurs postées, sinon la validation rejette le choix de l'utilisateur.
            try:
                department_id = int(self.data.get("department"))
                self.fields["commune"].queryset = Commune.objects.filter(
                    department_id=department_id
                )
            except (TypeError, ValueError):
                pass

            try:
                commune_id = int(self.data.get("commune"))
                self.fields["quartier"].queryset = Locality.objects.filter(
                    arrondissement__commune_id=commune_id
                )
            except (TypeError, ValueError):
                pass