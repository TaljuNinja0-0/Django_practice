from django.db import models
from django.contrib.auth.models import User

class Stock(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    name = models.CharField(max_length=50)
    sector = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.symbol} ({self.name})"
