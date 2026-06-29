"""
Celery tasks for the analytics app.
"""

from celery import shared_task
import logging

logger = logging.getLogger(__name__)


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
