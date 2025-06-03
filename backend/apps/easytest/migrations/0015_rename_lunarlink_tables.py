from django.db import migrations

# No explicit table renames are needed here because all models in the former
# 'lunarlink' (now 'easytest') app had explicit `db_table` names set in their Meta.
# If there were models without `db_table` or ManyToMany tables automatically
# created by Django, they would have been prefixed with `lunarlink_` and
# would need `ALTER TABLE lunarlink_modelname RENAME TO easytest_modelname;`

# However, we still need to update Django's internal tracking tables.

class Migration(migrations.Migration):

    dependencies = [
        ('easytest', '0014_delete_hostip'), # Adjusted to actual previous migration
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE django_content_type SET app_label='easytest' WHERE app_label='lunarlink';",
            reverse_sql="UPDATE django_content_type SET app_label='lunarlink' WHERE app_label='easytest';",
        ),
        migrations.RunSQL(
            sql="UPDATE django_migrations SET app='easytest' WHERE app='lunarlink';",
            reverse_sql="UPDATE django_migrations SET app='lunarlink' WHERE app='easytest';",
        ),
    ]
