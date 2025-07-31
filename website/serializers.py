# serializers.py
from rest_framework import serializers
from .models import Reservation, ReservationLog, ReservationDetail, DailyRevenue
from django.db import models

class ReservationDetailSerializer(serializers.ModelSerializer):
    status_display = serializers.SerializerMethodField(read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ReservationDetail
        fields = ['id',  'user', 'price', 'status', 'status_display', 'reserved_at', 'user_display']

    def get_status_display(self, obj):
        return obj.get_status_display()

    def get_user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"


class ReservationSerializer(serializers.ModelSerializer):
    lounger_position = serializers.CharField(source='lounger.position', read_only=True)
    lounger_type = serializers.CharField(source='lounger.lounger_type.name', read_only=True)
    stage = serializers.CharField(source='lounger.stage.name', read_only=True)
    user = serializers.CharField(source='user.username', read_only=True)
    status_display = serializers.SerializerMethodField(read_only=True)
    user_display = serializers.SerializerMethodField(read_only=True)

    details = ReservationDetailSerializer(many=True)
    # total_price = serializers.IntegerField(read_only=True)
    # total_reservations = serializers.IntegerField(read_only=True)

    class Meta:
        model = Reservation
        fields = [
            'id', 'user', 'lounger', 'lounger_position', 'lounger_type', 'stage',
            'date', 'end_date', 'status', 'status_display', 'details', 'user_display'
        ]
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["lounger"]),
        ]

    def get_user_display(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"

    # Validacija jer su datum i lezaljka jedinstveni, pa create ne moze da prodje i da kreira samo detalje ako vec postoji rezervacija kreirana

    def create(self, validated_data):
        details_data = validated_data.pop('details', [])
        user = self.context['request'].user

        reservation = Reservation.objects.create(user=user, **validated_data)

        for detail_data in details_data:
            ReservationDetail.objects.create(reservation=reservation, **detail_data)

        return reservation

    def update(self, instance, validated_data):
        print('usao u update sta')
        new_status = validated_data.get('status', instance.status)

        if new_status == instance.status:
            raise serializers.ValidationError({
                'status': 'Novi status mora biti različit od trenutnog statusa.'
            })

        return super().update(instance, validated_data)

    def get_status_display(self, obj):
        return obj.get_status_display()




class ReservationLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReservationLog
        fields = '__all__'
        read_only_fields = ['timestamp']


class DailyRevenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyRevenue
        fields = ['date', 'A', 'B', 'C', 'D', 'total_income']