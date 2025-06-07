# export_backup.py
import os
import django
from django.core.management import call_command

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "monbiblio.settings")
django.setup()

with open("backup.json", "w", encoding="utf-8") as f:
    call_command("dumpdata", indent=2, stdout=f)
