import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organizacion = models.ForeignKey('organization.Organizacion', on_delete=models.CASCADE, null=True, blank=True, related_name='users')
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)

    is_importador = models.BooleanField(default=False, help_text="Indicates if the user is an importer")
    rfc = models.CharField(max_length=13, unique=True, null=True, blank=True, help_text="RFC of the user")

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'Custom User'
        verbose_name_plural = 'Custom Users'
        ordering = ['username']