from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.review.models import ReviewAction
from apps.review.serializers import (
    ReviewActionSerializer,
    BulkReviewSerializer,
)
from apps.review.services import (
    approve_emission,
    reject_emission,
    flag_emission,
    lock_all_approved,
    bulk_review,
)


class ReviewActionListView(generics.ListAPIView):

    serializer_class = ReviewActionSerializer

    def get_queryset(self):

        return (
            ReviewAction.objects
            .filter(
                emission__organisation_id=1
            )
            .select_related(
                'analyst',
                'emission'
            )
            .order_by('-created_at')
        )


class ApproveEmissionView(APIView):

    def post(self, request, emission_id):

        try:

            action = approve_emission(emission_id, None)

            return Response(
                ReviewActionSerializer(action).data,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class RejectEmissionView(APIView):

    def post(self, request, emission_id):

        note = request.data.get('note', '')

        try:

            action = reject_emission(emission_id, None, note)

            return Response(
                ReviewActionSerializer(action).data,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class FlagEmissionView(APIView):

    def post(self, request, emission_id):

        note = request.data.get('note', '')

        try:

            action = flag_emission(emission_id, None, note)

            return Response(
                ReviewActionSerializer(action).data,
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BulkReviewView(APIView):

    def post(self, request):

        serializer = BulkReviewSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        result = bulk_review(
            emission_ids=serializer.validated_data['emission_ids'],
            action=serializer.validated_data['action'],
            analyst=None,
            note=serializer.validated_data.get('note', ''),
        )

        return Response(
            result,
            status=status.HTTP_200_OK
        )


class LockForAuditView(APIView):

    def post(self, request):

        try:

            count = lock_all_approved(1, None)

            return Response(
                {
                    'detail': f'{count} emissions locked for audit.'
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:

            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )