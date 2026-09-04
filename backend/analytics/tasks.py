"""
Celery tasks for the analytics app.
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='analytics.tasks.process_financial_analysis')
def process_financial_analysis(self, task_id, data_set_id):
    """Run async financial analysis for an uploaded dataset."""
    from django.utils import timezone

    from analytics.models import AnalysisTask, FinancialDataSet
    from analytics.services.report_generator import FinancialReportGenerator

    try:
        task = AnalysisTask.objects.select_related('upload').get(task_id=task_id)
        data_set = FinancialDataSet.objects.select_related('upload').get(id=data_set_id)

        task.status = 'processing'
        task.progress = 10
        task.save(update_fields=['status', 'progress'])

        data = {
            'dashboard': data_set.dashboard_data or {},
            'qc_dashboard': data_set.qc_dashboard_data or {},
            'income_risk': data_set.income_risk_data or {},
            'dupont': data_set.dupont_data or {},
        }
        upload_info = {
            'upload_id': data_set.upload_id,
            'filename': getattr(data_set.upload, 'original_filename', ''),
            'task_id': task_id,
        }

        task.progress = 40
        task.save(update_fields=['progress'])

        report = FinancialReportGenerator().generate_complete_report(
            data=data,
            upload_info=upload_info,
        )

        task.result_data = report
        task.status = 'completed'
        task.progress = 100
        task.completed_at = timezone.now()
        task.error_message = ''
        task.save(
            update_fields=['progress', 'result_data', 'status', 'completed_at', 'error_message']
        )

        upload = task.upload
        upload.status = 'completed'
        upload.processed_at = timezone.now()
        upload.error_message = ''
        upload.save(update_fields=['status', 'processed_at', 'error_message'])

        return {'status': 'completed', 'task_id': task_id, 'data_set_id': data_set_id}

    except Exception as exc:
        logger.exception('process_financial_analysis failed for task %s: %s', task_id, exc)
        try:
            task = AnalysisTask.objects.select_related('upload').get(task_id=task_id)
            task.status = 'failed'
            task.error_message = str(exc)
            task.completed_at = timezone.now()
            task.save(update_fields=['status', 'error_message', 'completed_at'])
            upload = task.upload
            upload.status = 'failed'
            upload.error_message = str(exc)
            upload.save(update_fields=['status', 'error_message'])
        except Exception:
            logger.exception('Failed to persist error state for analysis task %s', task_id)
        return {'status': 'error', 'message': str(exc), 'task_id': task_id}


@shared_task(bind=True, name='analytics.tasks.cleanup_old_data_task')
def cleanup_old_data_task(self, user_id=None):
    """
    Periodic task to clean up old reports and uploads.
    
    This task runs on a schedule defined in celery.py and can also
    be called manually with a specific user_id.
    
    Args:
        user_id: Optional user ID to clean up. If None, processes all users.
    
    Returns:
        dict: Cleanup results
    """
    try:
        from django.contrib.auth.models import User
        from analytics.services.cleanup_service import cleanup_all_old_data
        
        user = None
        if user_id:
            try:
                user = User.objects.get(id=user_id)
                logger.info(f"Running cleanup for user: {user.username}")
            except User.DoesNotExist:
                logger.error(f"User with id {user_id} not found")
                return {'status': 'error', 'message': 'User not found'}
        else:
            logger.info("Running global cleanup for all users")
        
        # Run cleanup
        result = cleanup_all_old_data(user=user, dry_run=False)
        
        # Log results
        logger.info(
            f"Cleanup completed: "
            f"Reports deleted: {result['reports_deleted']}, "
            f"Uploads deleted: {result['uploads_deleted']}, "
            f"Total: {result['total_deleted']}"
        )
        
        return {
            'status': 'success',
            'total_deleted': result['total_deleted'],
            'reports_deleted': result['reports_deleted'],
            'uploads_deleted': result['uploads_deleted']
        }
    
    except Exception as e:
        logger.exception(f"Error in cleanup_old_data_task: {str(e)}")
        return {
            'status': 'error',
            'message': str(e)
        }
