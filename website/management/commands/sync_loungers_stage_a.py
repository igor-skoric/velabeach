from django.core.management.base import BaseCommand

from website.layout_service import sync_stage_a_layout
from website.stage_seasons import STAGE_A_SEASON


class Command(BaseCommand):
    help = 'Sinhronizuje reon A iz STAGE_A_SEASON (website/stage_seasons.py).'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true')

    def handle(self, *args, **options):
        if options['dry_run']:
            from website.layout_service import generate_section_slots
            for code, cfg in STAGE_A_SEASON.items():
                n = len(generate_section_slots(code, cfg))
                self.stdout.write(f'  {code}: {n} slotova')
            return
        result = sync_stage_a_layout(verbose=True)
        self.stdout.write(self.style.SUCCESS(f'Gotovo: {result}'))
