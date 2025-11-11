from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.utils import timezone
from django.db import transaction, connection
from .models import CategoryOffer, ProductOffer
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#making expired category offer as false
def cleanup_category_offers():
    now=timezone.now()

    with transaction.atomic():
        expired=CategoryOffer.objects.filter(is_active=True,end_date__lt=now)
        count=expired.update(is_active=False)

    connection.close()

    if count:
        logger.info(f"Deactivated {count} expired category offers at {now}")
    else:
        logger.info(f"No expired Category offers found at {now}")


#making expired category offer as false
def cleanup_product_offers():
    now=timezone.now()

    with transaction.atomic():
        expired=ProductOffer.objects.filter(is_active=True,end_date__lt=now)
        count=expired.update(is_active=False)

    connection.close()

    if count:
        logger.info(f"Deactivated {count} expired product offers at {now}")
    else:
        logger.info(f"No expired product offers found at {now}")


def start_scheduler():
    scheduler=BlockingScheduler(timezone="Asia/Kolkata")

    scheduler.add_job(cleanup_category_offers,CronTrigger(hour=0, minute=0))
    scheduler.add_job(cleanup_product_offers,CronTrigger(hour=0, minute=0))

    cleanup_category_offers()
    cleanup_product_offers()

    logger.info("Offer cleanup scheduler started (runs daily at midnight)")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped gracefully.")




