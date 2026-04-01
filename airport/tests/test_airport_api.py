import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


from rest_framework import status
from rest_framework.test import APIClient

from airport.models import Airport, Route, AirplaneType, Airplane, Flight

FLIGHT_URL = reverse("airport:flight-list")


def sample_flight(**params):
    source = Airport.objects.create(name="London", closest_big_city="London")
    destination = Airport.objects.create(
        name="Paris", closest_big_city="Paris"
    )
    route = Route.objects.create(source=source, destination=destination)
    airplane_type = AirplaneType.objects.create(name="Jet")
    airplane = Airplane.objects.create(
        name="Test Plane", rows=10, seats_in_row=5, airplane_type=airplane_type
    )

    defaults = {
        "route": route,
        "airplane": airplane,
        "departure_time": "2026-10-10T10:00:00Z",
        "arrival_time": "2026-10-10T12:00:00Z",
    }
    defaults.update(params)

    return Flight.objects.create(**defaults)


class UnauthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required_for_orders(self):
        res = self.client.get(reverse("airport:order-list"))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_read_only_access_to_flights_allowed_for_anon(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthenticatedAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "password123"
        )
        self.client.force_authenticate(self.user)

    def test_create_order_authenticated(self):
        flight = sample_flight()
        payload = {
            "tickets_to_create": [{"row": 1, "seat": 1, "flight": flight.id}]
        }
        res = self.client.post(
            reverse("airport:order-list"), payload, format="json"
        )
        print(res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


class AdminAirportApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@test.com", "admin123"
        )
        self.client.force_authenticate(self.user)

    def test_create_airport_allowed_for_admin(self):
        payload = {"name": "JFK", "closest_big_city": "New York"}
        res = self.client.post(reverse("airport:airport-list"), payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Airport.objects.filter(name="JFK").exists())
