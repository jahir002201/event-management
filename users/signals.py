from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()
@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if created:
        token = default_token_generator.make_token(instance)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
        subject = "Activate your account"
        message = f"Hi {instance.username}, please click the link to activate your account: {activation_url}"
        recipient_list = [instance.email]
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
            print(f"Activation email sent to {instance.email}")
        except Exception as e:
            print(f"Failed to send activation email to {instance.email}: {str(e)}")