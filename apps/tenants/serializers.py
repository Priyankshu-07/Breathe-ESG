from rest_framework import serializers
from apps.tenants.models import Organisation


class OrganisationSerializer(serializers.ModelSerializer):
    user_count = serializers.SerializerMethodField()

    class Meta:
        model = Organisation
        fields = [
            'id',
            'name',
            'slug',
            'user_count',
            'created_at',
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'user_count']

    def get_user_count(self, obj) -> int:
        return obj.users.count()