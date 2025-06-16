# appbiblio/views.py

# Imports Django
from django.contrib.auth import login
from django.db import models, transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django import forms
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.utils.timezone import now # Importe 'now' de Django pour la gestion des fuseaux horaires
from django.utils import timezone # Assurez-vous que timezone est importé pour ses utilisations
from django.db import models
from django.db.models import Case, When, Value, BooleanField
from django.utils import timezone
import logging
from django.contrib import messages

# Imports Python standard
from datetime import timedelta, date # <-- C'EST ICI LA CORRECTION CRUCIALE pour date et timedelta

# Imports de vos applications locales
from .forms import UtilisateurForm, LivreForm, EmpruntForm # Assurez-vous d'importer tous les formulaires utilisés
from .models import Livre, Categorie, Emprunt, Panier, EmpruntPrevu, LignePanier, HistoriqueLivre


# Formulaire personnalisé pour l'inscription
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(label="Prénom", required=False)
    last_name = forms.CharField(label="Nom", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

# Fonction de sécurité : seuls les utilisateurs avec is_staff = True
def is_admin(user):
    """
    Vérifie si l'utilisateur est un administrateur (is_staff).
    """
    return user.is_authenticated and user.is_staff

def is_simple_admin(user):
    """
    Vérifie si l'utilisateur est un simple administrateur (is_staff).
    Cette fonction est identique à is_admin si votre distinction n'est pas plus complexe.
    """
    return user.is_authenticated and user.is_staff

## Vues publiques

def home(request):
    """
    Affiche la page d'accueil avec diverses statistiques sur les livres, les catégories et les utilisateurs.
    """
    categories = Categorie.objects.annotate(
        nombre_livres=Count('livres')
    ).all()

    livres = Livre.objects.all()

    # Calcul des statistiques
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    livres_empruntes = Livre.objects.filter(statut='emprunté').count()
    nombre_categories = Categorie.objects.count()
    membres_actifs = User.objects.filter(is_active=True).count()
    nombre_auteurs = Livre.objects.values('auteur').distinct().count()
    
    # En supposant que 'prix_litteraire' est un champ booléen dans votre modèle Livre
    prix_litteraires = Livre.objects.filter(prix_litteraire=True).count()
    
    livres_reserves = Livre.objects.filter(statut='réservé').count()
    livres_retournes = Emprunt.objects.filter(date_retour__isnull=False).count()

    return render(request, 'appbiblio/home.html', {
        'categories': categories,
        'livres': livres,
        'livres_disponibles': livres_disponibles,
        'livres_empruntes': livres_empruntes,
        'nombre_categories': nombre_categories,
        'membres_actifs': membres_actifs,
        'nombre_auteurs': nombre_auteurs,
        'prix_litteraires': prix_litteraires,
        'livres_reserves': livres_reserves,
        'livres_retournes': livres_retournes
    })

def livres_disponibles_ajax(request):
    """
    Renvoie le nombre de livres disponibles sous forme de réponse JSON.
    """
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    return JsonResponse({'livres_disponibles': livres_disponibles})

def register(request):
    """
    Gère l'inscription des utilisateurs.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            user.save()
            login(request, user)  # Connecte l'utilisateur après l'inscription
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'appbiblio/register.html', {'form': form})

def check_authentication(request):
    """
    Vérifie si l'utilisateur actuel est authentifié.
    Renvoie une réponse JSON indiquant le statut d'authentification.
    """
    return JsonResponse({'is_authenticated': request.user.is_authenticated})

def categorie_detail(request, categorie_id):
    """
    Affiche les détails d'une catégorie spécifique et de ses livres associés.
    """
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livres = categorie.livres.all()
    nombre_livres = livres.count()

    return render(request, 'appbiblio/categorie_detail.html', {
        'categorie': categorie,
        'livres': livres,
        'nombre_livres': nombre_livres
    })

def get_stats(request):
    """
    Renvoie des statistiques générales sous forme de réponse JSON.
    Note : Certains exemples statiques sont utilisés ici, ils devraient être remplacés par de vraies requêtes.
    """
    total_livres = Livre.objects.filter(statut='disponible').count()
    membres_actifs = User.objects.filter(is_active=True).count() # Exemple : vraie requête
    emprunts_mois = Emprunt.objects.filter(date_retrait__month=timezone.now().month, date_retrait__year=timezone.now().year).count()
    prix_litteraires = Livre.objects.filter(prix_litteraire=True).count()

    return JsonResponse({
        'livres_disponibles': total_livres,
        'membres_actifs': membres_actifs,
        'emprunts_par_mois': emprunts_mois,
        'prix_litteraires': prix_litteraires,
    })




# Configurez le logger en haut de votre fichier
logger = logging.getLogger(__name__)

@login_required
def historique_utilisateur(request):
    """Affiche l'historique complet des actions de l'utilisateur"""
    try:
        # Récupération des données
        panier_actif = LignePanier.objects.filter(
            panier__utilisateur=request.user
        ).select_related('livre')
        
        # Emprunts actifs avec annotation pour le statut de retard
        emprunts_actifs = Emprunt.objects.filter(
            utilisateur=request.user,
            date_retour__isnull=True
        ).annotate(
            en_retard=Case(
                When(date_limite_retrait__lt=timezone.now(), then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        ).select_related('livre')
        
        context = {
            'panier_actif': panier_actif,
            'livres_empruntes': emprunts_actifs,
            'livres_retournes': Emprunt.objects.filter(
                utilisateur=request.user,
                date_retour__isnull=False
            ).select_related('livre'),
            'livres_reserves': HistoriqueLivre.objects.filter(
                utilisateur=request.user,
                statut='réservé'
            ).select_related('livre'),
            'now': timezone.now(),
        }
        
        return render(request, 'appbiblio/historique.html', context)
        
    except Exception as e:
        logger.error(f"Erreur historique utilisateur: {str(e)}", exc_info=True)
        messages.error(request, "Une erreur est survenue lors de la récupération de votre historique.")
        return redirect('home')

def statistics_view(request):
    """
    Renvoie diverses statistiques de la bibliothèque sous forme de réponse JSON.
    """
    livres_disponibles = Livre.objects.filter(statut='disponible').count()
    livres_empruntes = Emprunt.objects.filter(date_retrait__isnull=False, date_retour__isnull=True).count() # Prêts actifs
    nombre_categories = Categorie.objects.count()
    nombre_auteurs = Livre.objects.values('auteur').distinct().count()
    membres_actifs = User.objects.filter(is_active=True).count()
    emprunts_par_mois = Emprunt.objects.filter(date_retrait__month=timezone.now().month).count()
    prix_litteraires = Livre.objects.filter(prix_litteraire=True).count()

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
    """
    Affiche les livres appartenant à une catégorie spécifique.
    """
    categorie = get_object_or_404(Categorie, nom=nom_categorie)
    livres = Livre.objects.filter(categorie=categorie)
    nombre_livres = livres.count()

    return render(request, 'appbiblio/categorie_detail.html', {
        'categorie': categorie,
        'livres': livres,
        'nombre_livres': nombre_livres
    })

def stats_view(request):
    """
    Affiche une page avec des statistiques générales de la bibliothèque.
    """
    total_livres = Livre.objects.count()
    livres_empruntes = Emprunt.objects.filter(date_retrait__isnull=False, date_retour__isnull=True).count()
    total_categories = Categorie.objects.count()
    total_auteurs = Livre.objects.values('auteur').distinct().count()
    
    return render(request, 'stats.html', {
        'total_livres': total_livres,
        'livres_empruntes': livres_empruntes,
        'total_categories': total_categories,
        'total_auteurs': total_auteurs
    })

## Vues de gestion du panier et des emprunts

@login_required
@require_POST
@transaction.atomic
def ajouter_au_panier(request, livre_id):
    """
    Ajoute un livre au panier (Panier) de l'utilisateur et définit son statut sur 'réservé'.
    Crée également un enregistrement EmpruntPrevu.
    """
    try:
        livre = get_object_or_404(Livre, id=livre_id)
        user = request.user

        panier, created_panier = Panier.objects.get_or_create(utilisateur=user)

        if LignePanier.objects.filter(panier=panier, livre=livre).exists():
            messages.info(request, f'Le livre "{livre.titre}" est déjà dans votre panier.')
            return JsonResponse({'success': False, 'message': 'Ce livre est déjà dans votre panier.', 'in_cart': True}, status=200)

        if livre.statut != 'disponible':
            messages.warning(request, f'Le livre "{livre.titre}" est actuellement {livre.statut}. Il ne peut pas être réservé.')
            return JsonResponse({'success': False, 'message': f'Le livre "{livre.titre}" est actuellement {livre.statut}. Il ne peut pas être réservé.'}, status=400)

        LignePanier.objects.create(panier=panier, livre=livre, quantite=1)

        livre.statut = 'réservé'
        livre.save()

        date_prevue_retrait_calcul = date.today()
        date_prevue_retour_calculee = date.today() + timedelta(days=14)

        EmpruntPrevu.objects.create(
            utilisateur=user,
            livre=livre,
            date_prevue_retrait=date_prevue_retrait_calcul,
            date_prevue_retour=date_prevue_retour_calculee
        )

        messages.success(request, f"'{livre.titre}' a été ajouté à votre panier et réservé.")
        return JsonResponse({
            'success': True,
            'message': f"'{livre.titre}' a été ajouté à votre panier et est maintenant réservé.",
            'new_status': 'réservé',
            'in_cart': True
        }, status=200)

    except Exception as e:
        print(f"Erreur dans la vue ajouter_au_panier : {e}")
        messages.error(request, f"Erreur lors de l'ajout au panier : {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erreur lors de l\'ajout au panier : {str(e)}'}, status=500)

@login_required
def voir_panier(request):
    """
    Affiche la page du panier de l'utilisateur.
    """
    panier, _ = Panier.objects.get_or_create(utilisateur=request.user)
    return render(request, 'appbiblio/panier.html', {'panier': panier})

@login_required
@require_POST
@transaction.atomic
def supprimer_panier(request, livre_id):
    """
    Supprime un livre du panier de l'utilisateur et de son EmpruntPrevu associé,
    et potentiellement rétablit le statut du livre à 'disponible'.
    """
    try:
        livre = get_object_or_404(Livre, id=livre_id)
        user = request.user

        panier = get_object_or_404(Panier, utilisateur=user)

        ligne_panier = get_object_or_404(LignePanier, panier=panier, livre=livre)
        ligne_panier.delete()

        EmpruntPrevu.objects.filter(utilisateur=user, livre=livre).delete()

        # Rétablit le statut du livre à 'disponible' uniquement s'il n'est pas réservé/emprunté par quelqu'un d'autre
        if not (LignePanier.objects.filter(livre=livre).exists() or
                EmpruntPrevu.objects.filter(livre=livre).exists() or
                Emprunt.objects.filter(livre=livre, date_retour__isnull=True).exists()):
            livre.statut = 'disponible'
            livre.save()
            new_status_text = 'disponible'
        else:
            new_status_text = livre.statut

        messages.info(request, f"'{livre.titre}' a été retiré de votre panier.")
        return JsonResponse({
            'success': True,
            'message': f"'{livre.titre}' a été retiré de votre panier.",
            'new_status': new_status_text,
            'in_cart': False
        }, status=200)

    except Panier.DoesNotExist:
        messages.error(request, 'Panier non trouvé pour cet utilisateur.')
        return JsonResponse({'success': False, 'message': 'Panier non trouvé pour cet utilisateur.'}, status=404)
    except LignePanier.DoesNotExist:
        messages.warning(request, 'Ce livre n\'était pas dans votre panier.')
        return JsonResponse({'success': False, 'message': 'Ce livre n\'était pas dans votre panier.'}, status=404)
    except Exception as e:
        print(f"Erreur dans la vue supprimer_panier : {e}")
        messages.error(request, f"Erreur lors du retrait du panier : {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erreur lors du retrait du panier : {str(e)}'}, status=500)

@login_required
@transaction.atomic
def valider_panier(request):
    """
    Valide les éléments du panier de l'utilisateur, convertissant les EmpruntPrevu en enregistrements Emprunt réels,
    mettant à jour les statuts des livres et vidant le panier.
    """
    panier = get_object_or_404(Panier, utilisateur=request.user)
    
    lignes_panier = LignePanier.objects.filter(panier=panier)

    if not lignes_panier.exists():
        messages.warning(request, "Votre panier est vide. Aucun emprunt à valider.")
        return redirect('home')

    for ligne in lignes_panier:
        livre = ligne.livre
        
        emprunt_prevu = get_object_or_404(EmpruntPrevu, utilisateur=request.user, livre=livre)
        
        Emprunt.objects.create(
            utilisateur=request.user,
            livre=livre,
            date_retrait=emprunt_prevu.date_prevue_retrait,
            date_retour=emprunt_prevu.date_prevue_retour,
            date_limite_retrait=emprunt_prevu.date_prevue_retrait + timedelta(days=2) 
        )
        
        livre.statut = 'emprunté'
        livre.save()
        
        emprunt_prevu.delete()
    
    lignes_panier.delete()

    messages.success(request, "Votre emprunt a été validé avec succès !")
    return redirect('home')

@login_required
def mon_panier(request):
    """
    Affiche le contenu du panier de l'utilisateur, y compris les dates de réservation et les détails du livre.
    """
    try:
        panier = get_object_or_404(Panier, utilisateur=request.user)
    except Exception as e:
        messages.error(request, "Impossible de trouver votre panier.")
        return redirect('home')

    lignes_panier = LignePanier.objects.filter(panier=panier).select_related('livre')
    
    lignes_enrichies = []
    for ligne in lignes_panier:
        emprunt_prevu = EmpruntPrevu.objects.filter(
            utilisateur=request.user, 
            livre=ligne.livre
        ).first()
        
        ligne_data = {
            'id': ligne.id,
            'livre': ligne.livre,
            'date_reservation': emprunt_prevu.date_prevue_retrait if emprunt_prevu else date.today(),
            'prix': ligne.livre.prix,
            'statut_actuel': ligne.livre.statut,
            'isbn': ligne.livre.isbn,
            'categorie': ligne.livre.categorie.nom if ligne.livre.categorie else "Non classé"
        }
        lignes_enrichies.append(ligne_data)

    return render(request, 'appbiblio/panier.html', {
        'panier': panier,
        'lignes_panier': lignes_enrichies
    })
@login_required
@transaction.atomic
def vider_panier(request):
    panier = get_object_or_404(Panier, utilisateur=request.user)
    lignes_panier = LignePanier.objects.filter(panier=panier)
    
    if not lignes_panier.exists():
        messages.warning(request, "Votre panier est déjà vide")
        return redirect('historique')
    
    # Supprimer les emprunts prévus associés
    EmpruntPrevu.objects.filter(
        utilisateur=request.user,
        livre__in=[ligne.livre for ligne in lignes_panier]
    ).delete()
    
    # Vider le panier
    lignes_panier.delete()
    
    messages.success(request, "Votre panier a été vidé avec succès")
    return redirect('historique')

@login_required
def commandes_utilisateur(request):
    """
    Affiche les prêts validés et en attente pour l'utilisateur actuel.
    """
    utilisateur = request.user
    emprunts_valides = Emprunt.objects.filter(utilisateur=utilisateur).order_by('-date_retrait')
    emprunts_non_valides = EmpruntPrevu.objects.filter(utilisateur=utilisateur).order_by('-date_prevue_retrait')

    return render(request, 'appbiblio/historique_emprunts.html', {
        'emprunts_valides': emprunts_valides,
        'emprunts_non_valides': emprunts_non_valides
    })

def dates_prevision(request):
    """
    Renvoie les dates de prêt prévues sous forme de réponse JSON.
    """
    date_retrait = timezone.now().strftime("%d/%m/%Y")
    date_limite_retrait = (timezone.now() + timedelta(days=2)).strftime("%d/%m/%Y")
    date_retour = (timezone.now() + timedelta(days=14)).strftime("%d/%m/%Y")
    
    return JsonResponse({
        'date_retrait': date_retrait,
        'date_limite_retrait': date_limite_retrait,
        'date_retour': date_retour
    })

@login_required
def livre_dans_panier(request, livre_id):
    """Vérifie si un livre est déjà dans le panier de l'utilisateur."""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    # Correction: Utilisation de 'lignes_panier' pour filtrer les livres dans le panier
    in_cart = panier.lignes_panier.filter(livre__id=livre_id).exists()
    return JsonResponse({'in_cart': in_cart})

@login_required
def panier_count(request):
    """Renvoie le nombre d'articles distincts dans le panier de l'utilisateur."""
    panier, created = Panier.objects.get_or_create(utilisateur=request.user)
    # Correction: Utilisation de 'lignes_panier' pour compter les éléments dans le panier
    count = LignePanier.objects.filter(panier=panier).count()
    return JsonResponse({'count': count})

@login_required
@require_POST
@transaction.atomic
def supprimer_ligne_panier(request, ligne_id):
    """
    Supprime une ligne spécifique du panier de l'utilisateur.
    Gère également la suppression de l'EmpruntPrevu associé et le statut du livre.
    """
    try:
        ligne = get_object_or_404(LignePanier, id=ligne_id, panier__utilisateur=request.user)
        livre = ligne.livre
        
        ligne.delete()
        
        # Supprimer la réservation associée
        EmpruntPrevu.objects.filter(utilisateur=request.user, livre=livre).delete()
        
        # Libérer le livre si plus de réservations (vérifie également les emprunts actifs pour ne pas le libérer par erreur)
        if not (LignePanier.objects.filter(livre=livre).exists() or
                EmpruntPrevu.objects.filter(livre=livre).exists() or
                Emprunt.objects.filter(livre=livre, date_retour__isnull=True).exists()):
            livre.statut = 'disponible'
            livre.save()

        messages.info(request, f"'{livre.titre}' a été retiré de votre collection.")
        return JsonResponse({
            'success': True,
            'message': f"'{livre.titre}' a été retiré de votre collection",
            'new_status': livre.statut # Retourne le nouveau statut du livre
        }, status=200)

    except Exception as e:
        messages.error(request, f"Erreur lors de la suppression : {str(e)}")
        return JsonResponse({
            'success': False,
            'message': f"Erreur lors de la suppression : {str(e)}"
        }, status=500)

## Vues d'administration

@user_passes_test(is_admin)
def dashboard(request):
    """
    Vue du tableau de bord de l'administrateur affichant les statistiques globales de la bibliothèque.
    """
    total_livres = Livre.objects.count()
    total_categories = Categorie.objects.count()
    return render(request, 'admincustom/dashboard.html', {
        'total_livres': total_livres,
        'total_categories': total_categories
    })

@user_passes_test(is_admin)
def liste_livres(request):
    """
    Vue d'administration pour lister tous les livres.
    """
    livres = Livre.objects.all()
    return render(request, 'admincustom/livres.html', {'livres': livres})

@login_required
@user_passes_test(is_admin) # Ajout du décorateur de sécurité
def ajouter_livre(request):
    """
    Vue d'administration pour ajouter un nouveau livre.
    """
    form = LivreForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, "Livre ajouté avec succès!")
        return redirect('admin_livres')  # Assurez-vous que cette URL existe
    return render(request, 'admincustom/ajouter_livre.html', {'form': form})

@login_required
@user_passes_test(is_admin) # Ajout du décorateur de sécurité
def modifier_livre(request, livre_id):
    """
    Vue d'administration pour modifier un livre existant.
    """
    livre = get_object_or_404(Livre, id=livre_id)
    form = LivreForm(request.POST or None, request.FILES or None, instance=livre)
    if form.is_valid():
        form.save()
        messages.success(request, f"Livre '{livre.titre}' modifié avec succès!")
        return redirect('livres_admin')
    return render(request, 'admincustom/modifier_livre.html', {'form': form})

@login_required
@user_passes_test(is_admin)  # Accès réservé aux admins
@transaction.atomic # S'assurer que les opérations sont atomiques
def supprimer_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    
    # Vérifier si le livre peut être supprimé
    if Emprunt.objects.filter(livre=livre, date_retour__isnull=True).exists():
        messages.error(request, "Impossible de supprimer ce livre car il est actuellement emprunté.")
        return redirect('admin_livres') # Assurez-vous que cette URL existe
    
    # Supprimer les réservations associées
    EmpruntPrevu.objects.filter(livre=livre).delete()
    
    # Supprimer les lignes de panier associées
    LignePanier.objects.filter(livre=livre).delete()
    
    # Supprimer le livre
    livre.delete()
    
    messages.success(request, f"Le livre '{livre.titre}' a été supprimé avec succès.")
    return redirect('livres_admin')


@login_required
@user_passes_test(is_simple_admin)
def dashboard_admin(request):
    """
    Tableau de bord de l'administrateur pour les utilisateurs du personnel, affichant les listes de livres, d'emprunts, d'utilisateurs et de paniers.
    """
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
    """
    Vue d'administration pour lister tous les livres pour les utilisateurs du personnel.
    """
    livres = Livre.objects.all()
    return render(request, 'admincustom/livres.html', {'livres': livres})

@login_required
@user_passes_test(is_admin) # Garantit que seul un administrateur peut accéder
def emprunts_admin(request):
    """
    Vue d'administration pour lister tous les emprunts, avec les informations de livre et d'utilisateur associées.
    """
    emprunts = Emprunt.objects.select_related('livre', 'utilisateur').all().order_by('-date_retrait')
    return render(request, 'admincustom/emprunts.html', {'emprunts': emprunts})

@login_required
@user_passes_test(is_admin)
def paniers_admin(request):
    """
    Vue d'administration pour gérer et examiner les paniers des utilisateurs et les demandes de prêt.
    Comprend des statistiques sur les paniers actifs, les prêts validés, les prêts en attente et les livres retournés.
    """
    paniers_actifs_count = Panier.objects.annotate(
        num_livres=Count('lignes_panier__id')
    ).filter(num_livres__gt=0).count()

    emprunts_valides_count = Emprunt.objects.filter(date_retour__isnull=True).count()
    emprunts_attente_count = EmpruntPrevu.objects.all().count()
    livres_retournes_count = Emprunt.objects.filter(date_retour__isnull=False).count()

    all_paniers = Panier.objects.prefetch_related(
        'lignes_panier',
        'lignes_panier__livre',
        'utilisateur'
    ).all().order_by('-date_creation')

    paniers_data = []
    for panier in all_paniers:
        livres_dans_panier = []
        date_demande = None
        statut_panier = 'vide'

        for ligne_panier in panier.lignes_panier.all():
            livre = ligne_panier.livre
            
            emprunt_prevu = EmpruntPrevu.objects.filter(
                utilisateur=panier.utilisateur,
                livre=livre
            ).first()

            emprunt_actif = Emprunt.objects.filter(
                utilisateur=panier.utilisateur,
                livre=livre,
                date_retour__isnull=True
            ).first()

            livre_status_display = livre.statut

            if emprunt_actif:
                request_status = 'emprunté'
                request_date = emprunt_actif.date_retrait
            elif emprunt_prevu:
                request_status = 'réservé'
                request_date = emprunt_prevu.date_prevue_retrait
            else:
                request_status = 'inconnu'
                request_date = None

            livres_dans_panier.append({
                'id': livre.id,
                'titre': livre.titre,
                'auteur': livre.auteur,
                'status': request_status,
                'book_status': livre_status_display,
                'emprunt_date': request_date,
            })
            
            if date_demande is None or (panier.date_creation and panier.date_creation.date() < date_demande):
                date_demande = panier.date_creation.date()

        if any(l['status'] == 'emprunté' for l in livres_dans_panier):
            statut_panier = 'validé'
        elif any(l['status'] == 'réservé' for l in livres_dans_panier):
            statut_panier = 'en attente'
        else:
            statut_panier = 'vide'

        paniers_data.append({
            'panier_obj': panier,
            'utilisateur': panier.utilisateur,
            'livres_details': livres_dans_panier,
            'date_demande': date_demande if date_demande else panier.date_creation.date(),
            'statut_global': statut_panier,
            'first_loan_date': next((l['emprunt_date'] for l in livres_dans_panier if l['emprunt_date']), None)
        })

    context = {
        'paniers': paniers_data,
        'paniers_actifs': paniers_actifs_count,
        'emprunts_valides': emprunts_valides_count,
        'emprunts_attente': emprunts_attente_count,
        'total_livres_retournes': livres_retournes_count,
    }
    return render(request, 'admincustom/paniers.html', context)

@login_required
@user_passes_test(is_admin)
@require_POST
@transaction.atomic
def valider_emprunt_admin(request, livre_id, user_id):
    """
    Action d'administration pour valider une demande de prêt en attente (EmpruntPrevu),
    la convertissant en un Emprunt réel et mettant à jour le statut du livre.
    """
    try:
        user = get_object_or_404(User, id=user_id) # Utilisation directe du modèle User
        livre = get_object_or_404(Livre, id=livre_id)

        emprunt_prevu = get_object_or_404(EmpruntPrevu, utilisateur=user, livre=livre)

        if livre.statut != 'réservé':
            messages.error(request, f"Le livre '{livre.titre}' n'est pas en statut 'réservé'. Impossible de valider.")
            return JsonResponse({'success': False, 'message': 'Statut du livre incompatible.'}, status=400)

        date_retrait = date.today()
        date_retour_prevue = emprunt_prevu.date_prevue_retour
        date_limite_retrait = date_retrait + timedelta(days=2)

        Emprunt.objects.create(
            utilisateur=user,
            livre=livre,
            date_retrait=date_retrait,
            date_retour=None,
            date_limite_retrait=date_limite_retrait
        )

        livre.statut = 'emprunté'
        livre.save()

        emprunt_prevu.delete()
        panier = Panier.objects.get(utilisateur=user)
        LignePanier.objects.filter(panier=panier, livre=livre).delete()


        messages.success(request, f"L'emprunt pour '{livre.titre}' par {user.username} a été validé et le livre est maintenant 'emprunté'.")
        return JsonResponse({'success': True, 'message': 'Emprunt validé.', 'new_status': 'emprunté'})

    except Livre.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Livre non trouvé.'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé.'}, status=404)
    except EmpruntPrevu.DoesNotExist:
        messages.error(request, f"Aucune réservation en attente trouvée pour '{livre.titre}' par {user.username}.")
        return JsonResponse({'success': False, 'message': 'Réservation non trouvée.'}, status=404)
    except Exception as e:
        messages.error(request, f"Erreur lors de la validation de l'emprunt : {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_admin)
@require_POST
@transaction.atomic
def refuser_emprunt_admin(request, livre_id, user_id):
    """
    Action d'administration pour refuser une demande de prêt en attente (EmpruntPrevu),
    supprimant la demande et potentiellement rétablissant le statut du livre.
    """
    try:
        user = get_object_or_404(User, id=user_id) # Utilisation directe du modèle User
        livre = get_object_or_404(Livre, id=livre_id)

        emprunt_prevu = get_object_or_404(EmpruntPrevu, utilisateur=user, livre=livre)

        emprunt_prevu.delete()

        if not (LignePanier.objects.filter(livre=livre).exists() or
                EmpruntPrevu.objects.filter(livre=livre).exists() or
                Emprunt.objects.filter(livre=livre, date_retour__isnull=True).exists()):
            livre.statut = 'disponible'
            livre.save()
            new_book_status = 'disponible'
        else:
            new_book_status = livre.statut

        panier = Panier.objects.get(utilisateur=user)
        LignePanier.objects.filter(panier=panier, livre=livre).delete()


        messages.info(request, f"La réservation pour '{livre.titre}' par {user.username} a été refusée.")
        return JsonResponse({'success': True, 'message': 'Réservation refusée.', 'new_status': 'refusé', 'book_status': new_book_status})

    except Livre.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Livre non trouvé.'}, status=404)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Utilisateur non trouvé.'}, status=404)
    except EmpruntPrevu.DoesNotExist:
        messages.error(request, f"Aucune réservation en attente trouvée pour '{livre.titre}' par {user.username}.")
        return JsonResponse({'success': False, 'message': 'Réservation non trouvée.'}, status=404)
    except Exception as e:
        messages.error(request, f"Erreur lors du refus de l'emprunt : {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_admin)
@require_POST
@transaction.atomic
def marquer_retourne_admin(request, emprunt_id):
    """
    Action d'administration pour marquer un prêt actif comme retourné.
    Met à jour l'enregistrement du prêt et potentiellement rétablit le statut du livre.
    """
    try:
        emprunt = get_object_or_404(Emprunt, id=emprunt_id)

        if emprunt.date_retour is not None:
            messages.warning(request, f"L'emprunt pour '{emprunt.livre.titre}' est déjà marqué comme retourné.")
            return JsonResponse({'success': False, 'message': 'Livre déjà retourné.'}, status=400)

        emprunt.date_retour = date.today()
        emprunt.save()

        if not (LignePanier.objects.filter(livre=emprunt.livre).exists() or
                EmpruntPrevu.objects.filter(livre=emprunt.livre).exists() or
                Emprunt.objects.filter(livre=emprunt.livre, date_retour__isnull=True).exclude(id=emprunt_id).exists()):
            emprunt.livre.statut = 'disponible'
            emprunt.livre.save()
            new_book_status = 'disponible'
        else:
            new_book_status = emprunt.livre.statut


        messages.success(request, f"'{emprunt.livre.titre}' emprunté par {emprunt.utilisateur.username} a été marqué comme retourné.")
        return JsonResponse({'success': True, 'message': 'Livre marqué comme retourné.', 'new_status': 'retourné', 'book_status': new_book_status})

    except Emprunt.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Emprunt non trouvé.'}, status=404)
    except Exception as e:
        messages.error(request, f"Erreur lors du marquage comme retourné : {str(e)}")
        return JsonResponse({'success': False, 'message': f'Erreur: {str(e)}'}, status=500)

@login_required
@user_passes_test(is_admin) # Ajout du décorateur pour restreindre l'accès
def utilisateurs_admin(request):
    """
    Vue d'administration pour lister tous les utilisateurs, avec le nombre de livres qu'ils ont empruntés.
    """
    utilisateurs = User.objects.annotate(
        nb_livres_empruntes=Count('emprunt', filter=Q(emprunt__date_retour__isnull=True))
    ).all().order_by('username')
    
    return render(request, 'admincustom/utilisateurs.html', {'utilisateurs': utilisateurs})

@login_required
@user_passes_test(is_admin) # Ajout du décorateur de sécurité
def ajouter_emprunt(request):
    """
    Vue d'administration pour ajouter un nouvel emprunt manuellement.
    """
    form = EmpruntForm(request.POST or None)
    if form.is_valid():
        emprunt = form.save(commit=False)
        # Mettre à jour le statut du livre à "emprunté" si ce n'est pas déjà le cas
        if emprunt.livre.statut != 'emprunté':
            emprunt.livre.statut = 'emprunté'
            emprunt.livre.save()
        emprunt.save()
        messages.success(request, "Emprunt ajouté avec succès!")
        return redirect('admin_emprunts') # Assurez-vous que cette URL existe
    return render(request, 'admincustom/ajouter_emprunt.html', {'form': form})

@login_required
@user_passes_test(is_admin) # Ajout du décorateur de sécurité
def modifier_utilisateur(request, user_id):
    """
    Vue d'administration pour modifier les informations d'un utilisateur.
    """
    utilisateur = get_object_or_404(User, id=user_id)
    form = UtilisateurForm(request.POST or None, instance=utilisateur)
    if form.is_valid():
        form.save()
        messages.success(request, f"Utilisateur '{utilisateur.username}' modifié avec succès!")
        return redirect('admin_utilisateurs') # Assurez-vous que cette URL existe
    return render(request, 'admincustom/modifier_utilisateur.html', {'form': form})

@login_required
@user_passes_test(is_simple_admin)
def gestion_admin(request):
    """
    Vue du tableau de bord d'administration générale.
    """
    return render(request, 'admincustom/gestion_admin.html')