from apps.ingestion.models import IngestionJob, IngestionRow
from apps.ingestion.parsers import sap_parser, utility_parser, travel_parser

PARSER_MAP = {
    'sap':     sap_parser,
    'utility': utility_parser,
    'travel':  travel_parser,
}


def handle_upload(job: IngestionJob) -> None:
    """
    Reads the uploaded file, routes to the correct parser,
    and writes one IngestionRow per parsed row.
    Updates job status and counts when done.
    """
    job.status = 'processing'
    job.save()

    parser = PARSER_MAP.get(job.source_type)
    if not parser:
        job.status = 'failed'
        job.save()
        raise ValueError(f"No parser registered for source_type '{job.source_type}'")

    try:
        file_content = job.file.read()
        parsed_rows = parser.parse(file_content)
    except Exception as e:
        job.status = 'failed'
        job.save()
        raise

    error_count = 0

    for i, row_data in enumerate(parsed_rows):
        warnings = row_data.pop('parse_warnings', [])
        has_error = any('error' in w.lower() for w in warnings)

        status = 'ok'
        error_message = ''
        if warnings:
            status = 'error' if has_error else 'warning'
            error_message = '; '.join(warnings)

        IngestionRow.objects.create(
            job=job,
            row_index=i,
            raw_data=row_data,       # full parsed dict stored as raw
            parsed_data=row_data,    # same at this stage; normalization updates later
            status=status,
            error_message=error_message,
        )

        if has_error:
            error_count += 1

    from django.utils import timezone
    job.row_count = len(parsed_rows)
    job.error_count = error_count
    job.status = 'done'
    job.completed_at = timezone.now()
    job.save()