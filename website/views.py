from django.shortcuts import render, get_object_or_404, redirect
from .serializers import ReservationSerializer, ReservationLogSerializer, ReservationDetailSerializer, \
    DailyRevenueSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Stage, Lounger, Reservation, ReservationDetail, ReservationLog, DailyRevenue
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
from django.db.models import Count
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated

import json
import logging

logger = logging.getLogger("django")
User = get_user_model()

@login_required
def home(request):
    context = {}
    return render(request, 'website/pages/index.html', context)


@login_required
def analytics(request):
    # Npr. broj rezervacija po danu za poslednjih 7 dana
    data = (Reservation.objects
            .filter(date__gte='2025-07-01')
            .values('date')
            .annotate(count=Count('id'))
            .order_by('date'))

    dates = [str(item['date']) for item in data]
    counts = [item['count'] for item in data]

    context = {
        'dates_json': json.dumps(dates),
        'counts_json': json.dumps(counts),
    }
    return render(request, 'website/pages/analytics.html', context)


class ReservationListAPIView(APIView):
    def get(self, request):
        stage = request.query_params.get('stage')
        date = request.query_params.get('date')  # format YYYY-MM-DD

        if not stage or not date:
            return Response(
                {"error": "stage and date query parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        reservations = (
            Reservation.objects
            .filter(lounger__stage__name=stage, date=date)
            .select_related('lounger', 'user')  # dodaj sve FK koje koristiš u serializeru
            .prefetch_related('details')        # dodaj i ostale M2M ako ih imaš
        )

        serializer = ReservationSerializer(reservations, many=True)
        return Response(serializer.data)


class ReservationCreateAPIView(APIView):
    def post(self, request):

        data = request.data
        user = request.user
        lounger_position = data.get('lounger_position')
        stage = data.get('stage')

        date = data.get('date')
        end_date = data.get('end_date')
        date = datetime.strptime(date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

        date_list = [date + timedelta(days=i) for i in range((end_date - date).days + 1)]

        reservation_status = data.get('status')
        details_data = data.get('details', [])

        stage = Stage.objects.filter(name=stage).first()
        lounger = Lounger.objects.filter(position=lounger_position, stage=stage).first()

        if not date or not end_date:
            return Response({'error': 'Both date and end_date are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if not lounger:
            return Response({'error': 'Lezaljka ili baldahin ne postoji'}, status=status.HTTP_400_BAD_REQUEST)

        unavailable = Reservation.check_unavailability(lounger, date, end_date)
        if unavailable and reservation_status != 'available':
            return Response({'error': 'Ležaljka je zauzeta.'}, status=status.HTTP_409_CONFLICT)

        for index, date in enumerate(date_list):
            reservation = Reservation.objects.filter(lounger_id=lounger.id, date=date).first()

            if reservation:
                if reservation.status == reservation_status:
                    return Response({'error': 'Ne može se promeniti status u već postojeći.'},
                                    status=status.HTTP_409_CONFLICT)
                reservation.date = date or reservation.date
                reservation.end_date = end_date or reservation.end_date
                reservation.status = reservation_status
                reservation.save()

                # Ako postoji rezervacija, dodaj samo nove detalje
                for detail_data in details_data:
                    ReservationDetail.objects.create(
                        reservation=reservation,
                        user=user,
                        status=reservation_status,
                        **detail_data
                    )

                serializer = ReservationSerializer(reservation, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                if reservation_status == 'available':
                    return Response({'error': 'Status je vеć dostupan.'}, status=status.HTTP_409_CONFLICT)

                # DODAVANJE REZERVACIJA
                reservation = Reservation.objects.create(
                    user=user,
                    lounger_id=lounger.id,
                    status=reservation_status,
                    date=date,
                    end_date=end_date
                )

                # DODAVANJE DETALJA
                for detail_data in details_data:
                    ReservationDetail.objects.create(
                        reservation=reservation,
                        user=user,
                        status=reservation_status,
                        **detail_data
                    )

                serializer = ReservationSerializer(reservation, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReservationUpdateAPIView(APIView):
    def put(self, request, pk):
        try:
            reservation = Reservation.objects.get(pk=pk)
        except Reservation.DoesNotExist:
            return Response({"error": "Reservation not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ReservationSerializer(reservation, data=request.data,
                                           partial=True)  # partial=True dozvoljava delimične izmene
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReservationLogViewSet(viewsets.ModelViewSet):
    queryset = ReservationLog.objects.all().order_by('-timestamp')
    serializer_class = ReservationLogSerializer


class ReservationDetailViewSet(viewsets.ModelViewSet):
    queryset = ReservationDetail.objects.all()
    serializer_class = ReservationDetailSerializer

    def get_queryset(self):
        queryset = ReservationDetail.objects.all()
        reservation_id = self.request.query_params.get('reservation', None)
        if reservation_id is not None:
            queryset = queryset.filter(reservation_id=reservation_id)
        return queryset


class DailyRevenueByDateAPIView(APIView):
    def get(self, request):
        date = request.query_params.get('date')
        end_date = request.query_params.get('end_date')

        if not date:
            return Response({"error": "date parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        revenue = DailyRevenue.objects.filter(date__range=[date, end_date]).order_by('date')

        if revenue:
            serializer = DailyRevenueSerializer(revenue, many=True)
        else:
            # Prazan odgovor ako ne postoji podatak za taj datum
            serializer = DailyRevenueSerializer(DailyRevenue(
                date=date,
                A=0, B=0, C=0, D=0, total_income=0
            ))

        return Response(serializer.data)


class ReservationDetailDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            detail = ReservationDetail.objects.get(pk=pk)
        except ReservationDetail.DoesNotExist:
            return Response({'error': 'Reservation detail not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Opcionalno: Proveri da li korisnik ima prava da briše (ako ima smisla)
        # if detail.user != request.user:
        #     return Response({'error': 'Not authorized to delete this detail.'}, status=status.HTTP_403_FORBIDDEN)

        detail.delete()
        return Response({'message': 'Reservation detail deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)
