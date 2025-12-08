from django.db.models.signals import post_save
from django.dispatch import receiver
from user_app.models import CustomUser
from user_app.models import generate_referralID


@receiver(post_save,sender=CustomUser)
def referralcode_for_googe_signup(sender,instance,created,**kwargs):
    if created:
        if not instance.referralID:
            instance.referralID=generate_referralID()
            instance.save(update_fields=["referralID"])

