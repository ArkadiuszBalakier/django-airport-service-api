from rest_framework import viewsets
from django.db.models import Prefetch

from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Order,
    Flight,
    Ticket,
)
from airport.serializers import (
    CrewSerializer,
    AirportSerializer,
    FlightListSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    OrderSerializer,
    FlightSerializer,
    TicketDetailsSerializer,
    TicketListSerializer,
    TicketSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all().select_related("airplane_type")
    serializer_class = AirplaneTypeSerializer


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        tickets_qs = Ticket.objects.select_related(
            "flight__route__source",
            "flight__route__destination",
            "flight__airplane__airplane_type",
        )

        return (
            Order.objects.filter(user=self.request.user)
            .select_related("user")
            .prefetch_related(Prefetch("tickets", queryset=tickets_qs))
        )


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer

    def get_serializer_class(self):
        if self.action in ("list", "retrive"):
            return FlightListSerializer
        return FlightSerializer

    def get_queryset(self):
        return (
            Flight.objects.all()
            .select_related(
                "route__source",
                "route__destination",
                "airplane__airplane_type",
            )
            .prefetch_related("crew")
        )


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketListSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailsSerializer
        return TicketSerializer

    def get_queryset(self):
        return Ticket.objects.filter(
            order__user=self.request.user
        ).select_related(
            "flight__airplane",
            "flight__route__source",
            "flight__route__destination",
        )
