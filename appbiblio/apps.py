from django.apps import AppConfig


class AppbiblioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'appbiblio'

def ready(self):
    import bibliotheque.signals # type: ignore