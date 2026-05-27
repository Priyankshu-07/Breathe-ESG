from rest_framework import generics

from apps.audit.models import AuditEvent
from apps.audit.serializers import AuditEventSerializer
from apps.common.permissions import IsTenantMember


class AuditEventListView(generics.ListAPIView):

    serializer_class = AuditEventSerializer

    permission_classes = [IsTenantMember]

    ordering = ['-timestamp']

    def get_queryset(self):

        return (
            AuditEvent.objects
            .filter(
                organisation=self.request.user.organisation
            )
            .select_related(
                'actor',
                'organisation',
            )
        )