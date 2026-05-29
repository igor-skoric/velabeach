# admin.py
from django.contrib import admin
from django.utils.html import format_html

from .models import (
    Stage,
    LoungerType,
    LoungerSection,
    Lounger,
    Reservation,
    ReservationDetail,
    ReservationLog,
    DailyRevenue,
)


def _sync_action(stage_name):
    def action(modeladmin, request, queryset):
        from .layout_service import sync_stage_layout

        result = sync_stage_layout(stage_name, verbose=False)
        modeladmin.message_user(
            request,
            f'Reon {stage_name}: {result["created"]} kreirano, {result["updated"]} ažurirano.',
        )

    action.__name__ = f'sync_stage_{stage_name.lower()}_action'
    action.short_description = f'Sinhronizuj layout reona {stage_name} (šablon)'
    return action


sync_stage_a_action = _sync_action('A')
sync_stage_b_action = _sync_action('B')
sync_stage_c_action = _sync_action('C')
sync_stage_d_action = _sync_action('D')


@admin.action(description='Sinhronizuj layout SVIH reona A–D (šablon)')
def sync_all_stages_action(modeladmin, request, queryset):
    from .layout_service import sync_all_stages_layout

    totals = sync_all_stages_layout(verbose=False)
    modeladmin.message_user(
        request,
        f'Ukupno: {totals["created"]} kreirano, {totals["updated"]} ažurirano.',
    )


class LoungerInline(admin.TabularInline):
    model = Lounger
    extra = 1
    fields = (
        'grid_row',
        'grid_col',
        'position',
        'default_price',
        'is_obstacle',
        'is_active',
    )
    ordering = ('grid_row', 'grid_col')
    show_change_link = True


@admin.register(LoungerSection)
class LoungerSectionAdmin(admin.ModelAdmin):
    list_display = ('stage', 'code', 'title', 'lounger_type', 'cols', 'display_order', 'slot_count')
    list_filter = ('stage', 'code', 'lounger_type')
    list_editable = ('cols', 'display_order', 'title')
    search_fields = ('stage__name', 'title')
    ordering = ('stage__name', 'display_order')
    inlines = [LoungerInline]
    fieldsets = (
        (None, {
            'fields': ('stage', 'code', 'title', 'lounger_type', 'cols', 'display_order'),
            'description': (
                '<strong>cols</strong> = broj kolona na ekranu. '
                'Ako dodaš 9. ležaljku u svaki red, postavi cols na 9.'
            ),
        }),
    )

    @admin.display(description='Slotova')
    def slot_count(self, obj):
        return obj.loungers.filter(is_active=True).count()


class LoungerSectionInline(admin.StackedInline):
    model = LoungerSection
    extra = 0
    fields = ('code', 'title', 'lounger_type', 'cols', 'display_order')
    show_change_link = True


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['name', 'section_summary']
    search_fields = ['name']
    actions = [sync_stage_a_action, sync_stage_b_action, sync_stage_c_action, sync_stage_d_action, sync_all_stages_action]
    inlines = [LoungerSectionInline]

    @admin.display(description='Sekcije')
    def section_summary(self, obj):
        parts = [
            f'{s.get_code_display()} ({s.cols} kol.)'
            for s in obj.sections.all().order_by('display_order')
        ]
        return ', '.join(parts) if parts else '—'


@admin.register(LoungerType)
class LoungerTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Lounger)
class LoungerAdmin(admin.ModelAdmin):
    list_display = [
        'stage',
        'section',
        'grid_row',
        'grid_col',
        'position',
        'default_price',
        'is_obstacle',
        'is_active',
        'status_badge',
    ]
    list_filter = ['stage', 'section__code', 'lounger_type', 'is_obstacle', 'is_active']
    list_editable = ['grid_row', 'grid_col', 'default_price', 'is_obstacle', 'is_active']
    search_fields = ['position', 'stage__name']
    ordering = ['stage__name', 'section__display_order', 'grid_row', 'grid_col']
    list_per_page = 50
    autocomplete_fields = ['section']
    fieldsets = (
        (None, {
            'fields': ('section', 'stage', 'lounger_type'),
            'description': 'Izaberi sekciju (Ležaljke / Baldahini) — stage i tip se popune automatski.',
        }),
        ('Pozicija u mreži', {
            'fields': ('grid_row', 'grid_col', 'position', 'default_price', 'is_obstacle', 'is_active'),
            'description': (
                '<ul style="margin-left:1em;">'
                '<li><strong>Red / kolona</strong> — tačna pozicija na mapi (III9 = red 3, kolona 9). '
                'Praznine iznad/dole se ne popunjavaju automatski — ne treba prepreka za prazan prostor.</li>'
                '<li><strong>Pozicija</strong> — oznaka na mapi (I3, 25). Za ležaljke može ostati prazno — popuni se iz reda (rimski broj)</li>'
                '<li><strong>Prepreka</strong> — vidljivo X samo tamo gde želiš blok u mreži</li>'
                '<li><strong>Neaktivno</strong> — skriveno sa mape</li>'
                '</ul>'
            ),
        }),
    )

    @admin.display(description='Status')
    def status_badge(self, obj):
        if not obj.is_active:
            return format_html('<span style="color:#999;">neaktivno</span>')
        if obj.is_obstacle:
            return format_html('<span style="color:#666;">prepreka</span>')
        return format_html('<span style="color:green;">aktivno</span>')


admin.site.register(ReservationDetail)
admin.site.register(DailyRevenue)
admin.site.register(Reservation)


@admin.register(ReservationLog)
class ReservationLogAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'field_name', 'old_value', 'new_value', 'timestamp', 'user')
    list_filter = ('field_name', 'timestamp', 'user')
    search_fields = ('field_name', 'old_value', 'new_value')
