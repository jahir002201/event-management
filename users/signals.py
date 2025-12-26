from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    if not created:
        return

    print("USER SIGNAL FIRED")
    token = default_token_generator.make_token(instance)
    activation_url = f"{settings.FRONTEND_URL}/users/activate/{instance.id}/{token}/"
    subject = "Activate your account"
    message = f"{instance.username}, please click the link to activate your account: {activation_url}"
    
    try:
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email], fail_silently=False)
        print(f"Activation email sent to {instance.email}")
    except Exception as e:
        print(f"Failed to send activation email to {instance.email}: {e}")