from django.core.management.base import BaseCommand
from appbiblio.models import Livre
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Supprime les livres sans image de couverture valide'

    def handle(self, *args, **options):
        # 1. Vérifier les livres sans champ couverture
        qs = Livre.objects.filter(couverture='') | Livre.objects.filter(couverture__isnull=True)
        count_db = qs.count()
        
        # 2. Vérifier les livres avec champ rempli mais fichier manquant
        books_with_missing_files = []
        for book in Livre.objects.exclude(couverture=''):
            if book.couverture:
                path = os.path.join(settings.MEDIA_ROOT, str(book.couverture))
                if not os.path.exists(path):
                    books_with_missing_files.append(book.id)
        
        count_missing_files = len(books_with_missing_files)
        total_problems = count_db + count_missing_files

        self.stdout.write(f"Livres sans couverture (DB): {count_db}")
        self.stdout.write(f"Livres avec fichier manquant: {count_missing_files}")
        self.stdout.write(f"Total à supprimer: {total_problems}")

        if total_problems == 0:
            self.stdout.write(self.style.SUCCESS("✅ Aucun problème détecté"))
            return

        if input("Voulez-vous voir la liste ? (oui/non): ").lower() == 'oui':
            for book in qs:
                self.stdout.write(f"- {book.titre} (champ vide/null)")
            for book_id in books_with_missing_files:
                book = Livre.objects.get(id=book_id)
                self.stdout.write(f"- {book.titre} (fichier manquant: {book.couverture})")

        if input(f"Voulez-vous supprimer ces {total_problems} livres ? (oui/non): ").lower() == 'oui':
            # Supprimer d'abord ceux avec champ vide/null
            deleted_db, _ = qs.delete()
            
            # Puis ceux avec fichiers manquants
            deleted_files = 0
            if books_with_missing_files:
                _, dict_deleted = Livre.objects.filter(id__in=books_with_missing_files).delete()
                deleted_files = dict_deleted['appbiblio.Livre']
            
            self.stdout.write(self.style.SUCCESS(
                f"✅ Supprimés : {deleted_db} (champ vide) + {deleted_files} (fichier manquant) = {deleted_db + deleted_files} livres"
            ))