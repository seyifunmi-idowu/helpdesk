from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import models
from authentication.decorators import customer_login_required
from knowledgebase.models import Folder, SolutionCategory, Article
from ticket.models import Ticket, TicketType, TicketPriority, TicketStatus
from authentication.models import User, UserInstance, SupportRole
from .forms import PublicTicketForm

def dashboard(request):
    folders = Folder.objects.all()
    context = {
        'folders': folders
    }
    return render(request, 'customer/dashboard.html', context)

def create_ticket_public(request):
    if request.method == 'POST':
        form = PublicTicketForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            ticket_type = form.cleaned_data['ticket_type']
            ticket_priority = form.cleaned_data['ticket_priority']

            # Check if user exists, if not, create a new one
            user, created = User.objects.get_or_create(email=email, defaults={'firstName': email, 'is_active': True})

            # Get the customer role
            customer_role, _ = SupportRole.objects.get_or_create(code='ROLE_CUSTOMER', defaults={'description': 'Customer'})

            # Create a user instance with the customer role
            user_instance, created_instance = UserInstance.objects.get_or_create(
                user=user,
                defaults={'supportRole': customer_role, 'source': 'public_ticket'}
            )

            default_status = TicketStatus.objects.get(code='open') # Assuming 'open' status exists

            # Create the ticket
            ticket = Ticket.objects.create(
                customer=user_instance,
                subject=subject,
                source='web', # Or 'public_form'
                type=ticket_type,
                priority=ticket_priority,
                status=default_status,
                is_new=True,
                isReplied=False,
                isAgentViewed=False,
                isCustomerViewed=True, # Customer just created it
            )

            # Create the initial thread message
            # Assuming Thread model exists and can be imported from ticket.models
            from ticket.models import Thread
            Thread.objects.create(
                ticket=ticket,
                user=user_instance, # UserInstance is the customer
                threadType='create',
                message=message,
                createdBy='customer',
            )

            messages.success(request, 'Your ticket has been created successfully!')
            return redirect('create_ticket_public')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PublicTicketForm()

    context = {
        'form': form
    }
    return render(request, 'customer/create_ticket_public.html', context)

def public_search_results(request):
    query = request.GET.get('q')
    articles = Article.objects.filter(name__icontains=query) if query else Article.objects.none()
    context = {
        'query': query,
        'articles': articles
    }
    return render(request, 'customer/public_search_results.html', context)

def public_folder_detail(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    categories = folder.categories.all()
    context = {
        'folder': folder,
        'categories': categories
    }
    return render(request, 'customer/public_folder_detail.html', context)

def public_folder_articles(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id)
    articles = Article.objects.filter(categories__in=folder.categories.all()).distinct()
    context = {
        'folder': folder,
        'articles': articles
    }
    return render(request, 'customer/public_folder_articles.html', context)

def public_category_detail(request, folder_id, category_id):
    folder = get_object_or_404(Folder, id=folder_id)
    category = get_object_or_404(SolutionCategory, id=category_id)
    articles = Article.objects.filter(categories=category)
    context = {
        'folder': folder,
        'category': category,
        'articles': articles
    }
    return render(request, 'customer/public_category_detail.html', context)

def public_article_detail(request, article_slug):
    article = get_object_or_404(Article, slug=article_slug)
    # Increment view count
    article.viewed = models.F('viewed') + 1
    article.save()
    # Refresh from DB to get updated viewed count
    article.refresh_from_db()

    related_articles = article.related_articles.all()

    context = {
        'article': article,
        'related_articles': related_articles
    }
    return render(request, 'customer/public_article_detail.html', context)

from django.contrib.auth import authenticate, login, logout
from authentication.email import EmailManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from authentication.models import User, UserInstance, SupportRole
from django.utils import timezone

def customer_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        password = request.POST.get('password')
        action = request.POST.get('action') # To differentiate between Send OTP, Login with Password

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, 'No account found with that email address.')
            return render(request, 'customer/customer_login.html', {'email': email})

        if action == 'send_otp':
            # Generate OTP
            import random
            otp_code = str(random.randint(100000, 999999))
            user.verificationCode = otp_code
            user.lastOtpGeneratedAt = timezone.now()
            user.save()

            # Send OTP email
            EmailManager.send_otp_email(user, otp_code)
            messages.success(request, 'OTP sent to your email.')
            return render(request, 'customer/customer_login.html', {'email': email, 'otp_sent': True, 'has_password': user.has_usable_password()})

        elif action == 'verify_otp':
            # This block requires OTP to be present
            if not otp:
                messages.error(request, 'Please enter the OTP.')
                return render(request, 'customer/customer_login.html', {'email': email, 'otp_sent': True, 'has_password': user.has_usable_password()})

            print(f"DEBUG: Stored OTP: {user.verificationCode}, Entered OTP: {otp}")
            if user.lastOtpGeneratedAt is None:
                messages.error(request, 'Invalid or expired OTP.')
                return render(request, 'customer/customer_login.html', {'email': email, 'otp_sent': True, 'has_password': user.has_usable_password()})
            print(f"DEBUG: Time diff: {(timezone.now() - user.lastOtpGeneratedAt).total_seconds()}")

            if user.verificationCode == otp and (timezone.now() - user.lastOtpGeneratedAt).total_seconds() < 300:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                return try_login_customer(request, user)
            else:
                messages.error(request, 'Invalid or expired OTP.')
                return render(request, 'customer/customer_login.html', {'email': email, 'otp_sent': True, 'has_password': user.has_usable_password()})

        elif action == 'login_with_password':
            user_auth = authenticate(request, username=email, password=password)
            if user_auth is not None:
                login(request, user_auth)
                try_login_customer(request, user_auth)
            else:
                messages.error(request, 'Invalid email or password.')
                return render(request, 'customer/customer_login.html', {'email': email, 'has_password': user.has_usable_password(), 'show_password_form': True})

        elif action == 'check_email': # Initial email submission to check for password
            context = {'email': email, 'has_password': user.has_usable_password()}
            if user.has_usable_password():
                context['show_password_form'] = False # Initially hide password form, show OTP/Password choice
            else:
                context['otp_sent'] = True # Directly go to OTP if no password
                # Generate and send OTP immediately if no password
                import random
                otp_code = str(random.randint(100000, 999999))
                user.verificationCode = otp_code
                user.lastOtpGeneratedAt = timezone.now()
                user.save()
                EmailManager.send_otp_email(user, otp_code)
                messages.success(request, 'OTP sent to your email.')
            return render(request, 'customer/customer_login.html', context)

    else: # GET request
        return render(request, 'customer/customer_login.html', {})

def try_login_customer(request, user):
    try:
        user_instance = UserInstance.objects.get(user=user)
        if user_instance.supportRole and user_instance.supportRole.code == 'ROLE_CUSTOMER':
            messages.success(request, 'Logged in successfully!')
            return redirect('authenticated_customer_dashboard')
        else:
            logout(request)
            messages.error(request, 'You do not have customer access.')
            return redirect('customer_login')
    except UserInstance.DoesNotExist:
        logout(request)
        messages.error(request, 'No customer profile found for this user.')
        return redirect('customer_login')

def customer_logout(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('customer_login')

@customer_login_required
def authenticated_customer_dashboard(request):
    # This will be the authenticated customer's main hub
    # For now, just a placeholder
    context = {
        'user': request.user
    }
    return render(request, 'customer/authenticated_customer_dashboard.html', context)

@customer_login_required
def customer_ticket_list(request):
    # List tickets for the logged-in customer
    customer_user_instance = request.user.user_instances.first() # Assuming one-to-one relationship
    tickets = Ticket.objects.filter(customer=customer_user_instance).order_by('-createdAt')
    context = {
        'tickets': tickets
    }
    return render(request, 'customer/customer_ticket_list.html', context)

@customer_login_required
def customer_view_ticket(request, ticket_id):
    # View a specific ticket for the logged-in customer
    customer_user_instance = request.user.user_instances.first()
    ticket = get_object_or_404(Ticket, id=ticket_id, customer=customer_user_instance)
    threads = ticket.threads.all().order_by('createdAt')

    # Handle reply form submission
    if request.method == 'POST':
        message_content = request.POST.get('message')
        if message_content:
            from ticket.models import Thread
            Thread.objects.create(
                ticket=ticket,
                user=customer_user_instance,
                threadType='reply',
                message=message_content,
                createdBy='customer',
            )
            messages.success(request, 'Your reply has been added.')
            return redirect('customer_view_ticket', ticket_id=ticket.id)
        else:
            messages.error(request, 'Reply message cannot be empty.')

    context = {
        'ticket': ticket,
        'threads': threads
    }
    return render(request, 'customer/customer_view_ticket.html', context)

@customer_login_required
def create_ticket_authenticated(request):
    # Authenticated form for creating a ticket
    customer_user_instance = request.user.user_instances.first()
    if request.method == 'POST':
        form = PublicTicketForm(request.POST) # Reuse the public form for now
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            ticket_type = form.cleaned_data['ticket_type']
            ticket_priority = form.cleaned_data['ticket_priority']
            default_status = TicketStatus.objects.get(code='open')

            ticket = Ticket.objects.create(
                customer=customer_user_instance,
                subject=subject,
                source='authenticated_web',
                type=ticket_type,
                priority=ticket_priority,
                status=default_status,
                is_new=True,
                isReplied=False,
                isAgentViewed=False,
                isCustomerViewed=True,
            )

            from ticket.models import Thread
            Thread.objects.create(
                ticket=ticket,
                user=customer_user_instance,
                threadType='create',
                message=message,
                createdBy='customer',
            )

            messages.success(request, 'Your ticket has been created successfully!')
            return redirect('customer_ticket_list') # Redirect to customer's ticket list
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PublicTicketForm()

    context = {
        'form': form
    }
    return render(request, 'customer/create_ticket_authenticated.html', context)

@customer_login_required
def customer_profile(request):
    # Customer profile management
    # For now, just a placeholder
    context = {
        'user': request.user
    }
    return render(request, 'customer/customer_profile.html', context)
