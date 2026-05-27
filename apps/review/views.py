from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.review.models import ReviewAction
from apps.review.serializers import ReviewActionSerializer, BulkReviewSerializer
from apps.review.services import (
    approve_emission, reject_emission, flag_emission,
    lock_all_approved, bulk_review
)
from apps.common.permissions import IsTenantMember, IsAnalyst
class ReviewActionListView(generics.ListAPIView):
    """
    GET /review/actions/
    Full audit trail of all review actions for this organisation.
    """
    serializer_class = ReviewActionSerializer
    permission_classes = [IsTenantMember]
    def get_queryset(self):
        return ReviewAction.objects.filter(
            emission__organisation=self.request.user.organisation
        ).select_related('analyst', 'emission').order_by('-created_at')
class ApproveEmissionView(APIView):
    permission_classes = [IsTenantMember, IsAnalyst]
    def post(self, request, emission_id):
        try:
            action = approve_emission(emission_id, request.user)
            return Response(ReviewActionSerializer(action).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class RejectEmissionView(APIView):
    permission_classes = [IsTenantMember, IsAnalyst]
    def post(self, request, emission_id):
        note = request.data.get('note', '')
        try:
            action = reject_emission(emission_id, request.user, note)
            return Response(ReviewActionSerializer(action).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class FlagEmissionView(APIView):
    permission_classes = [IsTenantMember, IsAnalyst]
    def post(self, request, emission_id):
        note = request.data.get('note', '')
        try:
            action = flag_emission(emission_id, request.user, note)
            return Response(ReviewActionSerializer(action).data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class BulkReviewView(APIView):
    permission_classes = [IsTenantMember, IsAnalyst]
    def post(self, request):
        serializer = BulkReviewSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        result = bulk_review(
            emission_ids=serializer.validated_data['emission_ids'],
            action=serializer.validated_data['action'],
            analyst=request.user,
            note=serializer.validated_data.get('note', ''),
        )
        return Response(result, status=status.HTTP_200_OK)
class LockForAuditView(APIView):
    permission_classes = [IsTenantMember, IsAnalyst]
    def post(self, request):
        try:
            count = lock_all_approved(request.user.organisation, request.user)
            return Response(
                {'detail': f'{count} emissions locked for audit.'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)