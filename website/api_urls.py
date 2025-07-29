from django.urls import path
from .views import ReservationListAPIView, ReservationCreateAPIView, ReservationUpdateAPIView, ReservationLogViewSet, ReservationDetailViewSet, DailyRevenueByDateAPIView, ReservationDetailDeleteAPIView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'reservation-logs', ReservationLogViewSet)
router.register(r'reservation-details', ReservationDetailViewSet)

urlpatterns = [
    path('reservations/', ReservationListAPIView.as_view(), name='reservations-list'),
    path('reservations/create/', ReservationCreateAPIView.as_view(), name='reservation-create'),
    path('reservations/<int:pk>/update/', ReservationUpdateAPIView.as_view(), name='reservation-update'),
    path('daily-revenue-by-date/', DailyRevenueByDateAPIView.as_view(), name='daily-revenue-by-date'),
    path('reservation-details/<int:pk>/delete/', ReservationDetailDeleteAPIView.as_view(), name='reservation-detail-delete'),
]


urlpatterns += router.urls