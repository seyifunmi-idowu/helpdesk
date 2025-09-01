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

    def __str__(self):
        return self.name