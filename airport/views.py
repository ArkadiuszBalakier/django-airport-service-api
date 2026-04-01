from rest_framework import viewsets
from rest_framework import permissions
from django.db.models import Prefetch, F, Count

from airport.permissions import IsAdminOrReadOnly
from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
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
    AirplaneSerializer,
    OrderSerializer,
    FlightSerializer,
    TicketDetailsSerializer,
    TicketListSerializer,
    TicketSerializer,
)


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = (IsAdminOrReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = (IsAdminOrReadOnly,)


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all().select_related("airplane_type")
    serializer_class = AirplaneSerializer
    permission_classes = (IsAdminOrReadOnly,)


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tickets_qs = Ticket.objects.select_related(
            "flight__route__source",
            "flight__route__destination",
            "flight__airplane__airplane_type",
        )

        queryset = Order.objects.prefetch_related(
            Prefetch("tickets", queryset=tickets_qs)
        )

        if not self.request.user.is_staff:
            return queryset.filter(user=self.request.user)

        return queryset


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
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
            .annotate(
                tickets_available=(
                    F("airplane__rows") * F("airplane__seats_in_row")
                    - Count("tickets")
                )
            )
        return queryset


class TicketViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = TicketListSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailsSerializer
        return TicketSerializer

    def get_queryset(self):
        queryset = Ticket.objects.select_related(
            "flight__airplane",
            "flight__route__source",
            "flight__route__destination",
        )
        if not self.request.user.is_staff:
            return queryset.filter(order__user=self.request.user)
        return queryset
