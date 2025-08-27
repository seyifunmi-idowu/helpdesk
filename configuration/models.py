from django.db import models
from core.models import User, UserInstance # Assuming User and UserInstance models are in the core app

class EmailTemplates(models.Model):
    name = models.CharField(max_length=191)
    subject = models.CharField(max_length=191)
    message = models.TextField()
    templateType = models.CharField(max_length=255, null=True, blank=True)
    isPredefined = models.BooleanField(default=True)
    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Email Template"
        verbose_name_plural = "Email Templates"
        db_table = "uv_email_templates"

    def __str__(self):
        return self.name

class SavedFilters(models.Model):
    name = models.CharField(max_length=191)
    filtering = models.JSONField(null=True, blank=True)
    route = models.CharField(max_length=190, null=True, blank=True)
    dateAdded = models.DateTimeField(auto_now_add=True)
    dateUpdated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(UserInstance, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        verbose_name = "Saved Filter"
        verbose_name_plural = "Saved Filters"
        db_table = "uv_saved_filters"

    def __str__(self):
        return f"{self.name} by {self.user.user.email if self.user else 'N/A'}"

class Website(models.Model):
    name = models.CharField(max_length=191)
    code = models.CharField(max_length=191, unique=True)
    logo = models.CharField(max_length=191, null=True, blank=True)
    themeColor = models.CharField(max_length=191)
    favicon = models.CharField(max_length=191, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    isActive = models.BooleanField(null=True, blank=True, default=True)
    timezone = models.CharField(max_length=191, null=True, blank=True)
    timeformat = models.CharField(max_length=191, null=True, blank=True)
    businessHour = models.JSONField(null=True, blank=True)
    businessHourStatus = models.BooleanField(null=True, blank=True, default=True)

    class Meta:
        verbose_name = "Website"
        verbose_name_plural = "Websites"
        db_table = "uv_website"

    def __str__(self):
        return self.name

class Recaptcha(models.Model):
    siteKey = models.CharField(max_length=255, null=True, blank=True)
    secretKey = models.CharField(max_length=255, null=True, blank=True)
    isActive = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "reCAPTCHA Setting"
        verbose_name_plural = "reCAPTCHA Settings"
        db_table = "uv_recaptcha"

    def __str__(self):
        return f"reCAPTCHA ({ 'Active' if self.isActive else 'Inactive' })"

class MicrosoftIntegration(models.Model):
    # Placeholder for Microsoft integration settings
    name = models.CharField(max_length=100, unique=True)
    client_id = models.CharField(max_length=255, blank=True, null=True)
    client_secret = models.CharField(max_length=255, blank=True, null=True)
    tenant_id = models.CharField(max_length=255, blank=True, null=True)
    # Add other fields as needed for specific Microsoft integrations (e.g., Azure AD, Outlook)

    class Meta:
        verbose_name = "Microsoft Integration"
        verbose_name_plural = "Microsoft Integrations"
        db_table = "uv_microsoft_integration"

    def __str__(self):
        return self.name