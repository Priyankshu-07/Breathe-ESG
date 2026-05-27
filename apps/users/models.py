import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.tenants.models import Organisation


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE,
        related_name='users', null=True, blank=True
    )

    ROLES = [('admin', 'Admin'), ('analyst', 'Analyst'), ('viewer', 'Viewer')]
    role = models.CharField(max_length=20, choices=ROLES, default='analyst')

    def __str__(self):
        return f"{self.email} ({self.organisation})"