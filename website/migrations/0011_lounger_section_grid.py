from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


def create_sections_and_row_col(apps, schema_editor):
    Stage = apps.get_model('website', 'Stage')
    LoungerSection = apps.get_model('website', 'LoungerSection')
    Lounger = apps.get_model('website', 'Lounger')
    LoungerType = apps.get_model('website', 'LoungerType')

    type_l, _ = LoungerType.objects.get_or_create(name='L')
    type_b, _ = LoungerType.objects.get_or_create(name='B')

    for stage_name, sections_cfg in [
        ('A', [
            ('chair', 'Ležaljke', type_l, 8, 0),
            ('bed', 'Baldahini', type_b, 9, 1),
        ]),
    ]:
        stage = Stage.objects.filter(name=stage_name).first()
        if not stage:
            continue

        section_by_code = {}
        for code, title, ltype, cols, order in sections_cfg:
            sec, _ = LoungerSection.objects.get_or_create(
                stage=stage,
                code=code,
                defaults={
                    'title': title,
                    'lounger_type': ltype,
                    'cols': cols,
                    'display_order': order,
                },
            )
            section_by_code[code] = sec

        for code, sec in section_by_code.items():
            cols = sec.cols
            loungers = Lounger.objects.filter(stage=stage, grid_section=code).order_by('sort_order')
            for index, lounger in enumerate(loungers):
                row = index // cols + 1
                col = index % cols + 1
                lounger.section_id = sec.id
                lounger.grid_row = row
                lounger.grid_col = col
                lounger.save(update_fields=['section_id', 'grid_row', 'grid_col'])


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0010_lounger_layout_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='LoungerSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(
                    choices=[
                        ('chair', 'Ležaljke (glavna mreža)'),
                        ('chair2', 'Ležaljke (druga mreža)'),
                        ('bed', 'Baldahini'),
                    ],
                    max_length=10,
                )),
                ('title', models.CharField(blank=True, help_text='npr. Ležaljke, Baldahini', max_length=100)),
                ('cols', models.PositiveIntegerField(
                    default=8,
                    help_text='Broj kolona u gridu na ekranu (povećaj ako dodaješ kolonu na kraju reda).',
                )),
                ('display_order', models.PositiveIntegerField(
                    default=0,
                    help_text='Redosled sekcije na stranici (0 = prva).',
                )),
                ('lounger_type', models.ForeignKey(
                    help_text='L = ležaljke, B = baldahini',
                    on_delete=django.db.models.deletion.PROTECT,
                    to='website.loungertype',
                )),
                ('stage', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='sections',
                    to='website.stage',
                )),
            ],
            options={
                'verbose_name': 'Sekcija mreže',
                'verbose_name_plural': 'Sekcije mreže',
                'ordering': ['display_order', 'code'],
            },
        ),
        migrations.AddConstraint(
            model_name='loungersection',
            constraint=models.UniqueConstraint(fields=('stage', 'code'), name='unique_stage_section'),
        ),
        migrations.AddField(
            model_name='lounger',
            name='grid_col',
            field=models.PositiveIntegerField(default=1, help_text='Kolona u mreži (1 = prva kolona).'),
        ),
        migrations.AddField(
            model_name='lounger',
            name='grid_row',
            field=models.PositiveIntegerField(default=1, help_text='Red u mreži (1 = prvi red).'),
        ),
        migrations.AddField(
            model_name='lounger',
            name='section',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='loungers',
                to='website.loungersection',
            ),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Neaktivne se ne prikazuju na mapi.'),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='is_obstacle',
            field=models.BooleanField(
                default=False,
                help_text='Prepreka = prazan prostor (X) na mapi, nije rezervabilno.',
            ),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='position',
            field=models.CharField(
                blank=True,
                help_text='Oznaka na mapi: I3 (ležaljka) ili 25 (baldahin). Za prepreku može ostati prazno.',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='lounger',
            name='sort_order',
            field=models.PositiveIntegerField(
                default=0,
                help_text='Zastarelo — koristi red i kolonu. Ostavljeno radi kompatibilnosti.',
            ),
        ),
        migrations.AlterModelOptions(
            name='lounger',
            options={'ordering': ['grid_row', 'grid_col', 'sort_order']},
        ),
        migrations.RunPython(create_sections_and_row_col, migrations.RunPython.noop),
        migrations.RemoveConstraint(
            model_name='lounger',
            name='unique_lounger_slot',
        ),
        migrations.AddConstraint(
            model_name='lounger',
            constraint=models.UniqueConstraint(
                condition=Q(section__isnull=False),
                fields=('section', 'grid_row', 'grid_col'),
                name='unique_section_cell',
            ),
        ),
    ]
