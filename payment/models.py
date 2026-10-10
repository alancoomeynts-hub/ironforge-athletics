from django.db import models


# Create your models here.
class StripeEventLog(models.Model):
    event_id = models.CharField(max_length=255, unique=True)
    event_type = models.CharField(max_length=255)

    def __str__(self):
        return self.event_type
