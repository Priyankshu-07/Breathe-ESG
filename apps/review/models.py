import uuid
from django.db import models
from apps.users.models import User
from apps.emissions.models import NormalizedEmission


class ReviewAction(models.Model):
    ACTION_CHOICES = [
        ('approve', 'Approved'),
        ('reject', 'Rejected'),
        ('flag', 'Flagged for Follow-up'),
        ('edit', 'Edited'),
        ('lock', 'Locked for Audit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    emission = models.ForeignKey(NormalizedEmission, on_delete=models.CASCADE, related_name='review_actions')
    analyst = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    note = models.TextField(blank=True)
    previous_value = models.JSONField(null=True, blank=True)  # snapshot before edit
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} | {self.emission_id} | {self.analyst}"