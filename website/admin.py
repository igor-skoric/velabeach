# admin.py
from django.contrib import admin
from .models import Stage, LoungerType, Lounger, Reservation, ReservationDetail, ReservationLog, DailyRevenue


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


@admin.register(LoungerType)
class LoungerTypeAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Lounger)
class LoungerAdmin(admin.ModelAdmin):
    list_display = ['stage', 'lounger_type', 'position', 'is_obstacle']
    list_filter = ['stage', 'lounger_type', 'is_obstacle']
    search_fields = ['position']



admin.site.register(ReservationDetail)
admin.site.register(DailyRevenue)
admin.site.register(Reservation)


@admin.register(ReservationLog)
class ReservationLogAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'field_name', 'old_value', 'new_value', 'timestamp', 'user')
    list_filter = ('field_name', 'timestamp', 'user')
    search_fields = ('field_name', 'old_value', 'new_value')


