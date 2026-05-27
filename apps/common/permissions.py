from rest_framework.permissions import (
    BasePermission,
    IsAuthenticated,
)
class IsTenantMember(IsAuthenticated):
    def _resolve_organisation(self, obj):
        if hasattr(obj, 'organisation'):
            return getattr(obj, 'organisation', None)
        if hasattr(obj, 'job'):
            return getattr(
                getattr(obj, 'job', None),
                'organisation',
                None
            )
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
    message = (
        "Only admins can perform this action."
    )

    def has_permission(self, request, view):

        return (
            request.user.is_authenticated
            and getattr(request.user, 'role', None)
            == 'admin'
        )