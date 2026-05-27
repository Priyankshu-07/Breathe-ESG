from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)


class IsTenantMember(IsAuthenticated):
    """
    User must:
    - be authenticated
    - belong to an organisation

    All tenant-scoped API views should inherit this permission.
    """

    def _resolve_organisation(self, obj):
        """
        Attempts to resolve organisation ownership for different
        object structures used across the platform.

        Supported:
        - obj.organisation
        - obj.job.organisation
        - obj.source_row.job.organisation
        """

        # Direct ownership
        if hasattr(obj, 'organisation'):
            return getattr(obj, 'organisation', None)

        # IngestionRow -> job -> organisation
        if hasattr(obj, 'job'):
            return getattr(
                getattr(obj, 'job', None),
                'organisation',
                None
            )

        # NormalizedEmission -> source_row -> job -> organisation
        if hasattr(obj, 'source_row'):
            return getattr(
                getattr(
                    getattr(obj, 'source_row', None),
                    'job',
                    None
                ),
                'organisation',
                None
            )

        return None

    def has_permission(self, request, view):

        return (
            super().has_permission(request, view)
            and getattr(
                request.user,
                'organisation',
                None
            ) is not None
        )

    def has_object_permission(self, request, view, obj):

        obj_org = self._resolve_organisation(obj)

        return (
            obj_org is not None
            and obj_org == request.user.organisation
        )


class IsAnalyst(BasePermission):
    """
    User must have:
    - analyst role
    OR
    - admin role

    Used for:
    - approve/reject/flag actions
    - review workflows
    """

    message = (
        "Only analysts and admins "
        "can perform review actions."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None)
            in ('analyst', 'admin')
        )


class IsAdmin(BasePermission):
    """
    User must have admin role.

    Used for:
    - tenant management
    - organisation-level operations
    - audit locking workflows
    """

    message = (
        "Only admins can perform this action."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None)
            == 'admin'
        )