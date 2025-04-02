from django.core.mail.backends.smtp import EmailBackend
import ssl
import certifi

class SSLFixEmailBackend(EmailBackend):
    def open(self):
        if self.connection:
            return False

        connection_class = self.connection_class
        context = ssl.create_default_context(cafile=certifi.where())

        try:
            self.connection = connection_class(
                self.host, self.port, timeout=self.timeout, context=context
            )
            if self.use_tls:
                self.connection.starttls(context=context)
            if self.username and self.password:
                self.connection.login(self.username, self.password)
            return True
        except Exception:
            if self.fail_silently:
                return False
            raise