from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0002_appointment"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="appointment",
            name="ends_at",
        ),
    ]
