from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.conf import settings
from django.core.mail import send_mail
from events.models import Event

@receiver(m2m_changed, sender=Event.participants.through)
def send_rsvp_email(sender, instance, action, **kwargs):
    if action == 'post_add':
        for user in instance.participants.all():
            subject = "RSVP Confirmation"
            message = f"Hi {user.username}, you have RSVPed to the event: {instance.name}"
            recipient_list = [user.email]
            try:
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            except Exception as e:
                print(f"{user.email} Failed to send RSVP email: {str(e)}")