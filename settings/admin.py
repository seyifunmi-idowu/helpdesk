from django.contrib import admin
from .models import Website, WebsiteKnowledgebase, EmailTemplate, UvSwiftmailer, UvMailbox, UvEmailSettings

admin.site.register(Website)
admin.site.register(WebsiteKnowledgebase)
admin.site.register(EmailTemplate)
admin.site.register(UvSwiftmailer)
admin.site.register(UvMailbox)
admin.site.register(UvEmailSettings)
