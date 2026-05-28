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

class IngestionJobListView(generics.ListAPIView):

    serializer_class = IngestionJobListSerializer

    def get_queryset(self):

        return IngestionJob.objects.filter(
            organisation_id=1
        ).order_by('-created_at')


class IngestionJobDetailView(generics.RetrieveAPIView):

    serializer_class = IngestionJobSerializer

    def get_queryset(self):

        return IngestionJob.objects.filter(
            organisation_id=1
        ).prefetch_related('rows')


class IngestionUploadView(APIView):

    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):

        serializer = IngestionUploadSerializer(data=request.data)

        if not serializer.is_valid():

            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        file = serializer.validated_data['file']
        source_type = serializer.validated_data['source_type']

        job = IngestionJob.objects.create(
            organisation_id=1,
            uploaded_by=None,
            source_type=source_type,
            file=file,
            raw_filename=file.name,
            status='pending',
        )
        try:

            ingest_and_normalize(job)

        except Exception as e:

            job.status = 'failed'
            job.save()

            return Response(
                {
                    'detail': 'Ingestion failed.',
                    'error': str(e),
                    'job_id': str(job.id),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return Response(
            IngestionJobSerializer(job).data,
            status=status.HTTP_201_CREATED
        )


class IngestionRowListView(generics.ListAPIView):
    serializer_class = IngestionRowSerializer

    def get_queryset(self):

        job_id = self.kwargs['job_id']
        try:

            job = IngestionJob.objects.get(
                id=job_id,
                organisation_id=1
            )

        except IngestionJob.DoesNotExist:

            return IngestionRow.objects.none()

        qs = IngestionRow.objects.filter(
            job=job
        ).order_by('row_index')
        row_status = self.request.query_params.get('status')

        if row_status:

            qs = qs.filter(status=row_status)

        return qs