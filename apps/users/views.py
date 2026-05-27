from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        organisation_id = request.data.get('organisation_id')

        if not email or not password:
            return Response({'detail': 'Email and password required.'}, status=400)

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            organisation_id=organisation_id,
        )
        return Response({'detail': 'User created.'}, status=status.HTTP_201_CREATED)


class MeView(APIView):
    def get(self, request):
        user = request.user
        return Response({
            'id': str(user.id),
            'email': user.email,
            'role': user.role,
            'organisation': str(user.organisation_id),
        })