from django.contrib import admin
from django.utils.html import format_html
from .models import Categorie, Livre, Emprunt, Panier, EmpruntPrevu

class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'categorie', 'statut', 'afficher_couverture')

    def afficher_couverture(self, obj):
        return format_html('<img src="{}" style="height: 100px;" />', obj.couverture_img)
    afficher_couverture.short_description = 'Couverture'

admin.site.register(Livre, LivreAdmin)  # Seulement ici pour Livre

admin.site.register(Categorie)
admin.site.register(Emprunt)
admin.site.register(Panier) 
admin.site.register(EmpruntPrevu)
