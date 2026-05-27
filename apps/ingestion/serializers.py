from rest_framework import serializers
from apps.ingestion.models import IngestionJob, IngestionRow


class IngestionRowSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngestionRow
        fields = [
            'id',
            'row_index',
            'raw_data',
            'parsed_data',
            'status',
            'error_message',
            'created_at',
        ]
        read_only_fields = fields


class IngestionJobSerializer(serializers.ModelSerializer):
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)
    rows              = IngestionRowSerializer(many=True, read_only=True)

    class Meta:
        model = IngestionJob
        fields = [
            'id',
            'source_type',
            'status',
            'raw_filename',
            'row_count',
            'error_count',
            'uploaded_by_email',
            'created_at',
            'completed_at',
            'rows',
        ]
        read_only_fields = [
            'id', 'status', 'row_count', 'error_count',
            'uploaded_by_email', 'created_at', 'completed_at', 'rows',
        ]


class IngestionJobListSerializer(serializers.ModelSerializer):
    """
    Lightweight version for list view — excludes rows.
    Loading all rows on a list endpoint would be extremely slow.
    """
    uploaded_by_email = serializers.EmailField(source='uploaded_by.email', read_only=True)

    class Meta:
        model = IngestionJob
        fields = [
            'id',
            'source_type',
            'status',
            'raw_filename',
            'row_count',
            'error_count',
            'uploaded_by_email',
            'created_at',
            'completed_at',
        ]
        read_only_fields = fields


class IngestionUploadSerializer(serializers.Serializer):
    """
    Validates the incoming upload request.
    source_type tells us which parser to route to.
    """
    file = serializers.FileField()
    source_type = serializers.ChoiceField(choices=['sap', 'utility', 'travel'])

    def validate_file(self, value):
        # 50MB hard limit
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                "File too large. Maximum size is 50MB."
            )

        # Loose extension check — real validation happens in the parser
        allowed_extensions = ['.csv', '.txt', '.json', '.xlsx']
        name = value.name.lower()
        if not any(name.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
            )

        return value