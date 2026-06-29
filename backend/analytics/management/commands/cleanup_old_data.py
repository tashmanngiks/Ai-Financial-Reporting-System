"""
Management command to clean up old data based on retention settings.

Usage:
    python manage.py cleanup_old_data                    # Global cleanup for all users
    python manage.py cleanup_old_data --user <username>  # Cleanup for specific user
    python manage.py cleanup_old_data --dry-run          # Preview what would be deleted
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from analytics.services.cleanup_service import cleanup_all_old_data


class Command(BaseCommand):
    help = "Clean up old reports and uploads based on user retention settings"

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username to clean up data for. If not provided, processes all users.'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be deleted without actually deleting'
        )

    def handle(self, *args, **options):
        username = options.get('user')
        dry_run = options.get('dry_run', False)
        
        user = None
        if username:
            try:
                user = User.objects.get(username=username)
                self.stdout.write(f"Cleaning up data for user: {username}")
            except User.DoesNotExist:
                raise CommandError(f"User '{username}' not found")
        else:
            self.stdout.write("Running global cleanup for all users")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No data will be deleted"))
        
        # Run cleanup
        result = cleanup_all_old_data(user=user, dry_run=dry_run)
        
        # Display results
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("CLEANUP RESULTS")
        self.stdout.write("=" * 60)
        
        self.stdout.write(f"Reports deleted: {result['reports_deleted']}")
        if result['reports_deleted'] > 0:
            self.stdout.write(f"  Details: {result['reports'].get('retention_days')} days retention")
            self.stdout.write(f"  Cutoff:  {result['reports'].get('cutoff_date')}")
        
        self.stdout.write(f"Uploads deleted: {result['uploads_deleted']}")
        if result['uploads_deleted'] > 0:
            self.stdout.write(f"  Details: {result['uploads'].get('retention_days')} days retention")
            self.stdout.write(f"  Cutoff:  {result['uploads'].get('cutoff_date')}")
        
        self.stdout.write(f"\nTotal deleted: {result['total_deleted']}")
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\n⚠️  DRY RUN - No actual deletions were made"))
        else:
            if result['total_deleted'] > 0:
                self.stdout.write(self.style.SUCCESS(f"\n✓ Successfully deleted {result['total_deleted']} items"))
            else:
                self.stdout.write("No items to delete")
        
        self.stdout.write("=" * 60 + "\n")
