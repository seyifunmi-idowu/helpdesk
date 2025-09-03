from django.db import models
from django.utils import timezone

class Website(models.Model):
    name = models.CharField(max_length=191)
    code = models.CharField(max_length=191, unique=True)
    logo = models.CharField(max_length=191, blank=True, null=True)
    theme_color = models.CharField(max_length=191, blank=True, null=True)
    favicon = models.CharField(max_length=191, blank=True, null=True)
    timezone = models.CharField(max_length=191, default='UTC')
    timeformat = models.CharField(max_length=20, default='24h')
    business_hour = models.JSONField(blank=True, null=True)
    business_hour_status = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'uv_website'

    def __str__(self):
        return self.name

class WebsiteKnowledgebase(models.Model):
    website = models.OneToOneField(Website, on_delete=models.CASCADE, related_name='knowledgebase_config')
    status = models.CharField(max_length=255, default='active')
    brand_color = models.CharField(max_length=255, blank=True, null=True)
    page_background_color = models.CharField(max_length=255, blank=True, null=True)
    header_background_color = models.CharField(max_length=255, blank=True, null=True)
    link_color = models.CharField(max_length=255, blank=True, null=True)
    article_text_color = models.CharField(max_length=255, blank=True, null=True)
    ticket_create_option = models.CharField(max_length=255, default='public')
    site_description = models.CharField(max_length=1000, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    homepage_content = models.CharField(max_length=255, blank=True, null=True)
    white_list = models.JSONField(blank=True, null=True)
    black_list = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    broadcast_message = models.TextField(blank=True, null=True)
    broadcast_from_date = models.DateTimeField(null=True, blank=True)
    broadcast_to_date = models.DateTimeField(null=True, blank=True)
    broadcast_status = models.BooleanField(default=False)
    disable_customer_login = models.BooleanField(default=False)
    script = models.TextField(blank=True, null=True)
    custom_css = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    header_links = models.JSONField(blank=True, null=True)
    footer_links = models.JSONField(blank=True, null=True)
    banner_background_color = models.CharField(max_length=255, blank=True, null=True)
    link_hover_color = models.CharField(max_length=255, blank=True, null=True)
    login_required_to_create = models.BooleanField(default=False)
    remove_customer_login_button = models.BooleanField(default=False)
    remove_branding_content = models.BooleanField(default=False)

    class Meta:
        db_table = 'uv_website_knowledgebase'

    def __str__(self):
        """String representation of the WebsiteKnowledgebase object."""
        return f"KB Config for {self.website.name}"

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255, unique=True)
    subject = models.CharField(max_length=255)
    body = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'uv_email_templates'
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"

    def __str__(self):
        return self.name


class UvSwiftmailer(models.Model):
    TRANSPORT_CHOICES = [
        ('smtp', 'SMTP'),
        ('gmail', 'Gmail'),
        ('yahoo', 'Yahoo'),
    ]
    ENCRYPTION_CHOICES = [
        ('ssl', 'SSL'),
        ('tls', 'TLS'),
        ('null', 'None'),
    ]

    name = models.CharField(max_length=191, verbose_name="Friendly Name")
    transport = models.CharField(max_length=10, choices=TRANSPORT_CHOICES, verbose_name="Transport Type")
    host = models.CharField(max_length=191, null=True, blank=True, verbose_name="SMTP Host")
    port = models.IntegerField(null=True, blank=True, verbose_name="SMTP Port")
    encryption = models.CharField(max_length=10, choices=ENCRYPTION_CHOICES, default='tls', verbose_name="Encryption Mode")
    username = models.CharField(max_length=191, verbose_name="Username")
    password = models.CharField(max_length=255, verbose_name="Password") # Storing as CharField, encryption handled at app level
    sender_address = models.CharField(max_length=191, verbose_name="Sender Address")

    class Meta:
        db_table = "uv_swiftmailer"
        verbose_name = "Swift Mailer Configuration"
        verbose_name_plural = "Swift Mailer Configurations"

    def __str__(self):
        return self.name


class UvMailbox(models.Model):
    IMAP_ENCRYPTION_CHOICES = [
        ('ssl', 'SSL'),
        ('tls', 'TLS'),
        ('null', 'None'),
    ]

    name = models.CharField(max_length=191, verbose_name="Mailbox Name")
    email = models.CharField(max_length=191, verbose_name="Email Address")
    is_enabled = models.BooleanField(default=True, verbose_name="Enable Mailbox")
    delete_after_fetch = models.BooleanField(default=False, verbose_name="Permanently delete from Inbox")
    imap_host = models.CharField(max_length=191, verbose_name="Incoming IMAP Server")
    imap_port = models.IntegerField(verbose_name="Incoming IMAP Port")
    imap_encryption = models.CharField(max_length=10, choices=IMAP_ENCRYPTION_CHOICES, default='ssl', verbose_name="IMAP Encryption")
    imap_username = models.CharField(max_length=191, verbose_name="IMAP Username")
    imap_password = models.CharField(max_length=255, verbose_name="IMAP Password") # Storing as CharField, encryption handled at app level
    outbound_transport = models.ForeignKey(UvSwiftmailer, on_delete=models.SET_NULL, null=True, blank=True, related_name='mailboxes', verbose_name="Outgoing Mail Transport")

    class Meta:
        db_table = "uv_mailbox"
        verbose_name = "Mailbox Configuration"
        verbose_name_plural = "Mailbox Configurations"

    def __str__(self):
        return self.name


class UvEmailSettings(models.Model):
    system_email = models.CharField(max_length=191, verbose_name="System Email ID")
    system_sender_name = models.CharField(max_length=191, verbose_name="System Sender Name")
    active_mailbox = models.OneToOneField(UvMailbox, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_settings', verbose_name="Active Mailbox for Incoming")
    active_swiftmailer = models.OneToOneField(UvSwiftmailer, on_delete=models.SET_NULL, null=True, blank=True, related_name='active_settings', verbose_name="Default Swift Mailer for Outgoing")

    class Meta:
        db_table = "uv_email_settings"
        verbose_name = "Email Setting"
        verbose_name_plural = "Email Settings"

    def __str__(self):
        return "Email Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance of UvEmailSettings exists
        if not self.pk and UvEmailSettings.objects.exists():
            raise Exception("There can be only one UvEmailSettings instance.")
        return super(UvEmailSettings, self).save(*args, **kwargs)
