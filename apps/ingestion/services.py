from apps.audit.models import AuditEvent
from apps.ingestion.models import IngestionJob
from apps.ingestion.upload_handlers import handle_upload
from apps.normalization.services import normalize_row
def ingest_and_normalize(job: IngestionJob) -> None:
    job.status = 'processing'
    job.save(update_fields=['status'])
    handle_upload(job)
    rows = job.rows.filter(
        status__in=['ok', 'warning']
    )
    normalized_count = 0
    failed_count = 0
    for row in rows:
        try:

            result = normalize_row(row)

            if result is not None:
                normalized_count += 1

            else:
                failed_count += 1

        except Exception as e:

            row.status = 'error'
            row.error_message = str(e)
            row.save(
                update_fields=[
                    'status',
                    'error_message',
                ]
            )

            failed_count += 1
    if failed_count > 0:

        job.status = 'partial'

    else:

        job.status = 'done'

    job.error_count = failed_count

    job.save(
        update_fields=[
            'status',
            'error_count',
        ]
    )
    AuditEvent.objects.create(
        organisation=job.organisation,
        actor=job.uploaded_by,
        content_object=job,
        verb='ingested',
        detail={
            'source_type': job.source_type,
            'raw_filename': job.raw_filename,
            'total_rows': job.row_count,
            'normalized': normalized_count,
            'failed': failed_count,
        }
    )