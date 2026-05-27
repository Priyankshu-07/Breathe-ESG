import uuid
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from apps.users.models import User
from apps.tenants.models import Organisation


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='audit_events')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    # generic FK — can point at any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey('content_type', 'object_id')

    verb = models.CharField(max_length=100)   # e.g. "approved", "ingested", "edited"
    detail = models.JSONField(default=dict)   # any extra context
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.actor} {self.verb} @ {self.timestamp}"