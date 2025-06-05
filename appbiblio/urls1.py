from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

http://127.0.0.1:8000/gestion-admin/livres/

urlpatterns = [
        path('gestion-admin/', views.dashboard_admin, name='dashboard_admin'),
        path('gestion-admin/livres/', views.livres_admin, name='livres_admin'),
        path('admin-custom/', views.dashboard, name='admin_dashboard'),
        path('admin-custom/livres/', views.liste_livres, name='admin_livres'),
        path('admin-custom/livre/ajouter/', views.ajouter_livre, name='ajouter_livre'),
        path('admin-biblio/', views.gestion_admin, name='gestion_admin'),
        path('admin-biblio/emprunts/', views.emprunts_admin, name='emprunts_admin'),
        path('admin-biblio/paniers/', views.paniers_admin, name='paniers_admin'),
        path('admin-biblio/utilisateurs/', views.utilisateurs_admin, name='utilisateurs_admin'),

    path('admin-biblio/livre/<int:livre_id>/modifier/', views.modifier_livre, name='modifier_livre'),
    path('admin-biblio/livre/ajouter/', views.ajouter_livre, name='ajouter_livre'),
    path('admin-biblio/livre/<int:livre_id>/modifier/', views.modifier_livre, name='modifier_livre'),

    path('admin-biblio/emprunt/ajouter/', views.ajouter_emprunt, name='ajouter_emprunt'),

    path('admin-biblio/utilisateur/<int:user_id>/modifier/', views.modifier_utilisateur, name='modifier_utilisateur'),
    # ... autres routes pour les emprunts, paniers, utilisateurs
]