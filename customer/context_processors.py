import json
from settings.models import WebsiteKnowledgebase
from django.utils import timezone
from django.conf import settings

def layout_settings(request):
    context = {
        'site_description': "Hi! how can i help you.",
        'header_links': [],
        'footer_links': [],
        'broadcast_message': None,
        'meta_description': '',
        'meta_keywords': '',
        'custom_css': '',
        'script': '',
        'website_logo': None,
        'website_name': 'Customer Portal',
    }
    try:
        website_kb = WebsiteKnowledgebase.objects.filter(website__pk=1).first()
        if website_kb:
            # Links
            context['header_links'] = website_kb.header_links if website_kb.header_links else []
            context['footer_links'] = website_kb.footer_links if website_kb.footer_links else []
            context['site_description'] = website_kb.site_description if website_kb.site_description else context['site_description']

            # Broadcast
            if website_kb.broadcast_status:
                now = timezone.now()
                is_in_date_range = True
                if website_kb.broadcast_from_date and now < website_kb.broadcast_from_date:
                    is_in_date_range = False
                if website_kb.broadcast_to_date and now > website_kb.broadcast_to_date:
                    is_in_date_range = False
                if is_in_date_range:
                    context['broadcast_message'] = website_kb.broadcast_message
            
            # SEO and Custom Code
            context['meta_description'] = website_kb.meta_description
            context['meta_keywords'] = website_kb.meta_keywords
            context['custom_css'] = website_kb.custom_css
            context['script'] = website_kb.script

            # Website Name and Logo
            if website_kb.website:
                context['website_name'] = website_kb.website.name
                if website_kb.website.logo:
                    # Corrected: logo is a string, prepend MEDIA_URL
                    context['website_logo'] = settings.MEDIA_URL + website_kb.website.logo

    except WebsiteKnowledgebase.DoesNotExist:
        pass
    return context