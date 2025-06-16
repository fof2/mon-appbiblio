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
        # Classiques
        {
            'titre': 'L\'Étranger',
            'auteur': 'Albert Camus',
            'categorie': 'Littérature',
            'isbn': '9782070360024',
            'prix': 7.50,
            'date_publication': '1942-01-01',
            'description': 'Roman existentialiste sur la vie et la mort d\'un homme indifférent.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070360024-L.jpg'
        },
        {
            'titre': 'Madame Bovary',
            'auteur': 'Gustave Flaubert',
            'categorie': 'Classique',
            'isbn': '9782070413081',
            'prix': 9.20,
            'date_publication': '1856-01-01',
            'description': 'Histoire d\'une femme insatisfaite de sa vie provinciale.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070413081-L.jpg'
        },

        # Science-Fiction
        {
            'titre': 'Dune',
            'auteur': 'Frank Herbert',
            'categorie': 'Science-Fiction',
            'isbn': '9782253064066',
            'prix': 14.90,
            'date_publication': '1965-01-01',
            'description': 'Épopée intergalactique sur la planète désertique Arrakis.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782253064066-L.jpg'
        },
        {
            'titre': 'Fondation',
            'auteur': 'Isaac Asimov',
            'categorie': 'Science-Fiction',
            'isbn': '9782070413463',
            'prix': 12.00,
            'date_publication': '1951-01-01',
            'description': 'Chute d\'un empire galactique et science de la psychohistoire.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070413463-L.jpg'
        },

        # Fantastique
        {
            'titre': 'Le Hobbit',
            'auteur': 'J.R.R. Tolkien',
            'categorie': 'Fantasy',
            'isbn': '9782266282942',
            'prix': 11.50,
            'date_publication': '1937-01-01',
            'description': 'Aventure de Bilbo le Hobbit pour reconquérir un trésor.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782266282942-L.jpg'
        },

        # Philosophie
        {
            'titre': 'Ainsi parlait Zarathoustra',
            'auteur': 'Friedrich Nietzsche',
            'categorie': 'Philosophie',
            'isbn': '9782080709316',
            'prix': 10.80,
            'date_publication': '1883-01-01',
            'description': 'Ouvre majeure de Nietzsche sur le surhomme.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782080709316-L.jpg'
        },

        # Romans contemporains
        {
            'titre': 'La Trilogie new-yorkaise',
            'auteur': 'Paul Auster',
            'categorie': 'Roman',
            'isbn': '9782020313930',
            'prix': 15.00,
            'date_publication': '1987-01-01',
            'description': 'Trois histoires policières métaphysiques.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782020313930-L.jpg'
        },
        {
            'titre': 'Les Bienveillantes',
            'auteur': 'Jonathan Littell',
            'categorie': 'Historique',
            'isbn': '9782070780978',
            'prix': 25.00,
            'date_publication': '2006-01-01',
            'description': 'Roman choc sur un officier SS durant la Seconde Guerre mondiale.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070780978-L.jpg'
        },

        # Polar/Thriller
        {
            'titre': 'Millénium 1 - Les Hommes qui n\'aimaient pas les femmes',
            'auteur': 'Stieg Larsson',
            'categorie': 'Polar',
            'isbn': '9782020515044',
            'prix': 13.50,
            'date_publication': '2005-01-01',
            'description': 'Enquête sur des disparitions mystérieuses en Suède.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782020515044-L.jpg'
        },

        # Littérature africaine
        {
            'titre': 'L\'Enfant noir',
            'auteur': 'Camara Laye',
            'categorie': 'Autobiographie',
            'isbn': '9782266116490',
            'prix': 8.90,
            'date_publication': '1953-01-01',
            'description': 'Enfance en Guinée pendant la période coloniale.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782266116490-L.jpg'
        },

        # Plus de classiques
        {
            'titre': 'Les Misérables',
            'auteur': 'Victor Hugo',
            'categorie': 'Classique',
            'isbn': '9782070409228',
            'prix': 12.00,
            'date_publication': '1862-01-01',
            'description': 'Épopée de Jean Valjean et Cosette dans la France du XIXe.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070409228-L.jpg'
        },
        {
            'titre': 'Bel-Ami',
            'auteur': 'Guy de Maupassant',
            'categorie': 'Classique',
            'isbn': '9782070419838',
            'prix': 9.50,
            'date_publication': '1885-01-01',
            'description': 'Ascension sociale d\'un homme ambitieux dans le Paris du XIXe.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070419838-L.jpg'
        },

        # Littérature asiatique
        {
            'titre': 'Le Dit du Genji',
            'auteur': 'Murasaki Shikibu',
            'categorie': 'Classique',
            'isbn': '9782253139116',
            'prix': 18.00,
            'date_publication': '1008-01-01',
            'description': 'Considéré comme le premier roman psychologique au monde (Japon XIe siècle).',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782253139116-L.jpg'
        },

        # Science-Fiction moderne
        {
            'titre': 'La Horde du Contrevent',
            'auteur': 'Alain Damasio',
            'categorie': 'Science-Fiction',
            'isbn': '9782070494866',
            'prix': 22.00,
            'date_publication': '2004-01-01',
            'description': 'Épopée d\'un groupe d\'élite dans un monde de vents extrêmes.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070494866-L.jpg'
        },

        # Littérature sud-américaine
        {
            'titre': 'L\'Amour aux temps du choléra',
            'auteur': 'Gabriel García Márquez',
            'categorie': 'Roman',
            'isbn': '9782020099095',
            'prix': 11.00,
            'date_publication': '1985-01-01',
            'description': 'Histoire d\'un amour qui dure cinquante ans.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782020099095-L.jpg'
        },

        # Philosophie moderne
        {
            'titre': 'Le Mythe de Sisyphe',
            'auteur': 'Albert Camus',
            'categorie': 'Philosophie',
            'isbn': '9782070322886',
            'prix': 9.80,
            'date_publication': '1942-01-01',
            'description': 'Essai sur l\'absurde et le sens de la vie.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070322886-L.jpg'
        },

        # Biographie
        {
            'titre': 'Steve Jobs',
            'auteur': 'Walter Isaacson',
            'categorie': 'Biographie',
            'isbn': '9782221112611',
            'prix': 24.00,
            'date_publication': '2011-01-01',
            'description': 'Biographie officielle du cofondateur d\'Apple.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782221112611-L.jpg'
        },

        # Jeunesse
        {
            'titre': 'Le Petit Nicolas',
            'auteur': 'René Goscinny',
            'categorie': 'Jeunesse',
            'isbn': '9782070612750',
            'prix': 8.00,
            'date_publication': '1959-01-01',
            'description': 'Aventures d\'un écolier espiègle dans les années 50.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070612750-L.jpg'
        },

        # Théâtre
        {
            'titre': 'En attendant Godot',
            'auteur': 'Samuel Beckett',
            'categorie': 'Théâtre',
            'isbn': '9782070414346',
            'prix': 9.00,
            'date_publication': '1952-01-01',
            'description': 'Pièce emblématique du théâtre de l\'absurde.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070414346-L.jpg'
        },

        # Poésie
        {
            'titre': 'Les Fleurs du Mal',
            'auteur': 'Charles Baudelaire',
            'categorie': 'Poésie',
            'isbn': '9782070105507',
            'prix': 7.50,
            'date_publication': '1857-01-01',
            'description': 'Recueil poétique majeur du XIXe siècle.',
            'couverture_url': 'https://covers.openlibrary.org/b/isbn/9782070105507-L.jpg'
        }
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