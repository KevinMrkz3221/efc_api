from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Organizacion, UsoAlmacenamiento

@receiver(post_save, sender=Organizacion)
def crear_uso_almacenamiento(sender, instance, created, **kwargs):
    if created:
        UsoAlmacenamiento.objects.create(organizacion=instance, espacio_utilizado=0)