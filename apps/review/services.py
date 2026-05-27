from django.db import transaction

from apps.audit.models import AuditEvent
from apps.emissions.models import NormalizedEmission
from apps.review.models import ReviewAction
from apps.users.models import User


class ReviewError(Exception):
    pass


def _assert_not_locked(emission: NormalizedEmission):

    if emission.status == 'locked':
        raise ReviewError(
            f"Emission {emission.id} is locked for audit "
            f"and cannot be changed."
        )


def _create_audit_event(
    emission: NormalizedEmission,
    analyst: User,
    verb: str,
    detail: dict | None = None,
):

    AuditEvent.objects.create(
        organisation=analyst.organisation,
        actor=analyst,
        content_object=emission,
        verb=verb,
        detail=detail or {},
    )


@transaction.atomic
def approve_emission(
    emission_id,
    analyst: User,
) -> ReviewAction:

    emission = (
        NormalizedEmission.objects
        .select_for_update()
        .get(
            id=emission_id,
            organisation=analyst.organisation,
        )
    )

    _assert_not_locked(emission)

    # Optional workflow guard
    if emission.status == 'rejected':
        raise ReviewError(
            f"Rejected emission {emission.id} "
            f"cannot be directly approved."
        )

    old_status = emission.status

    emission.status = 'approved'
    emission.save()

    review = ReviewAction.objects.create(
        emission=emission,
        analyst=analyst,
        action='approve',
    )

    _create_audit_event(
        emission=emission,
        analyst=analyst,
        verb='approved',
        detail={
            'old_status': old_status,
            'new_status': 'approved',
        }
    )

    return review


@transaction.atomic
def reject_emission(
    emission_id,
    analyst: User,
    note: str = '',
) -> ReviewAction:

    emission = (
        NormalizedEmission.objects
        .select_for_update()
        .get(
            id=emission_id,
            organisation=analyst.organisation,
        )
    )

    _assert_not_locked(emission)

    old_status = emission.status

    emission.status = 'rejected'
    emission.save()

    review = ReviewAction.objects.create(
        emission=emission,
        analyst=analyst,
        action='reject',
        note=note,
    )

    _create_audit_event(
        emission=emission,
        analyst=analyst,
        verb='rejected',
        detail={
            'old_status': old_status,
            'new_status': 'rejected',
            'note': note,
        }
    )

    return review


@transaction.atomic
def flag_emission(
    emission_id,
    analyst: User,
    note: str = '',
) -> ReviewAction:

    emission = (
        NormalizedEmission.objects
        .select_for_update()
        .get(
            id=emission_id,
            organisation=analyst.organisation,
        )
    )

    _assert_not_locked(emission)

    review = ReviewAction.objects.create(
        emission=emission,
        analyst=analyst,
        action='flag',
        note=note,
    )

    _create_audit_event(
        emission=emission,
        analyst=analyst,
        verb='flagged',
        detail={
            'note': note,
        }
    )

    return review


@transaction.atomic
def lock_all_approved(
    organisation,
    analyst: User,
) -> int:
    """
    Lock all currently approved emissions for audit submission.
    Returns number of rows locked.
    """

    qs = (
        NormalizedEmission.objects
        .select_for_update()
        .filter(
            organisation=organisation,
            status='approved',
        )
    )

    # Capture rows BEFORE update
    rows_to_lock = list(qs)

    count = len(rows_to_lock)

    qs.update(status='locked')

    for emission in rows_to_lock:

        ReviewAction.objects.create(
            emission=emission,
            analyst=analyst,
            action='lock',
        )

        _create_audit_event(
            emission=emission,
            analyst=analyst,
            verb='locked_for_audit',
        )

    return count


@transaction.atomic
def bulk_review(
    emission_ids: list,
    action: str,
    analyst: User,
    note: str = '',
) -> dict:
    """
    Bulk approve/reject/flag emissions.

    Returns:
    {
        success: int,
        failed: [
            { id, reason }
        ]
    }
    """

    ACTION_MAP = {
        'approve': approve_emission,
        'reject': reject_emission,
        'flag': flag_emission,
    }

    if action not in ACTION_MAP:
        raise ReviewError(
            f"Unsupported bulk action '{action}'"
        )

    fn = ACTION_MAP[action]

    success = 0
    failed = []

    for eid in emission_ids:

        try:

            if action == 'approve':
                fn(eid, analyst)

            else:
                fn(eid, analyst, note)

            success += 1

        except (
            NormalizedEmission.DoesNotExist,
            ReviewError,
        ) as e:

            failed.append({
                'id': str(eid),
                'reason': str(e),
            })

    return {
        'success': success,
        'failed': failed,
    }