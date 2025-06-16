from django.db import models
from datetime import date
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError # Import pour ValidationError
from django.utils import timezone

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    icone = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nom

class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.CharField(max_length=200)
    categorie = models.ForeignKey('Categorie', on_delete=models.CASCADE, related_name='livres')
    isbn = models.CharField(max_length=13, default='0000000000000')
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    prix_litteraire = models.CharField(max_length=255, null=True, blank=True)
    date_publication = models.DateField()
    description = models.TextField()
    couverture = models.ImageField(upload_to='couvertures/', default='appbiblio/defaut.jpg')
    couverture_url = models.URLField(max_length=500, blank=True, null=True)
    statut = models.CharField(
        max_length=20,
        choices=[('disponible', 'Disponible'), ('emprunte', 'Emprunté'), ('réservé', 'Réservé')],
        default='disponible'
    )

    def __str__(self):
        return self.titre

    @property
    def couverture_img(self):
        # Priorité à l'URL externe sur l'API Open Library
        if self.couverture_url:
            return self.couverture_url
        # Sinon l'image uploadée localement
        if self.couverture and hasattr(self.couverture, 'url'):
            return self.couverture.url
        # Sinon l'image par défaut
        return '/media/appbiblio/defaut.jpg'

    def clean(self):
        if self.couverture_url and not self.couverture_url.startswith('http'):
            raise ValidationError("L'URL de la couverture doit commencer par 'http'.")
        

class HistoriqueLivre(models.Model):
    """Modèle pour suivre tous les mouvements d'un livre pour un utilisateur"""
    
    STATUT_CHOICES = [
        ('réservé', 'Réservé'),
        ('emprunté', 'Emprunté'),
        ('retourné', 'Retourné'),
        ('annulé', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES)
    date_action = models.DateTimeField(auto_now_add=True)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True, blank=True)
    commentaire = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date_action']
    
    def __str__(self):
        return f"{self.livre.titre} - {self.get_statut_display()} par {self.utilisateur.username}"



class Emprunt(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_retrait = models.DateTimeField()
    date_retour = models.DateTimeField(null=True, blank=True)
    date_limite_retrait = models.DateTimeField()

    def __str__(self):
        return f"{self.livre.titre} emprunté par {self.utilisateur.username}"

class Panier(models.Model):
    # Ajoutez related_name pour un accès plus propre depuis l'utilisateur
    utilisateur = models.OneToOneField(User, on_delete=models.CASCADE, related_name='panier')
    date_creation = models.DateTimeField(auto_now_add=True)# Or default=datetime.now
    livres = models.ManyToManyField(Livre, through='LignePanier', related_name='paniers')


    def __str__(self):
        return f"Panier de {self.utilisateur.username}"

    def get_emprunts_prevus(self):
        return EmpruntPrevu.objects.filter(utilisateur=self.utilisateur)


class LignePanier(models.Model):
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='lignes_panier')  # Ajout ici
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_ajout = models.DateTimeField(auto_now_add=True)
    actif = models.BooleanField(default=True)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('panier', 'livre')
    
    def __str__(self):
        return f"{self.livre.titre} dans le panier de {self.panier.utilisateur.username}" 
    
class EmpruntPrevu(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    livre = models.ForeignKey(Livre, on_delete=models.CASCADE)
    date_prevue_retrait = models.DateField(default=date.today)
    date_prevue_retour = models.DateField()

    def __str__(self):
        return f"Prévu : {self.livre.titre} pour {self.utilisateur.username}"