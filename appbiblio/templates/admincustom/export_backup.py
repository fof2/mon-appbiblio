# export_backup.py
from django.core.management import call_command
import django
import os

# Remplace 'monbiblio.settings' par le bon chemin si nécessaire
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monbiblio.settings")
django.setup()

with open("backup.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", stdout=f, indent=2)
