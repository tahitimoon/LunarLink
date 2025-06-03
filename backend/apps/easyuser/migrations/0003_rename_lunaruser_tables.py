from django.db import migrations

TABLE_RENAMES = [
    ("lunaruser_myuser", "easyuser_myuser"),
    ("lunaruser_myuser_groups", "easyuser_myuser_groups"),
    ("lunaruser_myuser_user_permissions", "easyuser_myuser_user_permissions"),
]

class Migration(migrations.Migration):

    dependencies = [
        ('easyuser', '0002_myuser_name'), # Adjusted to actual previous migration
    ]

    operations = [
        migrations.RunSQL(
            sql=[f"ALTER TABLE {old_name} RENAME TO {new_name};" for old_name, new_name in TABLE_RENAMES],
            reverse_sql=[f"ALTER TABLE {new_name} RENAME TO {old_name};" for old_name, new_name in TABLE_RENAMES],
        ),
        migrations.RunSQL(
            sql="UPDATE django_content_type SET app_label='easyuser' WHERE app_label='lunaruser';",
            reverse_sql="UPDATE django_content_type SET app_label='lunaruser' WHERE app_label='easyuser';",
        ),
        migrations.RunSQL(
            sql="UPDATE django_migrations SET app='easyuser' WHERE app='lunaruser';",
            reverse_sql="UPDATE django_migrations SET app='lunaruser' WHERE app='easyuser';",
        ),
    ]
