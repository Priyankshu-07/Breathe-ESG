from django.urls import path
from apps.review.views import (
    ReviewActionListView,
    ApproveEmissionView,
    RejectEmissionView,
    FlagEmissionView,
    BulkReviewView,
    LockForAuditView,
)
urlpatterns = [
    path('actions/',                        ReviewActionListView.as_view(), name='review-actions'),
    path('bulk/',                           BulkReviewView.as_view(),       name='review-bulk'),
    path('lock/',                           LockForAuditView.as_view(),     name='review-lock'),
    path('<uuid:emission_id>/approve/',     ApproveEmissionView.as_view(),  name='review-approve'),
    path('<uuid:emission_id>/reject/',      RejectEmissionView.as_view(),   name='review-reject'),
    path('<uuid:emission_id>/flag/',        FlagEmissionView.as_view(),     name='review-flag'),
]