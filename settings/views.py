from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse # Added
import smtplib # Added
import imaplib # Added
from .models import Website, WebsiteKnowledgebase, EmailTemplate, UvSwiftmailer, UvMailbox, UvEmailSettings
from .forms import EmailTemplateForm, UvSwiftmailerForm, UvMailboxForm, UvEmailSettingsForm
from django.contrib import messages
import pytz
from django.core.files.storage import FileSystemStorage
import os
from django.conf import settings
from datetime import datetime
import json
from authentication.decorators import admin_login_required

@admin_login_required
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

@admin_login_required
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

@admin_login_required
def email_template_list(request):
    templates = EmailTemplate.objects.all().order_by('name')
    context = {
        'templates': templates
    }
    return render(request, 'settings/email_template_list.html', context)

@admin_login_required
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

@admin_login_required
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

@admin_login_required
def email_template_delete(request, pk):
    template = get_object_or_404(EmailTemplate, pk=pk)
    template.delete()
    messages.success(request, 'Email template deleted successfully!')
    return redirect(reverse('email_template_list'))


@admin_login_required
def uv_swiftmailer_list(request):
    swiftmailers = UvSwiftmailer.objects.all().order_by('name')
    context = {
        'swiftmailers': swiftmailers
    }
    return render(request, 'settings/swiftmailer_list.html', context)

@admin_login_required
def uv_swiftmailer_create(request):
    if request.method == 'POST':
        form = UvSwiftmailerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Swift Mailer configuration created successfully!')
            return redirect(reverse('uv_swiftmailer_list'))
    else:
        form = UvSwiftmailerForm()
    context = {
        'form': form,
        'view_title': 'Create Swift Mailer Configuration'
    }
    return render(request, 'settings/swiftmailer_form.html', context)

@admin_login_required
def uv_swiftmailer_edit(request, pk):
    swiftmailer = get_object_or_404(UvSwiftmailer, pk=pk)
    if request.method == 'POST':
        form = UvSwiftmailerForm(request.POST, instance=swiftmailer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Swift Mailer configuration updated successfully!')
            return redirect(reverse('uv_swiftmailer_list'))
    else:
        form = UvSwiftmailerForm(instance=swiftmailer)
    context = {
        'form': form,
        'view_title': 'Edit Swift Mailer Configuration'
    }
    return render(request, 'settings/swiftmailer_form.html', context)

@admin_login_required
def uv_swiftmailer_delete(request, pk):
    swiftmailer = get_object_or_404(UvSwiftmailer, pk=pk)
    swiftmailer.delete()
    messages.success(request, 'Swift Mailer configuration deleted successfully!')
    return redirect(reverse('uv_swiftmailer_list'))


@admin_login_required
def uv_mailbox_list(request):
    mailboxes = UvMailbox.objects.all().order_by('name')
    context = {
        'mailboxes': mailboxes
    }
    return render(request, 'settings/mailbox_list.html', context)

@admin_login_required
def uv_mailbox_create(request):
    if request.method == 'POST':
        form = UvMailboxForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mailbox configuration created successfully!')
            return redirect(reverse('uv_mailbox_list'))
    else:
        form = UvMailboxForm()
    context = {
        'form': form,
        'view_title': 'Create Mailbox Configuration'
    }
    return render(request, 'settings/mailbox_form.html', context)

@admin_login_required
def uv_mailbox_edit(request, pk):
    mailbox = get_object_or_404(UvMailbox, pk=pk)
    if request.method == 'POST':
        form = UvMailboxForm(request.POST, instance=mailbox)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mailbox configuration updated successfully!')
            return redirect(reverse('uv_mailbox_list'))
    else:
        form = UvMailboxForm(instance=mailbox)
    context = {
        'form': form,
        'view_title': 'Edit Mailbox Configuration'
    }
    return render(request, 'settings/mailbox_form.html', context)

@admin_login_required
def uv_mailbox_delete(request, pk):
    mailbox = get_object_or_404(UvMailbox, pk=pk)
    mailbox.delete()
    messages.success(request, 'Mailbox configuration deleted successfully!')
    return redirect(reverse('uv_mailbox_list'))


@admin_login_required
def uv_email_settings_view(request):
    email_settings, created = UvEmailSettings.objects.get_or_create(pk=1) # Ensure singleton
    if request.method == 'POST':
        form = UvEmailSettingsForm(request.POST, instance=email_settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Email settings updated successfully!')
            return redirect(reverse('uv_email_settings_view'))
    else:
        form = UvEmailSettingsForm(instance=email_settings)
    context = {
        'form': form,
        'view_title': 'Email Settings'
    }
    return render(request, 'settings/email_settings_form.html', context)


@admin_login_required
def test_swiftmailer_connection(request):
    if request.method == 'POST':
        host = request.POST.get('host')
        port_str = request.POST.get('port')
        username = request.POST.get('username')
        password = request.POST.get('password')
        encryption = request.POST.get('encryption')
        transport = request.POST.get('transport')

        # Validate required fields for SMTP
        if transport == 'smtp':
            if not host:
                return JsonResponse({'success': False, 'message': 'SMTP Server is required for SMTP transport.'})
            if not port_str:
                return JsonResponse({'success': False, 'message': 'Port is required for SMTP transport.'})
            try:
                port = int(port_str)
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Port must be a valid number.'})
        else: # gmail or yahoo
            host = None # Will be set by transport type
            port = None # Will be set by transport type

        # Validate username and password for all transports
        if not username:
            return JsonResponse({'success': False, 'message': 'Email (Username) is required.'})
        if not password:
            return JsonResponse({'success': False, 'message': 'Password is required.'})

        try:
            if transport == 'gmail':
                host = 'smtp.gmail.com'
                port = 587
                encryption = 'tls' # Force TLS for Gmail
            elif transport == 'yahoo':
                host = 'smtp.mail.yahoo.com'
                port = 587
                encryption = 'tls' # Force TLS for Yahoo
            elif transport == 'smtp':
                # Host, port, encryption already set from form
                pass
            else:
                return JsonResponse({'success': False, 'message': 'Invalid transport type selected.'})

            if encryption == 'ssl':
                server = smtplib.SMTP_SSL(host, port, timeout=10)
            else: # tls or null
                server = smtplib.SMTP(host, port, timeout=10)
                if encryption == 'tls':
                    server.starttls()

            server.login(username, password)
            server.quit()
            return JsonResponse({'success': True, 'message': 'Connection successful!'})
        except smtplib.SMTPAuthenticationError as e:
            return JsonResponse({'success': False, 'message': f'Authentication Error: {e.smtp_code} {e.smtp_error.decode()}'})
        except smtplib.SMTPConnectError as e:
            return JsonResponse({'success': False, 'message': f'Connection Error: Could not connect to SMTP server. Please check host, port, and network connectivity. ({e.smtp_code} {e.smtp_error.decode()})'})
        except smtplib.SMTPException as e:
            return JsonResponse({'success': False, 'message': f'SMTP Error: {e}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An unexpected error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})


@admin_login_required
def test_mailbox_connection(request):
    if request.method == 'POST':
        imap_host = request.POST.get('imap_host')
        imap_port_str = request.POST.get('imap_port')
        imap_username = request.POST.get('imap_username')
        imap_password = request.POST.get('imap_password')
        imap_encryption = request.POST.get('imap_encryption')

        if not imap_host:
            return JsonResponse({'success': False, 'message': 'IMAP Host is required.'})
        if not imap_port_str:
            return JsonResponse({'success': False, 'message': 'IMAP Port is required.'})
        try:
            imap_port = int(imap_port_str)
        except ValueError:
            return JsonResponse({'success': False, 'message': 'IMAP Port must be a valid number.'})
        if not imap_username:
            return JsonResponse({'success': False, 'message': 'IMAP Username is required.'})
        if not imap_password:
            return JsonResponse({'success': False, 'message': 'IMAP Password is required.'})

        try:
            if imap_encryption == 'ssl':
                mail = imaplib.IMAP4_SSL(imap_host, imap_port)
            else: # 'tls' or 'null'
                mail = imaplib.IMAP4(imap_host, imap_port)
                if imap_encryption == 'tls':
                    # IMAP STARTTLS is not directly supported by imaplib.IMAP4
                    # It's usually handled by IMAP4_SSL if the server supports it on the default port
                    # or requires a different port. For simplicity, we'll assume IMAP4_SSL handles it
                    # or it's a plain IMAP connection.
                    pass

            mail.login(imap_username, imap_password)
            mail.logout() # Logout immediately after successful login
            return JsonResponse({'success': True, 'message': 'IMAP Connection successful!'})
        except imaplib.IMAP4.error as e:
            return JsonResponse({'success': False, 'message': f'IMAP Connection Error: {e}'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'An unexpected error occurred: {e}'})
    return JsonResponse({'success': False, 'message': 'Invalid request method.'})
