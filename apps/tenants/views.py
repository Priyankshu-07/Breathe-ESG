from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.tenants.serializers import OrganisationSerializer
from apps.common.permissions import IsTenantMember


class MyOrganisationView(APIView):

    permission_classes = [IsTenantMember]

    def get(self, request):

        organisation = getattr(
            request.user,
            'organisation',
            None
        )

        if organisation is None:

            return Response(
                {
                    'detail':
                    'User does not belong to any organisation.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = OrganisationSerializer(
            organisation
        )

        return Response(serializer.data)