"""Email backend compatibility helpers."""

import ssl

from django.core.mail.backends.smtp import EmailBackend as DjangoSMTPEmailBackend
from django.core.mail.utils import DNS_NAME


class EmailBackend(DjangoSMTPEmailBackend):
    """SMTP backend compatible with newer Python versions.

    Django 3.2 passes ``keyfile`` and ``certfile`` to ``starttls``. Python 3.12
    removed those arguments, so we override the TLS handshake to use the modern
    ``context`` parameter instead.
    """

    def _get_ssl_context(self):
        context = ssl.create_default_context()
        if self.ssl_certfile:
            context.load_cert_chain(
                certfile=self.ssl_certfile,
                keyfile=self.ssl_keyfile,
            )
        return context

    def open(self):
        if self.connection:
            return False

        connection_params = {
            "host": self.host,
            "port": self.port,
            "local_hostname": DNS_NAME.get_fqdn(),
            "timeout": self.timeout,
        }

        try:
            if self.use_ssl:
                self.connection = self.connection_class(
                    **connection_params,
                    context=self._get_ssl_context(),
                )
            else:
                self.connection = self.connection_class(**connection_params)

            self.connection.ehlo()

            if self.use_tls:
                self.connection.starttls(context=self._get_ssl_context())
                self.connection.ehlo()

            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except OSError:
            if not self.fail_silently:
                raise
            return False
