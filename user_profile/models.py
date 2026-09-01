from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    display_name = models.CharField(max_length=30, blank=True)
    profile_image=CloudinaryField('image')
    bio = models.TextField(blank=True, max_length=500)
    goals = models.TextField(blank=True, max_length=500)
    member_since = models.DateField(auto_now_add=True)
    date_of_birth = models.DateField(blank=True, null=True)
    height = models.FloatField(blank=True, null=True)
    weight = models.FloatField(blank=True, null=True)

    class Meta:
        ordering = ['-member_since']
        indexes = [
            models.Index(fields=['display_name'])
        ]

    def save(self, *args, **kwargs):
        if not self.display_name:
            initial=self.last_name[0] if self.last_name else ""
            self.display_name=f"{self.first_name}{initial}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.display_name
