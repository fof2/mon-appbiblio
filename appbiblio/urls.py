from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='appbiblio/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),

    path('', views.home, name='home'),  
    path('home/', views.home, name='home'),

    path('categorie/<int:categorie_id>/', views.categorie_detail, name='categorie_detail'),

    path('livres-disponibles-ajax/', views.livres_disponibles_ajax, name='livres_disponibles_ajax'),
    path('api/livres/<str:nom_categorie>/', views.livres_par_categorie, name='api_livres_par_categorie'),

    path('stats/', views.stats_view, name='stats'),
    path('statistiques/', views.statistics_view, name='statistics_view'),
    path('api/stats/', views.get_stats, name='get_stats'),

    # Panier
    path('panier/', views.voir_panier, name='panier'),
    path('panier/ajouter/<int:livre_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/supprimer/<int:livre_id>/', views.supprimer_panier, name='supprimer_panier'),
    path('panier/valider/', views.valider_panier, name='valider_panier'),

    path('emprunts/', views.commandes_utilisateur, name='emprunts'),

    path('dates-prevision/', views.get_dates_prevision, name='dates_prevision'),

    path('gestion-admin/', views.dashboard_admin, name='dashboard_admin'),
    path('gestion-admin/livres/', views.livres_admin, name='livres_admin'),
    path('admin-custom/', views.dashboard, name='admin_dashboard'),
    path('admin-custom/livres/', views.liste_livres, name='admin_livres'),
    
    path('ajouter-au-panier/<int:livre_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier-count/', views.panier_count, name='panier_count'),

    path('admin-biblio/', views.gestion_admin, name='gestion_admin'),
    path('admin-biblio/emprunts/', views.emprunts_admin, name='emprunts_admin'),
    path('admin-biblio/paniers/', views.paniers_admin, name='paniers_admin'),
    path('admin-biblio/utilisateurs/', views.utilisateurs_admin, name='utilisateurs_admin'),

    path('admin-biblio/livre/ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('admin-biblio/livre/<int:livre_id>/supprimer/', views.supprimer_livre, name='supprimer_livre'),
    path('admin-biblio/livre/<int:livre_id>/modifier/', views.modifier_livre, name='modifier_livre'),
    path('admin-biblio/emprunt/ajouter/', views.ajouter_emprunt, name='ajouter_emprunt'),
    path('admin-biblio/utilisateur/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
