from rest_framework import serializers
from apps.audit.models import AuditEvent

class AuditEventSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField()
    
    class Meta:
        model = AuditEvent
        fields = [
            'id',
            'verb',
            'detail',
            'timestamp',
            'actor',
            'object_id',
            'content_type',
        ]