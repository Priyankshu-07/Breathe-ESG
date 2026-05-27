from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from apps.emissions.models import NormalizedEmission
from apps.emissions.serializers import (
    NormalizedEmissionSerializer,
    EmissionUpdateSerializer,
)
from apps.audit.models import AuditEvent
from apps.common.permissions import IsTenantMember
class EmissionListView(generics.ListAPIView):
    serializer_class = NormalizedEmissionSerializer
    permission_classes = [IsTenantMember]
    filter_backends = [
        DjangoFilterBackend,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        'scope',
        'category',
        'status',
        'period_start',
        'period_end',
    ]
    ordering_fields = [
        'period_start',
        'co2e_kg',
        'created_at',
    ]
    ordering = ['-created_at']
    def get_queryset(self):
        return (
            NormalizedEmission.objects
            .filter(
                organisation=self.request.user.organisation
            )
            .select_related(
                'source_row',
                'source_row__job',
                'organisation',
            )
        )
class FlaggedEmissionListView(generics.ListAPIView):
    serializer_class = NormalizedEmissionSerializer
    permission_classes = [IsTenantMember]
    ordering = ['-created_at']
    def get_queryset(self):
        return (
            NormalizedEmission.objects
            .filter(
                organisation=self.request.user.organisation
            )
            .filter(
                Q(source_row__status='warning') |
                Q(source_row__status='error')
            )
            .select_related(
                'source_row',
                'source_row__job',
                'organisation',
            )
        )
class EmissionDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsTenantMember]
    def get_queryset(self):
        return (
            NormalizedEmission.objects
            .filter(
                organisation=self.request.user.organisation
            )
            .select_related(
                'source_row',
                'source_row__job',
                'organisation',
            )
        )
    def get_serializer_class(self):
        if self.request.method in ('PUT', 'PATCH'):
            return EmissionUpdateSerializer
        return NormalizedEmissionSerializer
    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.status == 'locked':
            return Response(
                {
                    'detail':
                    'This emission has been locked for audit '
                    'and can no longer be edited.'
                },
                status=status.HTTP_403_FORBIDDEN
            )
        old_value = {
            'activity_value': str(instance.activity_value),
            'activity_unit': instance.activity_unit,
            'co2e_kg': (
                str(instance.co2e_kg)
                if instance.co2e_kg is not None
                else None
            ),
        }
        response = super().update(request, *args, **kwargs)
        instance.refresh_from_db()
        new_value = {
            'activity_value': str(instance.activity_value),
            'activity_unit': instance.activity_unit,
            'co2e_kg': (
                str(instance.co2e_kg)
                if instance.co2e_kg is not None
                else None
            ),
        }
        AuditEvent.objects.create(
            organisation=request.user.organisation,
            actor=request.user,
            content_object=instance,
            verb='emission_updated',
            detail={
                'old': old_value,
                'new': new_value,
            }
        )

        return response
class EmissionSummaryView(APIView):
    permission_classes = [IsTenantMember]
    def get(self, request):
        qs = (
            NormalizedEmission.objects
            .filter(
                organisation=request.user.organisation
            )
            .exclude(status='rejected')
        )
        scope_summary = (
            qs.values('scope')
            .annotate(
                total_co2e=Sum('co2e_kg'),
                row_count=Count('id'),
            )
        )
        summary = {
            'scope1': {
                'total_co2e_kg': 0,
                'row_count': 0,
            },
            'scope2': {
                'total_co2e_kg': 0,
                'row_count': 0,
            },
            'scope3': {
                'total_co2e_kg': 0,
                'row_count': 0,
            },
        }
        for item in scope_summary:
            summary[item['scope']] = {
                'total_co2e_kg': item['total_co2e'] or 0,
                'row_count': item['row_count'],
            }
        summary['review_status'] = {
            'pending_review': qs.filter(status='pending_review').count(),
            'approved': qs.filter(status='approved').count(),
            'locked': qs.filter(status='locked').count(),
            'rejected': qs.filter(status='rejected').count(),
        }
        summary['flagged_rows'] = qs.filter(
            Q(source_row__status='warning') |
            Q(source_row__status='error')
        ).count()
        return Response(summary)