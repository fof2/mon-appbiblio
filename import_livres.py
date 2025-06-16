import os
import django
import requests
from django.core.files import File
from tempfile import NamedTemporaryFile
from urllib.parse import urlparse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monbiblio.settings')
django.setup()

from appbiblio.models import Livre, Categorie

def download_image(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()
        return response.content
    except Exception as e:
        print(f"Erreur de téléchargement: {str(e)}")
        return None

def importer_livres():
    livres_data = [
    

    {
        'titre': 'Pride and Prejudice',
        'auteur': 'Jane Austen',
        'categorie': 'Classique',
        'isbn': '9780141439518',
        'prix': 9.00,
        'date_publication': '2002-12-31',
        'description': 'Comédie de mœurs anglaise du XIXe siècle.',
        'couverture_url': 'https://covers.openlibrary.org/b/isbn/9780141439518-L.jpg',
        'statut': 'réservé'
    },
    {
        'titre': 'The Count of Monte Cristo',
        'auteur': 'Alexandre Dumas',
        'categorie': 'Classique',
        'isbn': '9780140449266',
        'prix': 14.00,
        'date_publication': '2003-05-27',
        'description': 'Roman d’aventure et de vengeance napoléonienne.',
        'couverture_url': 'https://covers.openlibrary.org/b/isbn/9780140449266-L.jpg',
        'statut': 'disponible'
    },
    {
        'titre': 'The Bhagavad Gita',
        'auteur': 'Anonymous',
        'categorie': 'Philosophie',
        'isbn': '9780140449181',
        'prix': 12.00,
        'date_publication': '2003-02-25',
        'description': 'Texte sacré hindou, dialogue entre Arjuna et Krishna.',
        'couverture_url': 'https://covers.openlibrary.org/b/isbn/9780140449181-L.jpg',
        'statut': 'emprunté'
    },
    {
        'titre': 'The Fellowship of the Ring',
        'auteur': 'J.R.R. Tolkien',
        'categorie': 'Fantasy',
        'isbn': '9780261103573',
        'prix': 11.00,
        'date_publication': '2011-01-01',
        'description': 'Début de l’épopée de la Terre du Milieu.',
        'couverture_url': 'https://covers.openlibrary.org/b/isbn/9780261103573-L.jpg',
        'statut': 'en_reparation'
    },
    {
        'titre': 'The Iliad',
        'auteur': 'Homer, trad. Robert Fagles',
        'categorie': 'Classique',
        'isbn': '9780140275360',
        'prix': 21.00,
        'date_publication': '1998-11-01',
        'description': 'Épopée grecque sur le siège de Troie, traduction en vers modernes.',
        'couverture_url': 'https://covers.openlibrary.org/b/isbn/9780140275360-L.jpg',
        'statut': 'réservé'
    },



    ]

    for livre_data in livres_data:
        print(f"\nTraitement: {livre_data['titre']}")
        
        if Livre.objects.filter(isbn=livre_data['isbn']).exists():
            print("✓ Existe déjà")
            continue

        categorie, _ = Categorie.objects.get_or_create(nom=livre_data['categorie'])

        livre = Livre(
            titre=livre_data['titre'],
            auteur=livre_data['auteur'],
            categorie=categorie,
            isbn=livre_data['isbn'],
            prix=livre_data['prix'],
            date_publication=livre_data['date_publication'],
            description=livre_data['description'],
            couverture_url=livre_data['couverture_url'],
            statut='disponible'
        )

        if livre_data.get('couverture_url'):
            image_data = download_image(livre_data['couverture_url'])
            if image_data:
                img_temp = NamedTemporaryFile(delete=True)
                img_temp.write(image_data)
                img_temp.flush()
                
                filename = f"{livre_data['isbn']}.jpg"
                livre.couverture.save(filename, File(img_temp))
                img_temp.close()
                print("✓ Couverture importée")
            else:
                print("✗ Échec couverture")

        livre.save()
        print(f"✓ Enregistré: {livre.titre}")

if __name__ == '__main__':
    print("\n=== DÉBUT IMPORTATION ===")
    importer_livres()
    print("\n=== IMPORTATION TERMINÉE ===")