from django.urls import path
from apps.tenants.views import MyOrganisationView

urlpatterns = [
    path('me/', MyOrganisationView.as_view(), name='tenant-me'),
]