from django.db import models
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils import timezone


class Crew(models.Model):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Airport(models.Model):
    name = models.CharField(max_length=255)
    closest_big_city = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Route(models.Model):
    source = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="source_routes"
    )
    destination = models.ForeignKey(
        Airport, on_delete=models.CASCADE, related_name="destination_routes"
    )

    def __str__(self):
        return f"{self.source} -> {self.destination}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField(validators=[MinValueValidator(1)])
    seats_in_row = models.IntegerField(validators=[MinValueValidator(1)])
    airplane_type = models.ForeignKey(
        AirplaneType, on_delete=models.CASCADE, related_name="airplane"
    )

    def __str__(self):
        return f"{self.name} {self.airplane_type.name}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="order",
    )

    def __str__(self):
        return f"{self.user} {self.created_at}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route, on_delete=models.CASCADE, related_name="flights"
    )
    airplane = models.ForeignKey(
        Airplane, on_delete=models.CASCADE, related_name="flights"
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, blank=True, related_name="flights")

    def clean(self):
        super().clean()

        now_with_margin = timezone.now() - timedelta(minutes=2)

        if self.departure_time and self.arrival_time:
            if self.departure_time >= self.arrival_time:
                raise ValidationError(
                    {
                        "arrival_time": (
                            "arrival time need to be after departure"
                            "(can't be on same time)"
                        )
                    }
                )
            if self.departure_time < now_with_margin:
                raise ValidationError(
                    {"departure_time": "departure time can't be in pass"}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
<<<<<<< HEAD
        return (
            f"{self.route} {self.airplane} "
            f"{self.departure_time} {self.arrival_time}"
        )
=======
        return f"{self.route} | {self.airplane} | {self.departure_time}"
>>>>>>> 7254425 (fix: correct string representation in Flight model and improve error message in FlightSerializer)


class Ticket(models.Model):
    row = models.IntegerField(validators=[MinValueValidator(1)])

    seat = models.IntegerField(validators=[MinValueValidator(1)])
    flight = models.ForeignKey(
        Flight, on_delete=models.CASCADE, related_name="tickets"
    )
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="tickets"
    )

    class Meta:
        unique_together = ("row", "seat", "flight", "order")
        ordering = ["flight", "row", "seat"]

    def clean(self):
        if self.row > self.flight.airplane.rows:
            raise ValidationError(f"Row {self.row} out of range")
        if self.seat > self.flight.airplane.seats_in_row:
            raise ValidationError(f"Seat {self.seat} out of range")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{str(self.flight)} (row: {self.row}, seat: {self.seat})"
