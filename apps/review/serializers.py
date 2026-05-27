from rest_framework import serializers
from apps.review.models import ReviewAction
class ReviewActionSerializer(serializers.ModelSerializer):
    analyst_email = serializers.EmailField(
        source='analyst.email',
        read_only=True
    )
    class Meta:
        model = ReviewAction
        fields = [
            'id',
            'emission',
            'analyst_email',
            'action',
            'note',
            'previous_value',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'analyst_email',
            'previous_value',
            'created_at',
        ]
class BulkReviewSerializer(serializers.Serializer):
    emission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        min_length=1,
        max_length=500,
    )
    action = serializers.ChoiceField(
        choices=[
            'approve',
            'reject',
            'flag',
            'lock',
        ]
    )
    note = serializers.CharField(
        required=False,
        allow_blank=True,
        default=''
    )
    def validate_emission_ids(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError(
                "Duplicate emission IDs detected."
            )
        return value