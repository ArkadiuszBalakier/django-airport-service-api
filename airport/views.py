from rest_framework import viewsets

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
    queryset = Order.objects.all()
    serializer_class = OrderSerializer


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


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
        ).select_related("flight__airplane", "flight__route")
