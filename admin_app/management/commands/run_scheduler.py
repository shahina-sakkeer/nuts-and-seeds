from django.core.management.base import BaseCommand
from admin_app.scheduler import start_scheduler
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Starts the APScheduler for cleaning up expired offers."

    def handle(self, *args, **options):
        logger.info("starting Offer cleanup scheduler...")
        try:
            start_scheduler()

        except KeyboardInterrupt:
            logger.info("scheduler stopped manually.")
            
        except Exception as e:
            logger.error(f"scheduler crashed: {e}", exc_info=True)
