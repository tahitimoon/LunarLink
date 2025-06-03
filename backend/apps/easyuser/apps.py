from django.apps import AppConfig


class EasyUserConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'  # Added as it's good practice
    name = 'apps.easyuser'
    verbose_name = 'EasyUser'
