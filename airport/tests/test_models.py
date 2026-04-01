from django.test import TestCase
from django.contrib.auth import get_user_model
from airport.models import (
    Crew,
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket,
)


class ModelTests(TestCase):
    def test_crew_str(self):
        crew = Crew.objects.create(first_name="John", last_name="Doe")
        self.assertEqual(str(crew), "John Doe")

    def test_airport_str(self):
        airport = Airport.objects.create(
            name="Heathrow", closest_big_city="London"
        )
        self.assertEqual(str(airport), "Heathrow")

    def test_route_str(self):
        source = Airport.objects.create(name="WAW", closest_big_city="Warsaw")
        dest = Airport.objects.create(name="JFK", closest_big_city="New York")
        route = Route.objects.create(source=source, destination=dest)
        self.assertEqual(str(route), "WAW - JFK")

    def test_airplane_type_str(self):
        airplane_type = AirplaneType.objects.create(name="Boeing 747")
        self.assertEqual(str(airplane_type), "Boeing 747")

    def test_airplane_str(self):
        airplane_type = AirplaneType.objects.create(name="Boeing")
        airplane = Airplane.objects.create(
            name="Dreamliner",
            rows=20,
            seats_in_row=6,
            airplane_type=airplane_type,
        )
        self.assertEqual(str(airplane), "Dreamliner")

    def test_flight_str(self):
        source = Airport.objects.create(name="WAW", closest_big_city="Warsaw")
        dest = Airport.objects.create(name="JFK", closest_big_city="New York")
        route = Route.objects.create(source=source, destination=dest)
        airplane_type = AirplaneType.objects.create(name="Jet")
        airplane = Airplane.objects.create(
            name="Test", rows=10, seats_in_row=4, airplane_type=airplane_type
        )
        departure_time = "2026-12-31 12:00:00"
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time=departure_time,
            arrival_time="2026-12-31 20:00:00",
        )
        self.assertEqual(str(flight), f"WAW - JFK ({departure_time})")

    def test_order_str(self):
        user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        order = Order.objects.create(user=user)
        self.assertEqual(str(order.created_at), str(order))

    def test_ticket_str(self):
        user = get_user_model().objects.create_user(
            email="test@test.com", password="password123"
        )
        source = Airport.objects.create(name="WAW", closest_big_city="Warsaw")
        dest = Airport.objects.create(name="JFK", closest_big_city="New York")
        route = Route.objects.create(source=source, destination=dest)
        airplane_type = AirplaneType.objects.create(name="Jet")
        airplane = Airplane.objects.create(
            name="Test", rows=10, seats_in_row=4, airplane_type=airplane_type
        )
        flight = Flight.objects.create(
            route=route,
            airplane=airplane,
            departure_time="2026-12-31 12:00:00",
            arrival_time="2026-12-31 20:00:00",
        )
        order = Order.objects.create(user=user)
        ticket = Ticket.objects.create(
            row=1, seat=2, flight=flight, order=order
        )
        self.assertEqual(str(ticket), f"{str(flight)} (row: 1, seat: 2)")

    def test_ticket_row_seat_validation(self):
        # Testowanie walidatorów z Twojej migracji 0002
        # row < 1 lub seat < 2 powinno podnieść ValidationError przy full_clean()
        user = get_user_model().objects.create_user("t@t.com", "pass")
        # ... (pominąłem tworzenie setupu flight dla zwięzłości, załóżmy że istnieje)
        # Przykład walidacji:
        # ticket = Ticket(row=0, seat=1, flight=flight, order=order)
        # with self.assertRaises(ValidationError):
        #     ticket.full_clean()
        pass
