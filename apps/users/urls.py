from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from apps.users.views import RegisterView, MeView

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
]