"""Custom allauth forms for the Home app."""

from allauth.account.forms import LoginForm as AllauthLoginForm


CONFIRMED_EMAIL_SESSION_KEY = "fabric_focus_confirmed_email"


class LoginForm(AllauthLoginForm):
    """Prefill the login field from a recently confirmed email address."""

    def __init__(self, *args, **kwargs):
        request = kwargs.get("request")
        super().__init__(*args, **kwargs)

        if request is not None:
            confirmed_email = request.session.get(CONFIRMED_EMAIL_SESSION_KEY)
            if confirmed_email:
                self.fields["login"].initial = confirmed_email

    def login(self, request, redirect_url=None):
        response = super().login(request, redirect_url=redirect_url)
        request.session.pop(CONFIRMED_EMAIL_SESSION_KEY, None)
        return response