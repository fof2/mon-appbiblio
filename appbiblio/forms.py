

from django import forms
from .models import Livre, Emprunt
from django.contrib.auth.models import User

class LivreForm(forms.ModelForm):
    class Meta:
        model = Livre
        fields = '__all__'

class EmpruntForm(forms.ModelForm):
    class Meta:
        model = Emprunt
        fields = '__all__'

class UtilisateurForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'is_staff', 'is_active']

