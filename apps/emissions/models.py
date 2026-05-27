import uuid
from django.db import models
from apps.tenants.models import Organisation
from apps.ingestion.models import IngestionRow


class NormalizedEmission(models.Model):
    SCOPE_CHOICES = [
        ('scope1', 'Scope 1 - Direct'),
        ('scope2', 'Scope 2 - Electricity'),
        ('scope3', 'Scope 3 - Value Chain'),
    ]
    CATEGORY_CHOICES = [
        ('fuel_combustion', 'Fuel Combustion'),
        ('electricity', 'Electricity'),
        ('business_travel_flight', 'Business Travel - Flight'),
        ('business_travel_hotel', 'Business Travel - Hotel'),
        ('business_travel_ground', 'Business Travel - Ground'),
        ('procurement', 'Procurement'),
    ]
    STATUS = [
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('locked', 'Locked for Audit'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organisation = models.ForeignKey(Organisation, on_delete=models.CASCADE, related_name='emissions')
    source_row = models.OneToOneField(IngestionRow, on_delete=models.CASCADE, related_name='emission')

    scope = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)

    # normalized values — always in kg CO2e and base SI units
    activity_value = models.DecimalField(max_digits=18, decimal_places=6)
    activity_unit = models.CharField(max_length=50)   # e.g. "kWh", "litres", "km"
    co2e_kg = models.DecimalField(max_digits=18, decimal_places=6, null=True, blank=True)

    # period
    period_start = models.DateField()
    period_end = models.DateField()

    # traceability
    original_unit = models.CharField(max_length=50)   # what the source file had
    original_value = models.DecimalField(max_digits=18, decimal_places=6)
    emission_factor_used = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True)
    emission_factor_source = models.CharField(max_length=255, blank=True)

    status = models.CharField(max_length=20, choices=STATUS, default='pending_review')
    is_edited = models.BooleanField(default=False)   # True if analyst changed a value
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category} | {self.co2e_kg} kg CO2e | {self.period_start}"