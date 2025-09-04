# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.conf import settings
from collections import defaultdict
from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

STATUS_CHOICES = [
    ('available', 'Slobodno'),
    ('unavailable', 'Zauzeto'),
    ('reserved', 'Rezervisano'),
    ('signature', 'Potpis'),
]


class Stage(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class LoungerType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Lounger(models.Model):
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    lounger_type = models.ForeignKey(LoungerType, on_delete=models.CASCADE)
    position = models.CharField(max_length=10)

    is_obstacle = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['stage', 'lounger_type', 'position'], name='unique_lounger_position')
        ]

    def __str__(self):
        return f"{self.stage.name} - {self.lounger_type.name} #{self.position}"


class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lounger = models.ForeignKey(Lounger, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')
    total_price = models.PositiveIntegerField(default=0)
    total_reservations = models.PositiveIntegerField(default=0)
    date = models.DateField()
    # end_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - {self.lounger} - {self.date}"

    # def clean(self):
        # Custom validacija datuma
        # if self.end_date < self.date:
        #     raise ValidationError("Datum završetka ne može biti pre datuma početka.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'lounger'], name='unique_date_lounger')
        ]

    STATUS_CHOICES = [
        ('available', 'Slobodno'),
        ('unavailable', 'Zauzeto'),
        ('reserved', 'Rezervisano'),
        ('signature', 'Potpis'),
    ]

    @staticmethod
    def get_user_revenue(date, stage):
        busy_lounger = 0
        busy_bed = 0
        reserved = 0
        signature = 0
        reserved_lounger = 0
        reserved_bed = 0
        reservations = Reservation.objects.filter(date=date, lounger__stage=stage).prefetch_related('details')

        for r in reservations:
            for d in r.details.all():
                if d.status == 'unavailable':
                    if r.lounger.lounger_type.name == 'L':
                        busy_lounger += 1
                    else:
                        busy_bed += 1

                if d.status == 'reserved':
                    if r.lounger.lounger_type.name == 'L':
                        reserved_lounger += 1
                    else:
                        reserved_bed += 1

                if d.status == 'reserved':
                    reserved += 1

                if d.status == 'signature':
                    signature += 1
        from .utils import count_loungers
        total_beds = count_loungers(stage_name=stage, lounger_type="B")
        total_loungers = count_loungers(stage_name=stage, lounger_type="L")

        return {
            'busy_lounger': busy_lounger,
            'reserved_lounger': reserved_lounger,
            'busy_bed': busy_bed,
            'reserved_bed': reserved_bed,
            'signature': signature,
            'reserved': reserved,
            'total_beds': total_beds,
            'total_loungers': total_loungers
        }

    @property
    def total_price(self):
        return sum(detail.price for detail in self.details.all())

    @staticmethod
    def check_unavailability(lounger, date):
        busy_statuses = ['unavailable', 'reserved', 'signature']

        return Reservation.objects.filter(
            lounger_id=lounger.id,
            lounger__stage_id=lounger.stage.id,
            status__in=busy_statuses,
            date=date
        ).exists()


class ReservationDetail(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='details')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='available')
    price = models.PositiveIntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    reserved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.reservation}"


class ReservationLog(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    field_name = models.CharField(max_length=100, null=True, blank=True)
    old_value = models.TextField(null=True, blank=True)
    new_value = models.TextField(null=True, blank=True)
    action = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} at {self.timestamp}"


class DailyRevenue(models.Model):
    date = models.DateField(unique=True)
    A = models.IntegerField(default=0)
    B = models.IntegerField(default=0)
    C = models.IntegerField(default=0)
    D = models.IntegerField(default=0)

    busy_lounger = models.IntegerField(default=0)
    reserved_lounger = models.IntegerField(default=0)
    total_loungers = models.IntegerField(default=0)

    busy_bed = models.IntegerField(default=0)
    reserved_bed = models.IntegerField(default=0)
    total_beds = models.IntegerField(default=0)

    reserved = models.IntegerField(default=0)
    signature = models.IntegerField(default=0)

    total_income = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.date} - {self.total_income} EUR"

    @property
    def occupancy_rate(self):
        result = 0
        all = Lounger.objects.count()
        occupancy = self.busy_lounger + self.busy_bed + self.reserved + self.signature
        if occupancy != 0:
            result = f'{round((occupancy / all) * 100, 2):.1f}'

        return result


    def update_total(self):
        reservations = Reservation.objects.filter(date=self.date) \
            .select_related('lounger__stage') \
            .prefetch_related('details')

        busy_lounger = 0
        busy_bed = 0
        reserved = 0
        reserved_bed = 0
        reserved_lounger = 0
        signature = 0
        grouped_totals = defaultdict(float)

        for r in reservations:
            for detail in r.details.all():
                if detail.status == 'unavailable':
                    if r.lounger.lounger_type.name == 'L':
                        busy_lounger += 1
                    else:
                        busy_bed += 1

                if detail.status == 'reserved':
                    if r.lounger.lounger_type.name == 'L':
                        reserved_lounger += 1
                    else:
                        reserved_bed += 1

                    reserved += 1

                if detail.status == 'signature':
                    signature += 1

            stage_name = r.lounger.stage.name.upper()  # očekujemo 'A', 'B', itd.
            grouped_totals[stage_name] += r.total_price

        # Postavi vrednosti u polja
        self.A = grouped_totals.get('A', 0)
        self.B = grouped_totals.get('B', 0)
        self.C = grouped_totals.get('C', 0)
        self.D = grouped_totals.get('D', 0)

        self.busy_lounger = busy_lounger
        self.busy_bed = busy_bed
        self.reserved = reserved
        self.signature = signature
        self.reserved_lounger = reserved_lounger
        self.reserved_bed = reserved_bed

        self.total_income = sum(grouped_totals.values())

        self.save(
            update_fields=['A', 'B', 'C', 'D', 'reserved', 'busy_lounger', 'busy_bed', 'signature', 'total_income', 'reserved_lounger', 'reserved_bed'])
