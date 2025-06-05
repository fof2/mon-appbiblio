import os
import django

# Initialiser Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monbiblio.settings')
django.setup()

from django.contrib.auth.models import User

# Changer le mot de passe de l'utilisateur "fofana2"
user = User.objects.get(username='fofana2')
user.set_password('fof2')
user.save()

print("Le mot de passe a été changé avec succès.")
# http://monbiblio.adama.ci:8000/