import apps.groups.models
from django.db import migrations, models


def populate_invite_codes(apps, schema_editor):
    """Assign a unique invite code to every existing group."""
    Group = apps.get_model("groups", "Group")
    from apps.groups.models import _generate_invite_code

    used = set()
    for group in Group.objects.filter(invite_code__isnull=True):
        code = _generate_invite_code()
        while code in used:
            code = _generate_invite_code()
        used.add(code)
        group.invite_code = code
        group.save(update_fields=["invite_code"])


class Migration(migrations.Migration):
    dependencies = [
        ("groups", "0002_initial"),
    ]

    operations = [
        # 1. Add nullable first — existing rows get NULL, not a repeated default.
        migrations.AddField(
            model_name="group",
            name="invite_code",
            field=models.CharField(
                max_length=9,
                null=True,
                blank=True,
                help_text="9-character invite code (e.g. VLA-8K2QF9) for joining via the app",
            ),
        ),
        # 2. Populate a unique code for every existing row.
        migrations.RunPython(populate_invite_codes, migrations.RunPython.noop),
        # 3. Enforce NOT NULL + UNIQUE now that all rows have distinct values.
        migrations.AlterField(
            model_name="group",
            name="invite_code",
            field=models.CharField(
                max_length=9,
                unique=True,
                default=apps.groups.models._generate_invite_code,
                help_text="9-character invite code (e.g. VLA-8K2QF9) for joining via the app",
            ),
        ),
    ]
