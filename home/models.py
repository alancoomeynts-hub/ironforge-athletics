from django.db import models


# Create your models here.
class Gym(models.Model):
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    description = models.TextField()
    opening_hours = models.TextField()
    address = models.TextField()

    def __str__(self):
        return self.name

class ContactSubmission(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Subject{self.subject} - {self.name}"
