"""Signal handlers for the Home app."""

from django.dispatch import receiver

from allauth.account.signals import email_confirmed

from .forms import CONFIRMED_EMAIL_SESSION_KEY


@receiver(email_confirmed)
def stash_confirmed_email(request, email_address, **kwargs):
    if request is None or not hasattr(request, "session"):
        return
    request.session[CONFIRMED_EMAIL_SESSION_KEY] = email_address.email