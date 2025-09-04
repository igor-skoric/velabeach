from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from .models import Reservation, ReservationLog, DailyRevenue, ReservationDetail
import json


@receiver(post_save, sender=Reservation)
def log_reservation_create(sender, instance, created, **kwargs):
    if created:
        ReservationLog.objects.create(
            reservation=instance,
            user=instance.user,
            action='created',
            new_value=str({
                'status': instance.status,
                'date': str(instance.date),
                # 'end_date': str(instance.end_date),
                'lounger': str(instance.lounger),
                'user': str(instance.user),
            }),
        )

    revenue, _ = DailyRevenue.objects.get_or_create(date=str(instance.date))
    revenue.update_total()


@receiver(pre_save, sender=Reservation)
def log_reservation_update(sender, instance, **kwargs):
    try:
        old = sender.objects.get(pk=instance.pk)
    except sender.DoesNotExist:
        return  # Novi objekat, nije update

    user = instance.user  # korisnik koji menja (ovo možeš dodatno prilagoditi ako nije isti kao `user` rezervacije)

    changes = {}
    for field in instance._meta.fields:
        field_name = field.name
        if field_name in ['created_at', 'updated_at']:
            continue

        old_value = getattr(old, field_name)
        new_value = getattr(instance, field_name)
        if old_value != new_value:
            changes[field_name] = {
                'old': str(old_value),
                'new': str(new_value),
            }

    if changes:
        ReservationLog.objects.create(
            reservation=instance,
            user=user,
            action='updated',
            old_value='',  # opcionalno prazno jer se koristi `changes`
            new_value=json.dumps(changes),  # sve promene u jednom JSON stringu
        )


@receiver(post_save, sender=ReservationDetail)
def update_revenue_on_detail_save(sender, instance, created, **kwargs):
    reservation = instance.reservation
    revenue, _ = DailyRevenue.objects.get_or_create(date=reservation.date)
    revenue.update_total()


@receiver(post_delete, sender=ReservationDetail)
def delete_reservation_if_no_details(sender, instance, **kwargs):
    try:
        reservation = Reservation.objects.get(pk=instance.reservation_id)
    except Reservation.DoesNotExist:
        return  # Rezervacija ne postoji, ništa dalje ne radi

    remaining_details = reservation.details.all()

    if not remaining_details.exists():
        reservation.delete()
    else:
        last_detail = remaining_details.latest('reserved_at')
        reservation.status = last_detail.status
        reservation.save(update_fields=['status'])

    revenue, _ = DailyRevenue.objects.get_or_create(date=reservation.date)
    revenue.update_total()
