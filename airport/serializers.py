from django.core.exceptions import ValidationError
from rest_framework import serializers
from django.db import transaction

from .models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Ticket,
    Order,
)


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name")


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ("id", "name", "closest_big_city")


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(
        queryset=Airport.objects.all(), slug_field="name"
    )
    destination = serializers.SlugRelatedField(
        queryset=Airport.objects.all(), slug_field="name"
    )

    def validate(self, attrs):
        source = attrs.get("source") or (
            self.instance.source if self.instance else None
        )
        destination = attrs.get("destination") or (
            self.instance.destination if self.instance else None
        )

        if source == destination:
            raise serializers.ValidationError(
                {"destination": "destination can't be same as source"}
            )
        return attrs

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ("id", "name")


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = AirplaneTypeSerializer()

    class Meta:
        model = Airplane
        fields = ("id", "name", "rows", "seats_in_row", "airplane_type")


class AirplaneNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ("name",)


class FlightNestedSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()
    airplane = AirplaneNestedSerializer(read_only=True)

    class Meta:
        model = Flight
        fields = ("route", "airplane", "departure_time", "arrival_time")


class FlightSerializer(serializers.ModelSerializer):
    departure_time = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S",
        input_formats=["%Y-%m-%dT%H:%M:%S", "iso-8601"],
        style={"input_type": "text"},
    )

    arrival_time = serializers.DateTimeField(
        format="%Y-%m-%dT%H:%M:%S",
        input_formats=["%Y-%m-%dT%H:%M:%S", "iso-8601"],
        style={"input_type": "text"},
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = (
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
            "tickets_available",
        )

    def validate(self, attrs):
        if not attrs:
            return attrs

        if self.instance:
            instance = self.instance
            for field, value in attrs.items():
                setattr(instance, field, value)
        else:
            instance = Flight(**attrs)

        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        departure = instance.departure_time
        arrival = instance.arrival_time
        airplane = instance.airplane
        crew_members = attrs.get("crew", [])

        overlapping_flights = Flight.objects.filter(
            departure_time__lt=arrival, arrival_time__gt=departure
        )

        if self.instance:
            overlapping_flights = overlapping_flights.exclude(
                pk=self.instance.pk
            )

        if overlapping_flights.filter(airplane=airplane).exists():
            raise serializers.ValidationError(
                {"airplane": f"{airplane} is assigned to another flight"}
            )

        if crew_members:
            busy_crew = overlapping_flights.filter(
                crew__in=crew_members
            ).distinct()
            if busy_crew.exists():
                raise serializers.ValidationError(
                    {"crew": "Crew member already assigned to another flight."}
                )


class FlightListSerializer(FlightSerializer):
    route = serializers.StringRelatedField()
    airplane = AirplaneSerializer()


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "flight")

    def validate(self, attrs):
        instance = Ticket(**attrs)
        try:
            instance.full_clean()
        except ValidationError as e:
            raise serializers.ValidationError(e.message_dict)

        flight = attrs.get("flight")
        capacity = flight.airplane.rows * flight.airplane.seats_in_row
        current_tickets_count = flight.tickets.count()
        if current_tickets_count >= capacity:
            raise serializers.ValidationError(
                {"flight": "All tickets sold out !!!"}
            )

        return attrs


class FlightOrderStubSerializer(serializers.ModelSerializer):
    route = serializers.StringRelatedField()

    class Meta:
        model = Flight
        fields = ("route", "departure_time")


class TicketOrderSerializer(TicketSerializer):
    flight = FlightOrderStubSerializer()

    class Meta:
        model = Ticket
        fields = ("row", "seat", "flight")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketOrderSerializer(many=True, read_only=True)
    tickets_to_create = TicketSerializer(
        many=True, write_only=True, source="tickets"
    )

    class Meta:
        model = Order
        fields = ("id", "created_at", "user", "tickets", "tickets_to_create")
        read_only_fields = ("id", "created_at", "user")

    def create(self, validated_data):
        user = self.context["request"].user
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(user=user, **validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order


class TicketListSerializer(TicketSerializer):
    flight = FlightNestedSerializer(read_only=True)

    class Meta(TicketSerializer.Meta):
        fields = ("id", "row", "seat", "flight", "order")


class TicketDetailsSerializer(TicketSerializer):
    flight = FlightSerializer(read_only=True)

    class Meta(TicketSerializer.Meta):
        fields = ("id", "row", "seat", "flight", "order")
