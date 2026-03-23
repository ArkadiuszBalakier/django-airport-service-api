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
router.register("crew", CrewViewSet)
router.register("airport", AirportViewSet)
router.register("route", RouteViewSet)
router.register("airplane_type", AirplaneTypeViewSet)
router.register("airplane_route", AirplaneViewSet)
router.register("order", OrderViewSet)
router.register("flight", FlightViewSet)
router.register("ticket", TicketViewSet)

urlpatterns = [path("", include(router.urls))]

app_name = "airport"
