from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Website, WebsiteKnowledgebase, EmailTemplate
from .forms import EmailTemplateForm
from django.contrib import messages
import pytz
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import datetime
import json

def branding_settings_view(request):
    website_instance, created = Website.objects.get_or_create(pk=1, defaults={
        'name': 'Support Center',
        'code': 'help',
        'theme_color': '#7e91f0',
        'is_active': True,
        'timezone': 'UTC',
        'timeformat': '24h',
    })

    knowledgebase_instance, created_kb = WebsiteKnowledgebase.objects.get_or_create(website=website_instance, defaults={
        'site_description': 'Hi! how can i help you.',
        'status': 'active',
        'ticket_create_option': 'public',
        'is_active': True,
    })

    if request.method == 'POST':
        # General Tab
        website_instance.name = request.POST.get('name', website_instance.name)
        website_instance.is_active = request.POST.get('is_active') == 'on'
        if 'logo' in request.FILES:
            logo_file = request.FILES['logo']
            fs = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, 'website_logos'))
            filename = fs.save(logo_file.name, logo_file)
            website_instance.logo = os.path.join('website_logos', filename)
        
        # Site Description (Tag Line)
        knowledgebase_instance.site_description = request.POST.get('site_description', knowledgebase_instance.site_description)

        # Time Tab
        website_instance.timezone = request.POST.get('timezone', website_instance.timezone)
        website_instance.timeformat = request.POST.get('timeformat', website_instance.timeformat)

        # SEO Tab
        knowledgebase_instance.meta_description = request.POST.get('meta_description', knowledgebase_instance.meta_description)
        knowledgebase_instance.meta_keywords = request.POST.get('meta_keywords', knowledgebase_instance.meta_keywords)

        # Links Tab
        header_links = []
        header_link_titles = request.POST.getlist('header_link_title[]')
        header_link_urls = request.POST.getlist('header_link_url[]')
        for i in range(len(header_link_titles)):
            if header_link_titles[i] and header_link_urls[i]:
                header_links.append({'title': header_link_titles[i], 'url': header_link_urls[i]})
        knowledgebase_instance.header_links = header_links

        footer_links = []
        footer_link_titles = request.POST.getlist('footer_link_title[]')
        footer_link_urls = request.POST.getlist('footer_link_url[]')
        for i in range(len(footer_link_titles)):
            if footer_link_titles[i] and footer_link_urls[i]:
                footer_links.append({'title': footer_link_titles[i], 'url': footer_link_urls[i]})
        knowledgebase_instance.footer_links = footer_links

        # Advanced Tab
        knowledgebase_instance.custom_css = request.POST.get('custom_css', knowledgebase_instance.custom_css)
        knowledgebase_instance.script = request.POST.get('script', knowledgebase_instance.script)

        # Broadcast Tab
        knowledgebase_instance.broadcast_message = request.POST.get('broadcast_message', knowledgebase_instance.broadcast_message)
        
        broadcast_from_date_str = request.POST.get('broadcast_from_date')
        if broadcast_from_date_str:
            knowledgebase_instance.broadcast_from_date = datetime.fromisoformat(broadcast_from_date_str)
        else:
            knowledgebase_instance.broadcast_from_date = None

        broadcast_to_date_str = request.POST.get('broadcast_to_date')
        if broadcast_to_date_str:
            knowledgebase_instance.broadcast_to_date = datetime.fromisoformat(broadcast_to_date_str)
        else:
            knowledgebase_instance.broadcast_to_date = None

        knowledgebase_instance.broadcast_status = request.POST.get('broadcast_status') == 'on'

        website_instance.save()
        knowledgebase_instance.save()

        messages.success(request, 'Branding settings updated successfully!')
        return redirect(reverse('branding_settings'))

    all_timezones = pytz.all_timezones

    context = {
        'website': website_instance,
        'knowledgebase': knowledgebase_instance,
        'timezones': all_timezones,
    }
    return render(request, 'settings/branding_settings.html', context)

def spam_settings_view(request):
    website_instance, created = Website.objects.get_or_create(pk=1, defaults={
        'name': 'Support Center',
        'code': 'help',
        'theme_color': '#7e91f0',
        'is_active': True,
        'timezone': 'UTC',
        'timeformat': '24h',
    })

    knowledgebase_instance, created_kb = WebsiteKnowledgebase.objects.get_or_create(website=website_instance, defaults={
        'site_description': 'Hi! how can i help you.',
        'status': 'active',
        'ticket_create_option': 'public',
        'is_active': True,
    })

    if request.method == 'POST':
        # Convert comma-separated string to list for JSONField
        black_list_str = request.POST.get('black_list', '')
        knowledgebase_instance.black_list = [item.strip() for item in black_list_str.split(',') if item.strip()]

        white_list_str = request.POST.get('white_list', '')
        knowledgebase_instance.white_list = [item.strip() for item in white_list_str.split(',') if item.strip()]

        knowledgebase_instance.save()
        messages.success(request, 'Spam settings updated successfully!')
        return redirect(reverse('spam_settings'))

    # Convert list from JSONField back to comma-separated string for display
    black_list_display = ', '.join(knowledgebase_instance.black_list) if knowledgebase_instance.black_list else ''
    white_list_display = ', '.join(knowledgebase_instance.white_list) if knowledgebase_instance.white_list else ''

    context = {
        'knowledgebase': knowledgebase_instance,
        'black_list_display': black_list_display,
        'white_list_display': white_list_display,
    }
    return render(request, 'settings/spam_settings.html', context)

def email_template_list(request):
    templates = EmailTemplate.objects.all().order_by('name')
    context = {
        'templates': templates
    }
    return render(request, 'settings/email_template_list.html', context)

def email_template_create(request):
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email template created successfully!')
            return redirect(reverse('email_template_list'))
    else:
        form = EmailTemplateForm()
    context = {
        'form': form,
        'view': 'Create Email Template'
    }
    return render(request, 'settings/email_template_form.html', context)

def email_template_edit(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    if request.method == 'POST':
        form = EmailTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email template updated successfully!')
            return redirect(reverse('email_template_list'))
    else:
        form = EmailTemplateForm(instance=template)
    context = {
        'form': form,
        'view': 'Edit Email Template'
    }
    return render(request, 'settings/email_template_form.html', context)

def email_template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    template.delete()
    messages.success(request, 'Email template deleted successfully!')
    return redirect(reverse('email_template_list'))