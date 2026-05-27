from decimal import Decimal
from rest_framework import serializers
from apps.emissions.models import NormalizedEmission
class NormalizedEmissionSerializer(serializers.ModelSerializer):
    source_type      = serializers.CharField(source='source_row.job.source_type', read_only=True)
    ingestion_job_id = serializers.UUIDField(source='source_row.job.id', read_only=True)
    row_index        = serializers.IntegerField(source='source_row.row_index', read_only=True)
    organisation_name = serializers.CharField(source='organisation.name', read_only=True)
    warnings = serializers.CharField(source='source_row.error_message', read_only=True)
    class Meta:
        model = NormalizedEmission
        fields = [
            'id',
            'organisation_name',
            'scope',
            'category',
            'activity_value',
            'activity_unit',
            'co2e_kg',
            'period_start',
            'period_end',
            'original_value',
            'original_unit',
            'emission_factor_used',
            'emission_factor_source',
            'status',
            'is_edited',
            'source_type',
            'ingestion_job_id',
            'row_index',
            'warnings',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'scope', 'category', 'organisation_name',
            'source_type', 'ingestion_job_id', 'row_index',
            'warnings', 'created_at', 'updated_at', 'is_edited',
        ]
class EmissionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NormalizedEmission
        fields = ['activity_value', 'activity_unit']
    def validate(self, attrs):
        if self.instance and self.instance.status == 'locked':
            raise serializers.ValidationError(
                "Locked emissions cannot be edited. "
                "This record has been submitted for audit."
            )
        return attrs
    def update(self, instance, validated_data):
        instance.activity_value = validated_data.get('activity_value', instance.activity_value)
        instance.activity_unit  = validated_data.get('activity_unit', instance.activity_unit)
        instance.co2e_kg   = None
        instance.is_edited = True
        instance.save()
        return instance