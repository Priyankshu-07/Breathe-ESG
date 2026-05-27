from django.urls import path
from apps.ingestion.views import (
    IngestionJobListView,
    IngestionJobDetailView,
    IngestionUploadView,
    IngestionRowListView,
)

urlpatterns = [
    path('upload/',                          IngestionUploadView.as_view(),    name='ingest-upload'),
    path('jobs/',                            IngestionJobListView.as_view(),   name='ingest-job-list'),
    path('jobs/<uuid:pk>/',                  IngestionJobDetailView.as_view(), name='ingest-job-detail'),
    path('jobs/<uuid:job_id>/rows/',         IngestionRowListView.as_view(),   name='ingest-row-list'),
]