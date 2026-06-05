# Generated for COMP3310 S1 2026 group project secure feature implementation.

import uuid
from django.db import migrations, models


def set_unique_share_ids(apps, schema_editor):
    Game = apps.get_model('hangMansApp', 'Game')
    for game in Game.objects.all():
        game.share_id = uuid.uuid4()
        game.save(update_fields=['share_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('hangMansApp', '0004_game_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='share_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='hints_used',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='game',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.RunPython(set_unique_share_ids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='game',
            name='share_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='game',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
