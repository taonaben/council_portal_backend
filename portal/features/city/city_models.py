from django.db import models
import uuid


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CitySection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    section = models.CharField(
        max_length=50,
        choices=[
            ("low", "low"),
            ("medium", "medium"),
            ("high", "high"),
            ("cbd", "cbd"),
        ],
    )

    def __str__(self):
        return self.name + " - " + self.city.name
