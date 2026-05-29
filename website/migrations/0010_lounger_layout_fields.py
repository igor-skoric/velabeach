# Generated manually for lounger layout fields

from django.db import migrations, models
from django.db.models import Q


def assign_sort_orders(apps, schema_editor):
    Lounger = apps.get_model('website', 'Lounger')
    counters = {}
    for lounger in Lounger.objects.order_by('stage_id', 'grid_section', 'id'):
        key = (lounger.stage_id, lounger.grid_section)
        lounger.sort_order = counters.get(key, 0)
        counters[key] = lounger.sort_order + 1
        lounger.save(update_fields=['sort_order'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0009_reservation_end_date'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='lounger',
            options={'ordering': ['grid_section', 'sort_order']},
        ),
        migrations.AddField(
            model_name='lounger',
            name='default_price',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='lounger',
            name='grid_section',
            field=models.CharField(
                choices=[
                    ('chair', 'Ležaljke (glavna mreža)'),
                    ('chair2', 'Ležaljke (druga mreža)'),
                    ('bed', 'Baldahini'),
                ],
                default='chair',
                max_length=10,
            ),
        ),
        migrations.AddField(
            model_name='lounger',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Neaktivne se ne prikazuju na mapi.'),
        ),
        migrations.AddField(
            model_name='lounger',
            name='sort_order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='position',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='stage',
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                related_name='loungers',
                to='website.stage',
            ),
        ),
        migrations.RunPython(assign_sort_orders, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='lounger',
            name='unique_lounger_position',
        ),
        migrations.AddConstraint(
            model_name='lounger',
            constraint=models.UniqueConstraint(
                condition=Q(is_obstacle=False) & ~Q(position=''),
                fields=('stage', 'lounger_type', 'position'),
                name='unique_lounger_position',
            ),
        ),
        migrations.AddConstraint(
            model_name='lounger',
            constraint=models.UniqueConstraint(
                fields=('stage', 'grid_section', 'sort_order'),
                name='unique_lounger_slot',
            ),
        ),
    ]
