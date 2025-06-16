from django.contrib import admin
from django.utils.html import format_html
# Assurez-vous d'importer tous les modèles que vous souhaitez gérer
from .models import Categorie, Livre, Emprunt, Panier, EmpruntPrevu, LignePanier,HistoriqueLivre


# Configuration de l'administration pour le modèle Livre
class LivreAdmin(admin.ModelAdmin):
    # Champs à afficher dans la vue en liste des livres
    list_display = ('titre', 'auteur', 'categorie', 'statut', 'afficher_couverture')
    # Champs à utiliser pour la recherche
    search_fields = ('titre', 'auteur', 'isbn')
    # Champs pour filtrer les résultats dans la barre latérale droite
    list_filter = ('categorie', 'statut', 'date_publication')
    # Champs qui peuvent être modifiés directement dans la vue en liste (s'il n'y en a pas beaucoup)
    list_editable = ('statut',) # Exemple : permet de changer le statut directement depuis la liste
    # Champs à rendre cliquables pour accéder à la page de détail
    list_display_links = ('titre',)
    # Remarque : si vous aviez un champ 'slug' (pour des URL conviviales), vous utiliseriez :
    # prepopulated_fields = {'slug': ('titre',)}


    # Méthode personnalisée pour afficher l'image de couverture du livre dans la liste d'administration
    def afficher_couverture(self, obj):
        if obj.couverture_img: # Vérifier si une image de couverture existe
            return format_html('<img src="{}" style="height: 100px; object-fit: contain;" />', obj.couverture_img)
        return "Pas de couverture" # Texte si aucune image n'est disponible
    afficher_couverture.short_description = 'Couverture' # En-tête de colonne dans l'administration


# --- Inline pour LignePanier (pour gérer les articles du panier à l'intérieur d'un Panier) ---
class LignePanierInline(admin.TabularInline):
    model = LignePanier
    extra = 1
    fields = ('livre', 'date_ajout', 'actif')  # Utilisez les champs actuels
    readonly_fields = ('date_ajout',)  # Rendre la date en lecture seule

# Configuration de l'administration pour le modèle Panier
class PanierAdmin(admin.ModelAdmin):
    list_display = ('utilisateur',) # Afficher l'utilisateur associé au panier
    # Ajoutez la classe inline ici pour afficher les entrées LignePanier dans la page de détail du Panier
    inlines = [LignePanierInline]
    # Facultatif : pour rendre le champ utilisateur en lecture seule si défini programmatiquement
    # readonly_fields = ('utilisateur',) # Décommentez si vous voulez empêcher les changements directs d'utilisateur


# Configuration de l'administration pour le modèle Emprunt
class EmpruntAdmin(admin.ModelAdmin):
    list_display = ('livre', 'utilisateur', 'date_retrait', 'date_retour', 'date_limite_retrait')
    list_filter = ('utilisateur', 'livre', 'date_retrait', 'date_retour')
    search_fields = ('livre__titre', 'utilisateur__username') # Recherche par titre du livre ou nom d'utilisateur


# Configuration de l'administration pour le modèle EmpruntPrevu
class EmpruntPrevuAdmin(admin.ModelAdmin):
    list_display = ('livre', 'utilisateur', 'date_prevue_retrait', 'date_prevue_retour')
    list_filter = ('utilisateur', 'livre', 'date_prevue_retrait')
    search_fields = ('livre__titre', 'utilisateur__username')


# Configuration de l'administration pour le modèle Categorie
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'icone')
    search_fields = ('nom',)

class HistoriqueLivreAdmin(admin.ModelAdmin):
    list_display = ('livre', 'utilisateur', 'statut', 'date_action', 'date_debut', 'date_fin')
    list_filter = ('statut', 'utilisateur', 'date_action')
    search_fields = ('livre__titre', 'utilisateur__username', 'commentaire')
    readonly_fields = ('date_action',)  # La date d'action ne doit pas être modifiable
    date_hierarchy = 'date_action'  # Navigation par date
    
    fieldsets = (
        (None, {
            'fields': ('utilisateur', 'livre', 'statut')
        }),
        ('Dates', {
            'fields': ('date_debut', 'date_fin'),
            'classes': ('collapse',)
        }),
        ('Autres', {
            'fields': ('commentaire',),
            'classes': ('wide',)
        }),
    )


# --- Enregistrement de vos modèles avec leurs classes Admin personnalisées ---
admin.site.register(Livre, LivreAdmin)
admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Emprunt, EmpruntAdmin)
admin.site.register(Panier, PanierAdmin)
admin.site.register(EmpruntPrevu, EmpruntPrevuAdmin)
admin.site.register(LignePanier)
admin.site.register(HistoriqueLivre, HistoriqueLivreAdmin)
# Vous n'avez généralement pas besoin d'enregistrer LignePanier directement s'il est géré uniquement via PanierInline.
# Si vous souhaitez voir LignePanier comme un élément de premier niveau dans le menu d'administration, décommentez la ligne ci-dessous :
