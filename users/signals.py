from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.dispatch import Signal, receiver

user_registered = Signal()

@receiver(user_registered)
def send_activation_email(sender, user, **kwargs):
    if not user.is_active:
        token = default_token_generator.make_token(user)
        activation_url = f"{settings.FRONTEND_URL}/users/activate/{user.id}/{token}/"
        subject = "Activate your account"
        message = f"Hi {user.username}, please click the link to activate your account: {activation_url}"

        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)
            print(f"Activation email sent to {user.email}")
        except Exception as e:
            print(f"Failed to send activation email to {user.email}: {e}")