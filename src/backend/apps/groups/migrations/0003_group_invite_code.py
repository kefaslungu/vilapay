import apps.groups.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("groups", "0002_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="group",
            name="invite_code",
            field=models.CharField(
                default=apps.groups.models._generate_invite_code,
                help_text="9-character invite code (e.g. VLA-8K2QF9) for joining via the app",
                max_length=9,
                unique=True,
            ),
        ),
    ]
