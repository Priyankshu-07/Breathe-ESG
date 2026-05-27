from django.urls import path
from apps.emissions.views import (
    EmissionListView,
    FlaggedEmissionListView,
    EmissionDetailView,
    EmissionSummaryView,
)
urlpatterns = [
    path(
        '',
        EmissionListView.as_view(),
        name='emission-list',
    ),
    path(
        'flagged/',
        FlaggedEmissionListView.as_view(),
        name='emission-flagged',
    ),
    path(
        'summary/',
        EmissionSummaryView.as_view(),
        name='emission-summary',
    ),
    # GET /emissions/<uuid>/
    # PATCH /emissions/<uuid>/
    path(
        '<uuid:pk>/',
        EmissionDetailView.as_view(),
        name='emission-detail',
    ),
]