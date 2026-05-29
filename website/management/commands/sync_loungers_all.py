from django.core.management.base import BaseCommand

from website.layout_service import sync_all_stages_layout


class Command(BaseCommand):
    help = 'Sinhronizuje reone A, B, C i D iz stage_seasons.py.'

    def handle(self, *args, **options):
        totals = sync_all_stages_layout(verbose=True)
        self.stdout.write(
            self.style.SUCCESS(
                f'Ukupno: {totals["created"]} kreirano, {totals["updated"]} ažurirano.'
            )
        )
