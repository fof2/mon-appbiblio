from django.urls import path
from . import views
from .views import historique_utilisateur 
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [
    # --- Authentification ---
    path('login/', auth_views.LoginView.as_view(template_name='appbiblio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', views.register, name='register'),
    path('check_authentication/', views.check_authentication, name='check_authentication'),

    # --- Pages Générales ---
    path('', views.home, name='home'),
    path('home/', views.home, name='home_alias'),

    # --- Catégories et Livres (Front-end) ---
    path('categorie/<int:categorie_id>/', views.categorie_detail, name='categorie_detail'),
    path('livres-disponibles-ajax/', views.livres_disponibles_ajax, name='livres_disponibles_ajax'),

    # --- Panier Permanent ---
    path('panier/', views.mon_panier, name='panier'),
    path('panier/supprimer-ligne/<int:ligne_id>/', views.supprimer_ligne_panier, name='supprimer_ligne_panier'),
    path('panier/ajouter/<int:livre_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier-count/', views.panier_count, name='panier_count'),

    # ... vos autres URLs ...
    path('panier/valider/', views.valider_panier, name='valider_panier'),
    path('panier/vider/', views.vider_panier, name='vider_panier'),
    path('historique/', views.historique_utilisateur, name='historique'),


    # --- Emprunts (Historique Utilisateur) ---
    path('mes-emprunts/', views.commandes_utilisateur, name='mes_emprunts'),

    # --- Statistiques & API ---
    path('stats/', views.stats_view, name='stats_display'),
    path('statistiques/', views.statistics_view, name='statistics_view'),
    path('api/stats/', views.get_stats, name='api_get_stats'),
    path('api/livres/<str:nom_categorie>/', views.livres_par_categorie, name='api_livres_par_categorie'),
    path('dates-prevision/', views.dates_prevision, name='dates_prevision'),

    # --- Gestion Admin ---
    path('admin-biblio/', views.gestion_admin, name='gestion_admin'),
    path('admin-biblio/livres/', views.livres_admin, name='livres_admin'),
    path('admin-biblio/emprunts/', views.emprunts_admin, name='emprunts_admin'),
    path('admin-biblio/paniers/', views.paniers_admin, name='paniers_admin'),
    path('admin-biblio/utilisateurs/', views.utilisateurs_admin, name='utilisateurs_admin'),

    path('admin-biblio/livre/ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('admin-biblio/livre/<int:livre_id>/modifier/', views.modifier_livre, name='modifier_livre'),
    path('admin-biblio/livre/<int:livre_id>/supprimer/', views.supprimer_livre, name='supprimer_livre'),
    path('admin-biblio/emprunt/ajouter/', views.ajouter_emprunt, name='ajouter_emprunt'),
    path('admin-biblio/utilisateur/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),

    path('admin-biblio/emprunt/valider/<int:livre_id>/<int:user_id>/', views.valider_emprunt_admin, name='valider_emprunt_admin'),
    path('admin-biblio/emprunt/refuser/<int:livre_id>/<int:user_id>/', views.refuser_emprunt_admin, name='refuser_emprunt_admin'),
    path('admin-biblio/emprunt/retourner/<int:emprunt_id>/', views.marquer_retourne_admin, name='marquer_retourne_admin'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)