from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail

@receiver(post_save, sender=User)
def send_acivation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
        subject = "Activate your account"
        message = f"{instance.username} Please click the link to activate your account: {activation_url}"
        recipient_list = [instance.email]
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
        except Exception as e:
            print(f"{instance.email} Failed to send activation email: {str(e)}")