from django.contrib.auth import login
from django.db import models, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django import forms
from django.db.models import Count
from .forms import UtilisateurForm

from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.contrib.auth.models import User
from .models import Livre, Categorie, Emprunt, Panier, EmpruntPrevu 
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta, date




# Formulaire personnalisé pour l'inscription
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Prénom", required=False)
    last_name = forms.CharField(label="Nom", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

# Vue pour l'accueil
# views.py
@login_required
def home(request):
    # Correction du comptage des livres par catégorie
    categories = Categorie.objects.annotate(
        nombre_livres=Count('livres')  # Utilisation du nom correct du modèle
    ).all()

    # Récupération des livres
    livres = Livre.objects.all()

    # Calcul des statistiques
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    livres_empruntes = Livre.objects.filter(statut='emprunté').count()
    nombre_categories = Categorie.objects.count()
    membres_actifs = User.objects.filter(is_active=True).count()
    nombre_auteurs = Livre.objects.values('auteur').distinct().count()
    emprunts_par_mois = Emprunt.objects.filter(
        date_retrait__month=timezone.now().month
    ).count()

    # Passer les données au template
    return render(request, 'appbiblio/home.html', {
        'categories': categories,
        'livres': livres,
        'livres_disponibles': livres_disponibles,
        'livres_empruntes': livres_empruntes,
        'nombre_categories': nombre_categories,
        'membres_actifs': membres_actifs,
        'nombre_auteurs': nombre_auteurs,
        'emprunts_par_mois': emprunts_par_mois
    })
def livres_disponibles_ajax(request):
    # Calculer le nombre de livres disponibles
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    return JsonResponse({'livres_disponibles': livres_disponibles})

# Vue pour l'inscription
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            login(request, user)  # Connexion après l'inscription
            return redirect('home')  # ou autre page après inscription {% url 'home' %}
    else:
        form = CustomUserCreationForm()
    return render(request, 'appbiblio/register.html', {'form': form})





def categorie_detail(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livres = categorie.livres.all()  # Accède aux livres via le related_name
    nombre_livres = livres.count()  # Compte réel

    return render(request, 'appbiblio/categorie_detail.html', {
        'categorie': categorie,
        'livres': livres,
        'nombre_livres': nombre_livres
    })




def get_stats(request):
    total_livres = Livre.objects.filter(statut='disponible').count()
    membres_actifs = 12430  # Exemple : à remplacer par une vraie requête
    emprunts_mois = 3850    # Exemple statique
    prix_litteraires = 150  # Exemple statique

    return JsonResponse({
        'livres_disponibles': total_livres,
        'membres_actifs': membres_actifs,
        'emprunts_par_mois': emprunts_mois,
        'prix_litteraires': prix_litteraires,
    })



def statistics_view(request):
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    livres_empruntes = Emprunt.objects.filter(date_retrait__isnull=False).count()
    nombre_categories = Categorie.objects.count()
    nombre_auteurs = Livre.objects.values('auteur').distinct().count()
    membres_actifs = User.objects.filter(is_active=True).count()
    emprunts_par_mois = Emprunt.objects.filter(date_retrait__month=timezone.now().month).count()
    prix_litteraires = Livre.objects.filter(prix_litteraire__isnull=False).count()

    return JsonResponse({
        'livres_disponibles': livres_disponibles,
        'livres_empruntes': livres_empruntes,
        'nombre_categories': nombre_categories,
        'nombre_auteurs': nombre_auteurs,
        'membres_actifs': membres_actifs,
        'emprunts_par_mois': emprunts_par_mois,
        'prix_litteraires': prix_litteraires,
    })


def livres_par_categorie(request, nom_categorie):
    # Récupérer la catégorie par son nom, avec gestion des erreurs
    categorie = get_object_or_404(Categorie, nom=nom_categorie)
    
    # Récupérer les livres de cette catégorie
    livres = Livre.objects.filter(categorie=categorie)
    
    # Nombre total de livres dans cette catégorie
    nombre_livres = livres.count()

    # Passer la catégorie, les livres et le nombre de livres au template
    return render(request, 'appbiblio/categorie_detail.html', {
        'categorie': categorie,
        'livres': livres,
        'nombre_livres': nombre_livres
    })


def stats_view(request):
    total_livres = Livre.objects.count()
    livres_empruntes = Emprunt.objects.filter(date_retrait__isnull=False).count()
    total_categories = Categorie.objects.count()
    total_auteurs = Livre.objects.values('auteur').distinct().count()  # Nombre d'auteurs distincts
    
    return render(request, 'stats.html', {
        'total_livres': total_livres,
        'livres_empruntes': livres_empruntes,
        'total_categories': total_categories,
        'total_auteurs': total_auteurs
    })







@login_required
@csrf_exempt
def ajouter_au_panier(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    
    # Vérifier si le livre est déjà dans le panier
    if panier.livres.filter(id=livre_id).exists():
        return JsonResponse({
            'success': False, 
            'message': 'Ce livre est déjà dans votre panier'
        })
    
    # Si c'est une confirmation, ajouter au panier
    if request.method == 'POST':
        # Ajouter le livre au panier
        panier.livres.add(livre)
        
        # Créer un emprunt prévu pour ce livre
        date_retrait = timezone.now()
        date_limite_retrait = date_retrait + timedelta(days=2)
        date_retour = date_retrait + timedelta(days=14)
        
        EmpruntPrevu.objects.create(
            panier=panier,
            livre=livre,
            date_prevue_retrait=date_retrait,
            date_limite_retrait=date_limite_retrait,
            date_prevue_retour=date_retour
        )
        
        return JsonResponse({'success': True})
    
    # Si c'est une demande de confirmation
    return JsonResponse({
        'confirmation': True,
        'message': f'Voulez-vous ajouter "{livre.titre}" à votre panier?'
    })


@login_required
def voir_panier(request):
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    return render(request, 'appbiblio/panier.html', {'panier': panier})

@login_required
def supprimer_panier(request, livre_id):
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    livre = get_object_or_404(Livre, id=livre_id)
    panier.livres.remove(livre)
    messages.info(request, f"Le livre '{livre.titre}' a été retiré du panier.")
    return redirect('panier')



@login_required
def valider_panier(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    
    # Créer un emprunt pour chaque livre du panier
    for livre in panier.livres.all():
        emprunt_prevu = get_object_or_404(EmpruntPrevu, panier=panier, livre=livre)
        
        Emprunt.objects.create(
            utilisateur=request.user,
            livre=livre,
            date_emprunt=emprunt_prevu.date_prevue_retrait,
            date_retour_prevue=emprunt_prevu.date_prevue_retour
        )
        
        # Mettre à jour le statut du livre
        livre.statut = 'emprunté'
        livre.save()
        
        # Supprimer l'emprunt prévu
        emprunt_prevu.delete()
    
    # Vider le panier
    panier.livres.clear()
    
    messages.success(request, "Votre emprunt a été validé avec succès !")
    return redirect('home')




@login_required
def mon_panier(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    livres = panier.livres.all()
    emprunts_prevus = EmpruntPrevu.objects.filter(utilisateur=request.user, livre__in=livres)
    dates_prevision = {ep.livre.id: ep for ep in emprunts_prevus}

    # Ajouter les dates prévues à chaque livre
    for livre in livres:
        emprunt_prevu = dates_prevision.get(livre.id)
        if emprunt_prevu:
            livre.date_prevue_retrait = emprunt_prevu.date_prevue_retrait
            livre.date_prevue_retour = emprunt_prevu.date_prevue_retour
        else:
            # Valeurs par défaut si pas d'emprunt prévu
            livre.date_prevue_retrait = date.today() + timedelta(days=2)
            livre.date_prevue_retour = date.today() + timedelta(days=14)

    return render(request, 'appbiblio/panier.html', {'panier': panier})



@login_required
def commandes_utilisateur(request):
    utilisateur = request.user
    print("Utilisateur connecté :", utilisateur)

    emprunts_valides = Emprunt.objects.filter(utilisateur=utilisateur)
    print("Emprunts validés :", emprunts_valides)

    emprunts_non_valides = EmpruntPrevu.objects.filter(utilisateur=utilisateur)
    print("Emprunts en attente :", emprunts_non_valides)

    return render(request, 'appbiblio/historique_emprunts.html', {
        'emprunts_valides': emprunts_valides,
        'emprunts_non_valides': emprunts_non_valides
    })


def get_dates_prevision(request):
    # Définir les dates, ici on utilise des dates fictives pour l'exemple
    date_retrait = timezone.now() + timedelta(days=1)
    date_limite_retrait = timezone.now() + timedelta(days=2)
    date_retour = timezone.now() + timedelta(days=7)
    
    # Renvoyer ces dates sous forme de JSON
    return JsonResponse({
        'date_retrait': date_retrait.strftime('%Y-%m-%d'),
        'date_limite_retrait': date_limite_retrait.strftime('%Y-%m-%d'),
        'date_retour': date_retour.strftime('%Y-%m-%d')
    })
from django.utils import timezone
from datetime import timedelta

def dates_prevision(request):
    date_retrait = timezone.now().strftime("%d/%m/%Y")
    date_limite_retrait = (timezone.now() + timedelta(days=2)).strftime("%d/%m/%Y")
    date_retour = (timezone.now() + timedelta(days=14)).strftime("%d/%m/%Y")
    
    return JsonResponse({
        'date_retrait': date_retrait,
        'date_limite_retrait': date_limite_retrait,
        'date_retour': date_retour
    })





from .forms import LivreForm
from django.contrib.auth.decorators import user_passes_test

# Fonction de sécurité : uniquement les utilisateurs avec is_staff = True
def is_admin(user):
    return user.is_authenticated and user.is_staff


@user_passes_test(is_admin)
def dashboard(request):
    total_livres = Livre.objects.count()
    total_categories = Categorie.objects.count()
    return render(request, 'admincustom/dashboard.html', {
        'total_livres': total_livres,
        'total_categories': total_categories
    })

@user_passes_test(is_admin)
def liste_livres(request):
    livres = Livre.objects.all()
    return render(request, 'admincustom/livres.html', {'livres': livres})

@user_passes_test(is_admin)
def ajouter_livre(request):
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('admin_livres')
    else:
        form = LivreForm()
    return render(request, 'admincustom/ajouter_livre.html', {'form': form})


# Vérifier si l'utilisateur est un "admin" simple (ex. staff ou groupe custom)
def is_simple_admin(user):
    return user.is_staff  # ou autre critère : user.groups.filter(name='AdminSimple').exists()

@login_required
@user_passes_test(is_simple_admin)
def dashboard_admin(request):
    livres = Livre.objects.all()
    emprunts = Emprunt.objects.all()
    utilisateurs = User.objects.all()
    paniers = Panier.objects.all()
    return render(request, 'admincustom/dashboard.html', {
        'livres': livres,
        'emprunts': emprunts,
        'utilisateurs': utilisateurs,
        'paniers': paniers,
    })

@login_required
@user_passes_test(is_simple_admin)
def livres_admin(request):
    livres = Livre.objects.all()
    return render(request, 'admincustom/livres.html', {'livres': livres})


@login_required
def emprunts_admin(request):
    emprunts = Emprunt.objects.select_related('livre', 'utilisateur').all()
    return render(request, 'admincustom/emprunts.html', {'emprunts': emprunts})

from .models import Panier

@login_required
def paniers_admin(request):
    paniers = Panier.objects.select_related('utilisateur').prefetch_related('livres').all()
    return render(request, 'admincustom/paniers.html', {'paniers': paniers})

from django.contrib.auth.models import User

@login_required
def utilisateurs_admin(request):
    utilisateurs = User.objects.annotate(nb_livres=Count('emprunt__livre')).all()
    return render(request, 'admincustom/utilisateurs.html', {'utilisateurs': utilisateurs})


@login_required
def livre_dans_panier(request, livre_id):
    """Vérifie si un livre est déjà dans le panier de l'utilisateur"""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    in_cart = panier.livres.filter(id=livre_id).exists()
    return JsonResponse({'in_cart': in_cart})

@login_required
def panier_count(request):
    """Renvoie le nombre d'articles dans le panier"""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    count = panier.livres.count()
    return JsonResponse({'count': count})

# views.py
@login_required
def panier_count(request):
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    count = panier.livres.count()
    return JsonResponse({'count': count})

@login_required
def ajouter_livre(request):
    form = LivreForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect('livres_admin')  # Crée cette vue ou change la redirection
    return render(request, 'admincustom/ajouter_livre.html', {'form': form})

@login_required
def modifier_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    form = LivreForm(request.POST or None, request.FILES or None, instance=livre)
    if form.is_valid():
        form.save()
        return redirect('livres_admin')
    return render(request, 'admincustom/modifier_livre.html', {'form': form})

@login_required
def supprimer_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    livre.delete()
    return redirect('livres_admin') 

# Tu peux faire la même chose pour les emprunts et utilisateurs :
@login_required
def ajouter_emprunt(request):
    form = EmpruntForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('admin_emprunts')
    return render(request, 'admincustom/ajouter_emprunt.html', {'form': form})

@login_required
def modifier_utilisateur(request, user_id):
    utilisateur = get_object_or_404(User, id=user_id)
    form = UtilisateurForm(request.POST or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        return redirect('admin_utilisateurs')
    return render(request, 'admincustom/modifier_utilisateur.html', {'form': form})



@login_required
def gestion_admin(request):
    return render(request, 'admincustom/gestion_admin.html')