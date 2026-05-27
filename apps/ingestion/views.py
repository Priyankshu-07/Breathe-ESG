from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from apps.ingestion.models import IngestionJob, IngestionRow
from apps.ingestion.serializers import (
    IngestionJobSerializer,
    IngestionJobListSerializer,
    IngestionRowSerializer,
    IngestionUploadSerializer,
)
from apps.ingestion.services import ingest_and_normalize
from apps.common.permissions import IsTenantMember, IsAnalyst


class IngestionJobListView(generics.ListAPIView):
    """
    GET /ingest/jobs/
    Lists all ingestion jobs for the analyst's organisation.
    Lightweight — no rows included.
    """
    serializer_class = IngestionJobListSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        return IngestionJob.objects.filter(
            organisation=self.request.user.organisation
        ).order_by('-created_at')


class IngestionJobDetailView(generics.RetrieveAPIView):
    """
    GET /ingest/jobs/<id>/
    Full detail including all ingestion rows.
    Used by analyst to inspect what came in and what failed.
    """
    serializer_class = IngestionJobSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        return IngestionJob.objects.filter(
            organisation=self.request.user.organisation
        ).prefetch_related('rows')


class IngestionUploadView(APIView):
    """
    POST /ingest/upload/
    Accepts a file upload and source_type.
    Creates an IngestionJob, runs parsers, runs normalization.
    Returns the job record so the frontend can poll or redirect.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsTenantMember, IsAnalyst]

    def post(self, request):
        serializer = IngestionUploadSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file        = serializer.validated_data['file']
        source_type = serializer.validated_data['source_type']

        # Create the job record first so we have an ID to return
        job = IngestionJob.objects.create(
            organisation  = request.user.organisation,
            uploaded_by   = request.user,
            source_type   = source_type,
            file          = file,
            raw_filename  = file.name,
            status        = 'pending',
        )

        # Run ingestion + normalization synchronously for prototype.
        # In production this would be a Celery task:
        #   ingest_and_normalize.delay(job.id)
        try:
            ingest_and_normalize(job)
        except Exception as e:
            job.status = 'failed'
            job.save()
            return Response(
                {
                    'detail': 'Ingestion failed.',
                    'error':  str(e),
                    'job_id': str(job.id),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            IngestionJobSerializer(job).data,
            status=status.HTTP_201_CREATED
        )


class IngestionRowListView(generics.ListAPIView):
    """
    GET /ingest/jobs/<job_id>/rows/
    Lists all rows for a specific job.
    Supports filtering by status so analysts can drill into errors.
    """
    serializer_class = IngestionRowSerializer
    permission_classes = [IsTenantMember]

    def get_queryset(self):
        job_id = self.kwargs['job_id']

        # Verify job belongs to this organisation
        try:
            job = IngestionJob.objects.get(
                id=job_id,
                organisation=self.request.user.organisation
            )
        except IngestionJob.DoesNotExist:
            return IngestionRow.objects.none()

        qs = IngestionRow.objects.filter(job=job).order_by('row_index')

        # Optional ?status=error filter
        row_status = self.request.query_params.get('status')
        if row_status:
            qs = qs.filter(status=row_status)

        return qs