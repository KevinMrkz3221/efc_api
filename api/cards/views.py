from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import F
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from core.permissions import (
    IsSameOrganization, 
    IsSameOrganizationDeveloper,
    IsSameOrganizationAndAdmin,
    IsSuperUser
)

from api.organization.models import UsoAlmacenamiento, Organizacion
from api.record.models import Document
from api.customs.models import ProcesamientoPedimento
from api.logger.models import UserActivity, RequestLog

from api.logger.mixins import LoggingMixin
from mixins.filtrado_organizacion import FiltroPorOrganizacionMixin

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.logger.models import UserActivity, RequestLog, UserActivity


# Create your views here.
class DocumentUtilInformation(LoggingMixin, APIView, FiltroPorOrganizacionMixin):
    """
    View to get the total storage used by the organization and stats of documents added in last 1, 7, and 30 days.
    Permite filtrar por fecha usando los parámetros ?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = Document

    my_tags = ['Cards']

    @swagger_auto_schema(
        operation_description="Get total storage used and document stats. Permite filtrar por fecha de documentos.",
        manual_parameters=[
            openapi.Parameter('fecha_inicio', openapi.IN_QUERY, description="Fecha de inicio (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_fin', openapi.IN_QUERY, description="Fecha de fin (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Document stats",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "archivos_ultimas_1_dia": openapi.Schema(type=openapi.TYPE_INTEGER, description="Archivos en el último día"),
                        "archivos_ultimos_7_dias": openapi.Schema(type=openapi.TYPE_INTEGER, description="Archivos en los últimos 7 días"),
                        "archivos_ultimos_30_dias": openapi.Schema(type=openapi.TYPE_INTEGER, description="Archivos en los últimos 30 días"),
                        "archivos_filtrados": openapi.Schema(type=openapi.TYPE_INTEGER, description="Archivos en el rango de fechas")
                    }
                ),
                examples={
                    "application/json": {
                        "archivos_ultimas_1_dia": 5,
                        "archivos_ultimos_7_dias": 20,
                        "archivos_ultimos_30_dias": 50,
                        "archivos_filtrados": 10
                        }
                }
            )
        }
    )

    def get_queryset(self):
        return self.get_queryset_filtrado()
        
    def get(self, request):
        queryset = self.get_queryset()
        now = timezone.now()
        count_1 = queryset.filter(created_at__gte=now - timedelta(days=1)).count()
        count_7 = queryset.filter(created_at__gte=now - timedelta(days=7)).count()
        count_30 = queryset.filter(created_at__gte=now - timedelta(days=30)).count()

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        docs_filtrados = queryset

        if fecha_inicio:
            docs_filtrados = docs_filtrados.filter(created_at__gte=fecha_inicio)
        if fecha_fin:
            docs_filtrados = docs_filtrados.filter(created_at__lte=fecha_fin)
        count_filtrados = docs_filtrados.count()
        return Response({
            "archivos_ultimas_1_dia": count_1,
            "archivos_ultimos_7_dias": count_7,
            "archivos_ultimos_30_dias": count_30,
            "archivos_filtrados": count_filtrados
        })

class ViewPedimentoServicesUtilInformation(LoggingMixin, APIView, FiltroPorOrganizacionMixin):
    """
    View para obtener información de uso de servicios relacionados con pedimentos.
    Devuelve la cantidad de procesos por estado (1: espera, 2: proceso, 3: finalizado, 4: error) para la organización.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = Document
    my_tags = ['Cards']

    @swagger_auto_schema(
        operation_description="Get services stats. Permite filtrar por fecha de procesos.",
        manual_parameters=[
            openapi.Parameter('fecha_inicio', openapi.IN_QUERY, description="Fecha de inicio (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_fin', openapi.IN_QUERY, description="Fecha de fin (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Services stats",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "en_espera": openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad de procesos en espera"), 
                        "en_proceso": openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad de procesos en proceso"),
                        "finalizados": openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad de procesos finalizados"),
                        "con_error": openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad de procesos con error"),
                        "procesos_filtrados": openapi.Schema(type=openapi.TYPE_INTEGER, description="Procesos en el rango de fechas")
                    }
                ),
                examples={
                    "application/json": {
                        "en_espera": 1, 
                        "en_proceso": 2,
                        "finalizados": 3,
                        "con_error": 4,
                        "procesos_filtrados": 5
                    }
                }
            )
        }
    )

    def get_queryset(self):
        if not self.request.user.is_authenticated or not hasattr(self.request.user, 'organizacion'):
            return None
        
        # Si es super usuario, devuelve todos los procesos
        if self.request.user.is_superuser:
            return ProcesamientoPedimento.objects.all()

        # Si es Administrador de la organizacion devuelve todos los servicios de la organizacion
        if self.request.user.is_authenticated and self.request.user.groups.filter(name='admin').exists() and self.request.user.groups.filter(name='Agente Aduanal').exists():
            return ProcesamientoPedimento.objects.filter(pedimento__organizacion=self.request.user.organizacion)

        # Si es Desarrollador de la organizacion devuelve todos los servicios de la organizacion
        if self.request.user.is_authenticated and self.request.user.groups.filter(name='developer').exists() and self.request.user.groups.filter(name='Agente Aduanal').exists():
            return self.request.user.organizacion.procesamiento_pedimentos.all()
        
        if self.request.user.is_authenticated and self.request.user.groups.filter(name='user').exists() and self.request.user.groups.filter(name='Agente Aduanal').exists():
            return self.request.user.organizacion.procesamiento_pedimentos.all()

        # Si es importador de la organizacion, devuelve los servicios relacionados con sus pedimentos
        if self.request.user.is_authenticated and self.request.user.groups.filter(name='importador').exists() and self.request.user.is_importador and self.request.user.groups.filter(name='user').exists():
            return self.request.user.organizacion.procesamiento_pedimentos.filter(pedimento__contribuyente=self.request.user.rfc)

        
        
        # Si es parte de una organización, filtrar por esa organización
        return ProcesamientoPedimento.objects.filter(pedimento__organizacion=self.request.user.organizacion)

    def get(self, request):
        queryset = self.get_queryset()
        if queryset is None:
            return Response({"error": "Usuario no autenticado o sin organización"}, status=401)
        en_espera = queryset.filter(estado=1).count()
        en_proceso = queryset.filter(estado=2).count()
        finalizados = queryset.filter(estado=3).count()
        con_error = queryset.filter(estado=4).count()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        procesos_filtrados = queryset
        if fecha_inicio:
            procesos_filtrados = procesos_filtrados.filter(created_at__gte=fecha_inicio)
        if fecha_fin:
            procesos_filtrados = procesos_filtrados.filter(created_at__lte=fecha_fin)
        count_filtrados = procesos_filtrados.count()
        return Response({
            "en_espera": en_espera,
            "en_proceso": en_proceso,
            "finalizados": finalizados,
            "con_error": con_error,
            "procesos_filtrados": count_filtrados
        })

class UserActivityAnalysis(LoggingMixin, APIView, FiltroPorOrganizacionMixin):
    """
    Endpoint para análisis de actividades de usuario.
    Devuelve el conteo de acciones por tipo y los 5 usuarios más activos.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    
    model = UserActivity

    my_tags = ['Cards']

    @swagger_auto_schema(
        operation_description="Get analysis of user activities. Permite filtrar por fecha de actividades.",
        manual_parameters=[
            openapi.Parameter('fecha_inicio', openapi.IN_QUERY, description="Fecha de inicio (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_fin', openapi.IN_QUERY, description="Fecha de fin (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="User activity analysis",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "actions_count": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad por acción")
                        ),
                        "top_users": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "username": openapi.Schema(type=openapi.TYPE_STRING),
                                    "activity_count": openapi.Schema(type=openapi.TYPE_INTEGER)
                                }
                            ),
                            description="Top 5 usuarios más activos"
                        ),
                        "actividades_filtradas": openapi.Schema(type=openapi.TYPE_INTEGER, description="Actividades en el rango de fechas")
                    }
                ),
                examples={
                    "application/json": {
                        "actions_count": {
                            "login": 20,
                            "logout": 18,
                            "create": 15,
                            "update": 10,
                            "delete": 5,
                            "view": 30,
                            "search": 12,
                            "export": 3,
                            "import": 2
                        },
                        "top_users": [
                            {"username": "admin", "activity_count": 25},
                            {"username": "user1", "activity_count": 20}
                        ],
                        "actividades_filtradas": 10
                    }
                }
            )
        }
    )
    def get_queryset(self):
        return  self.get_queryset_filtrado()

    def get(self, request):
        queryset = self.get_queryset()
        User = get_user_model()
        actions = [a[0] for a in UserActivity.ACTIONS]
        actions_count = {a: queryset.filter(action=a).count() for a in actions}
        # Top 5 usuarios más activos
        top_users = []
        from django.db.models import Count
        top_users_qs = queryset.values('user').annotate(activity_count=Count('id')).order_by('-activity_count')[:5]
        for entry in top_users_qs:
            try:
                user_obj = User.objects.get(pk=entry['user'])
                top_users.append({"username": user_obj.username, "activity_count": entry['activity_count']})
            except User.DoesNotExist:
                continue
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        actividades_filtradas = queryset
        if fecha_inicio:
            actividades_filtradas = actividades_filtradas.filter(timestamp__gte=fecha_inicio)
        if fecha_fin:
            actividades_filtradas = actividades_filtradas.filter(timestamp__lte=fecha_fin)
        count_filtrados = actividades_filtradas.count()
        return Response({
            "actions_count": actions_count,
            "top_users": top_users,
            "actividades_filtradas": count_filtrados
        })

class RequestLogAnalysis(LoggingMixin, APIView, FiltroPorOrganizacionMixin):
    """
    Endpoint para análisis de logs de peticiones.
    Devuelve el conteo por método, los paths más solicitados y el promedio de tiempo de respuesta.
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = RequestLog

    my_tags = ['Cards']

    @swagger_auto_schema(
        operation_description="Get analysis of request logs. Permite filtrar por fecha de logs.",
        manual_parameters=[
            openapi.Parameter('fecha_inicio', openapi.IN_QUERY, description="Fecha de inicio (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_fin', openapi.IN_QUERY, description="Fecha de fin (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Request log analysis",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "methods_count": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            additional_properties=openapi.Schema(type=openapi.TYPE_INTEGER, description="Cantidad por método")
                        ),
                        "top_paths": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "path": openapi.Schema(type=openapi.TYPE_STRING),
                                    "count": openapi.Schema(type=openapi.TYPE_INTEGER)
                                }
                            ),
                            description="Top 5 paths más solicitados"
                        ),
                        "avg_response_time": openapi.Schema(type=openapi.TYPE_NUMBER, format='float', description="Promedio de tiempo de respuesta (ms)"),
                        "logs_filtrados": openapi.Schema(type=openapi.TYPE_INTEGER, description="Logs en el rango de fechas")
                    }
                ),
                examples={
                    "application/json": {
                        "methods_count": {
                            "GET": 120,
                            "POST": 30,
                            "PUT": 10,
                            "DELETE": 5
                        },
                        "top_paths": [
                            {"path": "/api/v1/record/documents/", "count": 50},
                            {"path": "/api/v1/customs/pedimentos/", "count": 40}
                        ],
                        "avg_response_time": 120.5,
                        "logs_filtrados": 15
                    }
                }
            )
        }
    )
    def get_queryset(self):
        return self.get_queryset_filtrado()

    def get(self, request):
        queryset = self.get_queryset()
        from django.db.models import Count, Avg
        from api.logger.models import RequestLog
        methods = [m[0] for m in RequestLog.METHODS]
        methods_count = {m: queryset.filter(method=m).count() for m in methods}
        top_paths_qs = queryset.values('path').annotate(count=Count('id')).order_by('-count')[:5]
        top_paths = [{"path": entry['path'], "count": entry['count']} for entry in top_paths_qs]
        avg_response_time = queryset.aggregate(avg=Avg('response_time'))['avg'] or 0.0
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        logs_filtrados = queryset
        if fecha_inicio:
            logs_filtrados = logs_filtrados.filter(timestamp__gte=fecha_inicio)
        if fecha_fin:
            logs_filtrados = logs_filtrados.filter(timestamp__lte=fecha_fin)
        count_filtrados = logs_filtrados.count()
        return Response({
            "methods_count": methods_count,
            "top_paths": top_paths,
            "avg_response_time": round(avg_response_time, 2),
            "logs_filtrados": count_filtrados
        })

class LastDocumentView(LoggingMixin, APIView, FiltroPorOrganizacionMixin):
    """
        View que obtiene los ultimos 10 documentos agregados.
        Permite filtrar por fecha usando los parámetros ?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD
    """
    permission_classes = [IsAuthenticated &  (IsSameOrganization | IsSameOrganizationAndAdmin | IsSameOrganizationDeveloper | IsSuperUser)]
    model = Document

    my_tags = ['Cards']

    @swagger_auto_schema(
        operation_description="Obtiene los últimos 10 documentos agregados. Permite filtrar por fecha de creación.",
        manual_parameters=[
            openapi.Parameter('fecha_inicio', openapi.IN_QUERY, description="Fecha de inicio (YYYY-MM-DD)", type=openapi.TYPE_STRING),
            openapi.Parameter('fecha_fin', openapi.IN_QUERY, description="Fecha de fin (YYYY-MM-DD)", type=openapi.TYPE_STRING),
        ],
        responses={
            200: openapi.Response(
                description="Lista de los últimos 10 documentos",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "documentos": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                                    "archivo": openapi.Schema(type=openapi.TYPE_STRING, description="Ruta del archivo"),
                                    "extension": openapi.Schema(type=openapi.TYPE_STRING),
                                    "size": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "created_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                                    "updated_at": openapi.Schema(type=openapi.TYPE_STRING, format="date-time"),
                                    "organizacion": openapi.Schema(type=openapi.TYPE_STRING),
                                    "pedimento": openapi.Schema(type=openapi.TYPE_STRING)
                                }
                            ),
                            description="Últimos 10 documentos agregados"
                        ),
                        "total_filtrados": openapi.Schema(type=openapi.TYPE_INTEGER, description="Total de documentos en el rango de fechas")
                    }
                ),
                examples={
                    "application/json": {
                        "documentos": [
                            {"id": "b7e6c8e2-1a2b-4c3d-8e9f-123456789abc", "archivo": "documents/doc1.pdf", "extension": "pdf", "size": 123456, "created_at": "2025-07-14T10:00:00Z", "updated_at": "2025-07-14T10:00:00Z", "organizacion": "Org1", "pedimento": "Ped1"}
                        ],
                        "total_filtrados": 1
                    }
                }
            )
        }
    )
    def get_queryset(self):
        return self.get_queryset_filtrado()

    def get(self, request):
        queryset = self.get_queryset()
        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        documentos = queryset
        if fecha_inicio:
            documentos = documentos.filter(created_at__gte=fecha_inicio)
        if fecha_fin:
            documentos = documentos.filter(created_at__lte=fecha_fin)
        total_filtrados = documentos.count()
        ultimos = documentos[:10]
        docs_serializados = []
        for doc in ultimos:
            docs_serializados.append({
                "id": str(doc.id),
                "archivo": doc.archivo.name if doc.archivo else '',
                "extension": doc.extension,
                "size": doc.size,
                "created_at": doc.created_at.isoformat() if doc.created_at else '',
                "updated_at": doc.updated_at.isoformat() if doc.updated_at else '',
                "organizacion": str(doc.organizacion) if doc.organizacion else '',
                "pedimento": str(doc.pedimento) if doc.pedimento else ''
            })
        return Response({
            "documentos": docs_serializados,
            "total_filtrados": total_filtrados
        })
    