from django.apps import AppConfig


class EasyTestConfig(AppConfig):
    default_auto_field = 'django.db.models.AutoField'  # Added as it's good practice
    name = 'apps.easytest'
    verbose_name = 'EasyTest'
