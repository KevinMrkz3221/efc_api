from api.organization.models import UsoAlmacenamiento


def verificar_espacio_disponible(organizacion, tamaño_archivo):
    try:
        uso = UsoAlmacenamiento.objects.get(organizacion=organizacion)
        if uso.espacio_disponible < tamaño_archivo:
            raise ValueError("La organización no tiene suficiente espacio de almacenamiento disponible")
        return True
    except UsoAlmacenamiento.DoesNotExist:
        # Si no existe registro, crear uno
        UsoAlmacenamiento.objects.create(organizacion=organizacion, espacio_utilizado=0)
        return True