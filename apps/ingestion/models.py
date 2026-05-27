import uuid
from django.db import models
from apps.tenants.models import Organisation
from apps.users.models import User


class IngestionJob(models.Model):
    SOURCE_TYPES = [
        ('sap', 'SAP Fuel & Procurement'),
        ('utility', 'Utility / Electricity'),
        ('travel', 'Corporate Travel'),
    ]
    STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('done', 'Done'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='ingestion_jobs')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    file = models.FileField(upload_to='uploads/%Y/%m/%d/')
    raw_filename = models.CharField(max_length=255)
    row_count = models.IntegerField(default=0)
    error_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.source_type} | {self.organisation} | {self.created_at.date()}"


class IngestionRow(models.Model):
    STATUS = [
        ('ok', 'OK'),
        ('warning', 'Warning'),
        ('error', 'Error'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(IngestionJob, on_delete=models.CASCADE, related_name='rows')
    row_index = models.IntegerField()
    raw_data = models.JSONField()         # exact original row, never touched
    parsed_data = models.JSONField(null=True, blank=True)   # after parser runs
    status = models.CharField(max_length=20, choices=STATUS, default='ok')
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Row {self.row_index} | Job {self.job_id} | {self.status}"