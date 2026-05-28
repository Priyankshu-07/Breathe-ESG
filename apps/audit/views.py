from rest_framework import generics
from apps.audit.models import AuditEvent
from apps.audit.serializers import AuditEventSerializer
class AuditEventListView(generics.ListAPIView):
    serializer_class = AuditEventSerializer
    ordering = ['-timestamp']
    def get_queryset(self):
        return (
            AuditEvent.objects
            .filter(
                organisation_id=1
            )
            .select_related(
                'actor',
                'organisation',
            )
        )