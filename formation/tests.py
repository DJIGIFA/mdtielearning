from django.test import TestCase

# Create your tests here.


def minute_to_heure(minute: int):
    h = minute // 60
    minute = minute % 60

    if h > 0:
        return f"{h}h : {minute}m"
    return f"{minute}m"

print(minute_to_heure(50))