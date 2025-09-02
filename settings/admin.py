from django.contrib import admin
from .models import Website, WebsiteKnowledgebase, EmailTemplate

admin.site.register(Website)
admin.site.register(WebsiteKnowledgebase)
admin.site.register(EmailTemplate)
