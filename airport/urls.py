from django.urls import path, include
from rest_framework import routers

from airport.views import (
    AirportViewSet,
    CrewViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    OrderViewSet,
    FlightViewSet,
    TicketViewSet,
)

router = routers.DefaultRouter()
router.register("/crew", CrewViewSet, basename="crew")
router.register("/airport", AirportViewSet, basename="airport")
router.register("/route", RouteViewSet, basename="route")
router.register(
    "/airplane-type", AirplaneTypeViewSet, basename="airplane-type"
)
router.register("/airplane", AirplaneViewSet, basename="airplane")
router.register("/order", OrderViewSet, basename="order")
router.register("/flight", FlightViewSet, basename="flight")
router.register("/ticket", TicketViewSet, basename="ticket")

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
