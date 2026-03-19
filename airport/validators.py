from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_date_is_future(value):
    if value > timezone.now():
        raise ValidationError("Date must be in the future")
