from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings
from .models import UvEmailSettings, UvSwiftmailer


class UvSwiftmailerEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connection = None # Ensure connection is not established prematurely by parent

    def open(self):
        if self.connection:
            return True

        try:
            email_settings = UvEmailSettings.objects.first()
            if not email_settings or not email_settings.active_swiftmailer:
                print("UvSwiftmailerEmailBackend: No active swiftmailer configured. Falling back to default Django settings.")
                self.host = settings.EMAIL_HOST
                self.port = settings.EMAIL_PORT
                self.username = settings.EMAIL_HOST_USER
                self.password = settings.EMAIL_HOST_PASSWORD
                self.use_tls = settings.EMAIL_USE_TLS
                self.use_ssl = settings.EMAIL_USE_SSL
                self.timeout = settings.EMAIL_TIMEOUT
                self.ssl_keyfile = settings.EMAIL_SSL_KEYFILE
                self.ssl_certfile = settings.EMAIL_SSL_CERTFILE
            else:
                swiftmailer = email_settings.active_swiftmailer
                print(f"UvSwiftmailerEmailBackend: Using swiftmailer '{swiftmailer.name}' (ID: {swiftmailer.pk})")

                # Set common SMTP settings
                self.username = swiftmailer.username
                self.password = swiftmailer.password
                self.timeout = 10 # Default timeout

                # Handle different transport types
                if swiftmailer.transport == 'gmail':
                    self.host = 'smtp.gmail.com'
                    self.port = 587
                    self.use_tls = True
                    self.use_ssl = False
                elif swiftmailer.transport == 'yahoo':
                    self.host = 'smtp.mail.yahoo.com'
                    self.port = 587
                    self.use_tls = True
                    self.use_ssl = False
                elif swiftmailer.transport == 'smtp':
                    self.host = swiftmailer.host
                    self.port = swiftmailer.port

                    if swiftmailer.encryption == 'tls':
                        self.use_tls = True
                        self.use_ssl = False
                    elif swiftmailer.encryption == 'ssl':
                        self.use_tls = False
                        self.use_ssl = True
                    else: # 'null' or no encryption
                        self.use_tls = False
                        self.use_ssl = False
                else:
                    print(f"UvSwiftmailerEmailBackend: Unknown transport type '{swiftmailer.transport}'. Falling back to default Django settings.")
                    # Fallback to default Django settings if transport type is unknown
                    self.host = settings.EMAIL_HOST
                    self.port = settings.EMAIL_PORT
                    self.username = settings.EMAIL_HOST_USER
                    self.password = settings.EMAIL_HOST_PASSWORD
                    self.use_tls = settings.EMAIL_USE_TLS
                    self.use_ssl = settings.EMAIL_USE_SSL

            print(f"UvSwiftmailerEmailBackend: Attempting connection to {self.host}:{self.port} (TLS: {self.use_tls}, SSL: {self.use_ssl}) with user {self.username}")
            print(f"UvSwiftmailerEmailBackend: self.fail_silently is {self.fail_silently}")
            # Establish connection using the determined settings
            # super().open() will set self.connection internally if successful
            super().open()
            print(f"UvSwiftmailerEmailBackend: super().open() completed. self.connection is now: {self.connection}")
            if self.connection:
                print("UvSwiftmailerEmailBackend: Connection established successfully.")
                return True # Return True to indicate successful opening
            else:
                print("UvSwiftmailerEmailBackend: Connection failed, but no exception was raised by super().open().")
                # If super().open() returns False and fail_silently is False,
                # it should have raised an exception. Explicitly raise one here
                # to ensure the outer except block is hit.
                if not self.fail_silently:
                    raise smtplib.SMTPException("Failed to connect to SMTP server.")
                return None

        except Exception as e:
            print(f"UvSwiftmailerEmailBackend: CRITICAL ERROR - Failed to open email connection: {e}")
            if not self.fail_silently:
                raise
            return None
