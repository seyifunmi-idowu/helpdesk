from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse
from django.db import models
from .models import Workflow, TicketType, Tag, SavedReplies, PreparedResponse, Ticket, TicketStatus, TicketPriority, Thread, SupportLabel, AgentActivity
from .forms import WorkflowForm, TicketTypeForm, TagForm, SavedReplyForm, PreparedResponseForm, ThreadForm, NoteForm, ForwardForm, CollaboratorForm, TicketForm, SupportLabelForm
from .services import get_or_create_user_instance
from authentication.models import User, UserInstance, SupportGroup, SupportTeam
from .constants import PREPARED_RESPONSE_ACTIONS, EMAIL_TEMPLATES, PRIORITIES, STATUSES
from authentication.decorators import admin_login_required, permission_required

def create_agent_activity(agent, ticket, activity_type):
    AgentActivity.objects.create(
        agent=agent,
        ticket=ticket,
        agentName=agent.user.get_full_name(),
        customerName=ticket.customer.user.get_full_name(),
        threadType=activity_type
    )

def format_count(count):
    if 100 <= count <= 199:
        return "100+"
    elif 600 <= count <= 699:
        return "600+"
    elif count >= 1000:
        return "1000+"
    else:
        return str(count)

@admin_login_required
@permission_required('ROLE_AGENT_VIEW_AGENT_ACTIVITY') # Assuming a new permission is needed
def agent_activity_list(request):
    all_activities = AgentActivity.objects.all().order_by('-createdAt')

    ticket_id = request.GET.get('ticket_id')
    agent_id = request.GET.get('agent_id')

    if ticket_id:
        all_activities = all_activities.filter(ticket__id=ticket_id)
    if agent_id:
        all_activities = all_activities.filter(agent__id=agent_id)

    paginator = Paginator(all_activities, 20) # 20 activities per page
    page = request.GET.get('page')

    try:
        agent_activities = paginator.page(page)
    except PageNotAnInteger:
        agent_activities = paginator.page(1)
    except EmptyPage:
        agent_activities = paginator.page(paginator.num_pages)

    context = {
        "view": "Agent Activities",
        "user": request.user,
        "agent_activities": agent_activities,
        "ticket_id": ticket_id or '',
        "agent_id": agent_id or '',
    }
    return render(request, "ticket/agent_activity_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_VIEW_AGENT_ACTIVITY') # Assuming a new permission is needed
def agent_activity_detail(request, activity_id):
    activity = get_object_or_404(AgentActivity, pk=activity_id)

    context = {
        "view": "Agent Activity Detail",
        "user": request.user,
        "activity": activity,
    }
    return render(request, "ticket/agent_activity_detail.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_EDIT_TICKET')
def ticket_list(request):
    # Base queryset for all tickets
    all_tickets = Ticket.objects.all().order_by('-createdAt')

    customer_id = request.GET.get('customer_id')
    customer = None
    if customer_id:
        try:
            customer_id = int(customer_id)
            all_tickets = all_tickets.filter(customer__user__id=customer_id)
            customer = User.objects.get(id=customer_id)
        except (ValueError, TypeError, User.DoesNotExist):
            # Handle cases where customer_id is not a valid integer or user does not exist
            # For now, we'll just ignore the filter and set customer to None
            customer_id = None
            customer = None

    label_id = request.GET.get('label_id')
    if label_id:
        try:
            label_id = int(label_id)
            all_tickets = all_tickets.filter(supportLabels__id=label_id)
        except (ValueError, TypeError):
            pass

    # Set up Paginator
    tickets_per_page = 10  # You can adjust this number
    paginator = Paginator(all_tickets, tickets_per_page)

    page = request.GET.get('page')
    try:
        tickets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        tickets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        tickets = paginator.page(paginator.num_pages)

    # Calculate sidebar counts
    all_count = all_tickets.count()
    new_count = all_tickets.filter(is_new=True).count()
    unassigned_count = all_tickets.filter(agent__isnull=True).count()
    unanswered_count = all_tickets.filter(isReplied=False).count()
    my_tickets_count = all_tickets.filter(agent__user=request.user).count() # Assuming request.user is the agent
    starred_count = all_tickets.filter(isStarred=True).count()
    trashed_count = all_tickets.filter(isTrashed=True).count()

    sidebar_filters = {
        'all': {'label': 'All', 'count': format_count(all_count)},
        'new': {'label': 'New', 'count': format_count(new_count)},
        'unassigned': {'label': 'Unassigned', 'count': format_count(unassigned_count)},
        'unanswered': {'label': 'Unanswered', 'count': format_count(unanswered_count)},
        'my_tickets': {'label': 'My Tickets', 'count': format_count(my_tickets_count)},
        'starred': {'label': 'Starred', 'count': format_count(starred_count)},
        'trashed': {'label': 'Trashed', 'count': format_count(trashed_count)},
    }

    # Calculate sub-filter (status) counts for 'All' tickets initially
    status_counts = {}
    statuses = TicketStatus.objects.all().order_by('sortOrder') # Assuming sortOrder exists
    for status in statuses:
        count = all_tickets.filter(status=status).count()
        status_counts[status.code] = {'label': status.description, 'count': format_count(count)}

    # Calculate sub-filter (label) counts
    label_counts = {}
    # Only show labels associated with the current agent's user instance
    current_agent_user_instance = request.user.user_instances.first()
    if current_agent_user_instance:
        labels = SupportLabel.objects.filter(user=current_agent_user_instance).order_by('name')
        for label in labels:
            count = all_tickets.filter(supportLabels=label).count()
            label_counts[label.id] = {'label': label.name, 'count': format_count(count)}

    context = {
        "view": "Tickets",
        "user": request.user,
        "sidebar_filters": sidebar_filters,
        "status_counts": status_counts,
        "label_counts": label_counts,
        "tickets": tickets, # Pass the Page object
        "customer": customer,
        "customer_id": customer_id,
        "selected_label_id": label_id, # Pass selected label ID to template
    }
    return render(request, "ticket_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_EDIT_TICKET')
def get_filtered_tickets_and_counts(request):
    filter_type = request.GET.get('filter_type', 'all')
    status_code = request.GET.get('status_code', None)
    label_id = request.GET.get('label_id', None)
    customer_id = request.GET.get('customer_id')

    tickets_queryset = Ticket.objects.all().order_by('-createdAt')
    if customer_id:
        try:
            customer_id = int(customer_id)
            tickets_queryset = tickets_queryset.filter(customer__user__id=customer_id)
        except (ValueError, TypeError):
            # Handle cases where customer_id is not a valid integer (e.g., 'None', '')
            # You might want to log this or return an error response depending on desired behavior
            # For now, we'll just ignore the filter if customer_id is invalid
            pass

    # Apply primary filter
    if filter_type == 'new':
        tickets_queryset = tickets_queryset.filter(is_new=True)
    elif filter_type == 'unassigned':
        tickets_queryset = tickets_queryset.filter(agent__isnull=True)
    elif filter_type == 'unanswered':
        tickets_queryset = tickets_queryset.filter(isReplied=False)
    elif filter_type == 'my_tickets':
        tickets_queryset = tickets_queryset.filter(agent__user=request.user)
    elif filter_type == 'starred':
        tickets_queryset = tickets_queryset.filter(isStarred=True)
    elif filter_type == 'trashed':
        tickets_queryset = tickets_queryset.filter(isTrashed=True)

    # Apply status sub-filter if provided
    if status_code:
        tickets_queryset = tickets_queryset.filter(status__code=status_code)

    # Apply label sub-filter if provided
    if label_id:
        try:
            label_id = int(label_id)
            tickets_queryset = tickets_queryset.filter(supportLabels__id=label_id)
        except (ValueError, TypeError):
            pass

    # Set up Paginator for the filtered queryset
    tickets_per_page = 100  # Consistent with ticket_list view
    paginator = Paginator(tickets_queryset, tickets_per_page)

    page = request.GET.get('page')
    try:
        tickets_page_obj = paginator.page(page)
    except PageNotAnInteger:
        tickets_page_obj = paginator.page(1)
    except EmptyPage:
        tickets_page_obj = paginator.page(paginator.num_pages)

    # Recalculate sidebar counts based on the current primary filter (before status and label filter)
    # This is important because the sidebar counts should reflect the primary category
    # regardless of the selected status/label sub-filter.
    all_tickets_for_primary_filter = Ticket.objects.all()
    # Apply customer_id filter if valid
    if customer_id: # customer_id might be None if it was invalid in the initial check
        try:
            # Ensure customer_id is an int for this filter as well
            valid_customer_id = int(customer_id)
            all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(customer__user__id=valid_customer_id)
        except (ValueError, TypeError):
            pass # Ignore filter if customer_id is invalid

    if filter_type == 'new':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(is_new=True)
    elif filter_type == 'unassigned':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(agent__isnull=True)
    elif filter_type == 'unanswered':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(isReplied=False)
    elif filter_type == 'my_tickets':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(agent__user=request.user)
    elif filter_type == 'starred':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(isStarred=True)
    elif filter_type == 'trashed':
        all_tickets_for_primary_filter = all_tickets_for_primary_filter.filter(isTrashed=True)

    sidebar_filters_updated = {
        'all': {'label': 'All', 'count': format_count(all_tickets_for_primary_filter.count())},
        'new': {'label': 'New', 'count': format_count(all_tickets_for_primary_filter.filter(is_new=True).count())},
        'unassigned': {'label': 'Unassigned', 'count': format_count(all_tickets_for_primary_filter.filter(agent__isnull=True).count())},
        'unanswered': {'label': 'Unanswered', 'count': format_count(all_tickets_for_primary_filter.filter(isReplied=False).count())},
        'my_tickets': {'label': 'My Tickets', 'count': format_count(all_tickets_for_primary_filter.filter(agent__user=request.user).count())},
        'starred': {'label': 'Starred', 'count': format_count(all_tickets_for_primary_filter.filter(isStarred=True).count())},
        'trashed': {'label': 'Trashed', 'count': format_count(all_tickets_for_primary_filter.filter(isTrashed=True).count())},
    }

    # Recalculate status counts based on the current primary filter
    status_counts_updated = {}
    statuses = TicketStatus.objects.all().order_by('sortOrder')
    for status in statuses:
        count = all_tickets_for_primary_filter.filter(status=status).count()
        status_counts_updated[status.code] = {'label': status.description, 'count': format_count(count)}

    # Recalculate label counts based on the current primary filter
    label_counts_updated = {}
    current_agent_user_instance = request.user.user_instances.first()
    if current_agent_user_instance:
        labels = SupportLabel.objects.filter(user=current_agent_user_instance).order_by('name')
        for label in labels:
            count = all_tickets_for_primary_filter.filter(supportLabels=label).count()
            label_counts_updated[label.id] = {'label': label.name, 'count': format_count(count)}

    # Serialize tickets
    tickets_data = []
    for ticket in tickets_page_obj:
        tickets_data.append({
            'id': ticket.id,
            'subject': ticket.subject,
            'customer_email': ticket.customer.user.email if ticket.customer and ticket.customer.user else 'N/A',
            'status_description': ticket.status.description if ticket.status else 'N/A',
            'priority_description': ticket.priority.description if ticket.priority else 'N/A',
            'agent_email': ticket.agent.user.email if ticket.agent and ticket.agent.user else 'Unassigned',
            'created_at': ticket.createdAt.strftime("%b %d, %Y %H:%M"),
        })

    return JsonResponse({
        'tickets': tickets_data,
        'sidebar_filters': sidebar_filters_updated,
        'status_counts': status_counts_updated,
        'label_counts': label_counts_updated,
        'pagination': {
            'num_pages': tickets_page_obj.paginator.num_pages,
            'current_page': tickets_page_obj.number,
            'has_next': tickets_page_obj.has_next(),
            'has_previous': tickets_page_obj.has_previous(),
            'next_page_number': tickets_page_obj.next_page_number() if tickets_page_obj.has_next() else None,
            'previous_page_number': tickets_page_obj.previous_page_number() if tickets_page_obj.has_previous() else None,
            'page_range': list(tickets_page_obj.paginator.page_range),
        }
    })

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_AUTOMATIC')
def workflow_list(request):
    workflows = Workflow.objects.all()
    context = {
        "view": "Workflows",
        "user": request.user,
        "workflows": workflows
    }
    return render(request, "workflow_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_AUTOMATIC')
def workflow_create(request):
    if request.method == 'POST':
        form = WorkflowForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Workflow created successfully.")
            return redirect('workflow_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = WorkflowForm()

    context = {
        "view": "Create Workflow",
        "user": request.user,
        "form": form
    }
    return render(request, "workflow_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_AUTOMATIC')
def workflow_edit(request, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if request.method == 'POST':
        form = WorkflowForm(request.POST, instance=workflow)
        if form.is_valid():
            form.save()
            messages.success(request, "Workflow updated successfully.")
            return redirect('workflow_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = WorkflowForm(instance=workflow)

    context = {
        "view": "Edit Workflow",
        "user": request.user,
        "form": form,
        "workflow_id": workflow_id
    }
    return render(request, "workflow_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_AUTOMATIC')
def workflow_delete(request, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if request.method == 'POST':
        workflow.delete()
        messages.success(request, f"Workflow '{workflow.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('workflow_list')


@admin_login_required
@permission_required('ROLE_AGENT_CREATE_TICKET')
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False) # Save ticket instance but don't commit yet

            # The customer is already set by form.save() in TicketForm's save method
            # Now save the ticket to the database
            ticket.save()

            # Create the initial thread for the ticket
            initial_thread = Thread.objects.create(
                ticket=ticket,
                user=ticket.customer, # The customer is the initial sender
                source='web', # Assuming web creation
                message=form.cleaned_data['initial_message'],
                threadType='initial_message', # Custom type for initial message
                createdBy='agent', # Agent created it
            )

            # Send initial ticket email
            from .email_utils import send_initial_ticket_email
            try:
                generated_message_id = send_initial_ticket_email(ticket, initial_thread)
                initial_thread.messageId = generated_message_id # Save the generated Message-ID
                initial_thread.save() # Save the thread with the Message-ID
                messages.success(request, "Ticket created successfully and initial email sent.")
            except Exception as e:
                messages.error(request, f"Ticket created, but failed to send initial email: {e}")

            return redirect('ticket_view', ticket_id=ticket.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TicketForm()

    context = {
        "view": "Create Ticket",
        "user": request.user,
        "form": form
    }
    return render(request, "ticket_create.html", context)


@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TICKET_TYPE')
def ticket_type_list(request):
    ticket_types = TicketType.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        ticket_types = ticket_types.filter(models.Q(code__icontains=search_query) | models.Q(description__icontains=search_query))

    # Filter by isActive
    is_active_filter = request.GET.get('is_active')
    if is_active_filter == 'true':
        ticket_types = ticket_types.filter(isActive=True)
    elif is_active_filter == 'false':
        ticket_types = ticket_types.filter(isActive=False)

    # Sorting
    sort_by = request.GET.get('sort_by', 'code') # Default sort by code
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    ticket_types = ticket_types.order_by(sort_by)

    context = {
        "view": "Ticket Types",
        "user": request.user,
        "ticket_types": ticket_types,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''), # Pass original field name to template
        "order": order,
        "is_active_filter": is_active_filter,
    }
    return render(request, "ticket_type_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TICKET_TYPE')
def ticket_type_create(request):
    if request.method == 'POST':
        form = TicketTypeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket Type created successfully.")
            return redirect('ticket_type_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TicketTypeForm()

    context = {
        "view": "Create Ticket Type",
        "user": request.user,
        "form": form
    }
    return render(request, "ticket_type_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TICKET_TYPE')
def ticket_type_edit(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    if request.method == 'POST':
        form = TicketTypeForm(request.POST, instance=ticket_type)
        if form.is_valid():
            form.save()
            messages.success(request, "Ticket Type updated successfully.")
            return redirect('ticket_type_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TicketTypeForm(instance=ticket_type)

    context = {
        "view": "Edit Ticket Type",
        "user": request.user,
        "form": form,
        "ticket_type_id": ticket_type_id
    }
    return render(request, "ticket_type_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TICKET_TYPE')
def ticket_type_delete(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    if request.method == 'POST':
        ticket_type.delete()
        messages.success(request, f"Ticket Type '{ticket_type.code}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('ticket_type_list')

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TAG')
def tag_list(request):
    tags = Tag.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        tags = tags.filter(name__icontains=search_query)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    tags = tags.order_by(sort_by)

    context = {
        "view": "Tags",
        "user": request.user,
        "tags": tags,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
    }
    return render(request, "tag_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TAG')
def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag created successfully.")
            return redirect('tag_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TagForm()

    context = {
        "view": "Create Tag",
        "user": request.user,
        "form": form
    }
    return render(request, "tag_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TAG')
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        form = TagForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            messages.success(request, "Tag updated successfully.")
            return redirect('tag_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = TagForm(instance=tag)

    context = {
        "view": "Edit Tag",
        "user": request.user,
        "form": form,
        "tag_id": tag_id
    }
    return render(request, "tag_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TAG')
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, f"Tag '{tag.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('tag_list')

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_SUPPORT_LABEL')
def support_label_list(request):
    labels = SupportLabel.objects.filter(user=request.user.user_instances.first())
    context = {
        "view": "Support Labels",
        "user": request.user,
        "labels": labels
    }
    return render(request, "support_label_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_SUPPORT_LABEL')
def support_label_create(request):
    if request.method == 'POST':
        form = SupportLabelForm(request.POST)
        if form.is_valid():
            label = form.save(commit=False)
            label.user = request.user.user_instances.first()
            label.save()
            messages.success(request, "Support Label created successfully.")
            return redirect('support_label_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupportLabelForm()

    context = {
        "view": "Create Support Label",
        "user": request.user,
        "form": form
    }
    return render(request, "support_label_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_SUPPORT_LABEL')
def support_label_edit(request, label_id):
    label = get_object_or_404(SupportLabel, pk=label_id, user=request.user.user_instances.first())
    if request.method == 'POST':
        form = SupportLabelForm(request.POST, instance=label)
        if form.is_valid():
            form.save()
            messages.success(request, "Support Label updated successfully.")
            return redirect('support_label_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SupportLabelForm(instance=label)

    context = {
        "view": "Edit Support Label",
        "user": request.user,
        "form": form,
        "label_id": label_id
    }
    return render(request, "support_label_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_SUPPORT_LABEL')
def support_label_delete(request, label_id):
    label = get_object_or_404(SupportLabel, pk=label_id, user=request.user.user_instances.first())
    if request.method == 'POST':
        label.delete()
        messages.success(request, f"Support Label '{label.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('support_label_list')

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def saved_reply_list(request):
    saved_replies = SavedReplies.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        saved_replies = saved_replies.filter(
            models.Q(name__icontains=search_query) |
            models.Q(subject__icontains=search_query) |
            models.Q(message__icontains=search_query)
        )

    # Filter by isPredefind
    is_predefined_filter = request.GET.get('is_predefined')
    if is_predefined_filter == 'true':
        saved_replies = saved_replies.filter(isPredefind=True)
    elif is_predefined_filter == 'false':
        saved_replies = saved_replies.filter(isPredefind=False)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    saved_replies = saved_replies.order_by(sort_by)

    context = {
        "view": "Saved Replies",
        "user": request.user,
        "saved_replies": saved_replies,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "is_predefined_filter": is_predefined_filter,
    }
    return render(request, "saved_reply_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def saved_reply_create(request):
    if request.method == 'POST':
        form = SavedReplyForm(request.POST)
        if form.is_valid():
            saved_reply = form.save(commit=False)
            # Assign the current user as the owner
            try:
                user_instance = UserInstance.objects.get(user=request.user)
                saved_reply.user = user_instance
            except UserInstance.DoesNotExist:
                messages.error(request, "User instance not found. Cannot create saved reply.")
                return render(request, "saved_reply_create_edit.html", {"view": "Create Saved Reply", "user": request.user, "form": form})
            saved_reply.save()
            messages.success(request, "Saved Reply created successfully.")
            return redirect('saved_reply_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SavedReplyForm()

    context = {
        "view": "Create Saved Reply",
        "user": request.user,
        "form": form
    }
    return render(request, "saved_reply_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def saved_reply_edit(request, saved_reply_id):
    saved_reply = get_object_or_404(SavedReplies, pk=saved_reply_id)
    if request.method == 'POST':
        form = SavedReplyForm(request.POST, instance=saved_reply)
        if form.is_valid():
            form.save()
            messages.success(request, "Saved Reply updated successfully.")
            return redirect('saved_reply_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = SavedReplyForm(instance=saved_reply)

    context = {
        "view": "Edit Saved Reply",
        "user": request.user,
        "form": form,
        "saved_reply_id": saved_reply_id
    }
    return render(request, "saved_reply_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def saved_reply_delete(request, saved_reply_id):
    saved_reply = get_object_or_404(SavedReplies, pk=saved_reply_id)
    if request.method == 'POST':
        saved_reply.delete()
        messages.success(request, f"Saved Reply '{saved_reply.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('saved_reply_list')

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def prepared_response_list(request):
    prepared_responses = PreparedResponse.objects.all()

    # Search
    search_query = request.GET.get('search')
    if search_query:
        prepared_responses = prepared_responses.filter(models.Q(name__icontains=search_query) | models.Q(description__icontains=search_query))

    # Filter by type
    type_filter = request.GET.get('type')
    if type_filter:
        prepared_responses = prepared_responses.filter(type=type_filter)

    # Sorting
    sort_by = request.GET.get('sort_by', 'name') # Default sort by name
    order = request.GET.get('order', 'asc') # Default order ascending

    if order == 'desc':
        sort_by = '-' + sort_by

    prepared_responses = prepared_responses.order_by(sort_by)

    context = {
        "view": "Prepared Responses",
        "user": request.user,
        "prepared_responses": prepared_responses,
        "search_query": search_query,
        "sort_by": sort_by.replace('-', ''),
        "order": order,
        "type_filter": type_filter,
    }
    return render(request, "prepared_response_list.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def prepared_response_create(request):
    if request.method == 'POST':
        form = PreparedResponseForm(request.POST)
        if form.is_valid():
            prepared_response = form.save(commit=False)
            # Assign the current user as the owner
            try:
                user_instance = UserInstance.objects.get(user=request.user)
                prepared_response.user = user_instance
            except UserInstance.DoesNotExist:
                messages.error(request, "User instance not found. Cannot create prepared response.")
                return render(request, "prepared_response_create_edit.html", {"view": "Create Prepared Response", "user": request.user, "form": form})
            prepared_response.save()
            messages.success(request, "Prepared Response created successfully.")
            return redirect('prepared_response_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PreparedResponseForm()

    context = {
        "view": "Create Prepared Response",
        "user": request.user,
        "form": form,
        "prepared_response_actions": PREPARED_RESPONSE_ACTIONS,
        "current_actions_json": []
    }
    return render(request, "prepared_response_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def prepared_response_edit(request, prepared_response_id):
    prepared_response = get_object_or_404(PreparedResponse, pk=prepared_response_id)
    current_actions_json = prepared_response.actions if prepared_response.actions else []

    if request.method == 'POST':
        form = PreparedResponseForm(request.POST, instance=prepared_response)
        if form.is_valid():
            # Handle actions field manually as it's not directly in the form
            actions_json = request.POST.get('actions_json_data')
            if actions_json:
                try:
                    prepared_response.actions = json.loads(actions_json)
                except json.JSONDecodeError:
                    messages.error(request, "Actions data is not valid JSON.")
                    context = {
                        "view": "Edit Prepared Response",
                        "user": request.user,
                        "form": form,
                        "prepared_response_id": prepared_response_id,
                        "prepared_response_actions": PREPARED_RESPONSE_ACTIONS,
                        "current_actions_json": actions_json # Pass back invalid JSON for correction
                    }
                    return render(request, "prepared_response_create_edit.html", context)
            else:
                prepared_response.actions = [] # Or None, depending on desired default

            form.save()
            messages.success(request, "Prepared Response updated successfully.")
            return redirect('prepared_response_list')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PreparedResponseForm(instance=prepared_response)

    context = {
        "view": "Edit Prepared Response",
        "user": request.user,
        "form": form,
        "prepared_response_id": prepared_response_id,
        "prepared_response_actions": PREPARED_RESPONSE_ACTIONS,
        "current_actions_json": current_actions_json
    }
    return render(request, "prepared_response_create_edit.html", context)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_WORKFLOW_MANUAL')
def prepared_response_delete(request, prepared_response_id):
    prepared_response = get_object_or_404(PreparedResponse, pk=prepared_response_id)
    if request.method == 'POST':
        prepared_response.delete()
        messages.success(request, f"Prepared Response '{prepared_response.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('prepared_response_list')

# API Views
@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_AGENT')
def get_agents(request):
    agents = UserInstance.objects.filter(supportRole__code='ROLE_AGENT').values('id', name=models.F('user__firstName'))
    return JsonResponse(list(agents), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_GROUP')
def get_groups(request):
    groups = SupportGroup.objects.all().values('id', 'name')
    return JsonResponse(list(groups), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_SUB_GROUP')
def get_teams(request):
    teams = SupportTeam.objects.all().values('id', 'name')
    return JsonResponse(list(teams), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TAG')
def get_tags(request):
    tags = Tag.objects.all().values('id', 'name')
    return JsonResponse(list(tags), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_TICKET_TYPE')
def get_ticket_types(request):
    ticket_types = TicketType.objects.all().values('id', name=models.F('code'))
    return JsonResponse(list(ticket_types), safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_EDIT_TICKET')
def get_priorities(request):
    return JsonResponse(PRIORITIES, safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_EDIT_TICKET')
def get_statuses(request):
    return JsonResponse(STATUSES, safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_MANAGE_EMAIL_TEMPLATE')
def get_email_templates(request):
    return JsonResponse(EMAIL_TEMPLATES, safe=False)

@admin_login_required
@permission_required('ROLE_AGENT_UPDATE_TICKET_STATUS')
def update_ticket_status(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_status_id = request.POST.get('status_id')
            if new_status_id:
                new_status = get_object_or_404(TicketStatus, id=new_status_id)
                ticket.status = new_status
                ticket.save()
                create_agent_activity(request.user.user_instances.first(), ticket, f"status_changed_to_{new_status.code}")
                return JsonResponse({'success': True, 'message': 'Ticket status updated successfully.'})
            else:
                return JsonResponse({'success': False, 'error': 'No status ID provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_UPDATE_TICKET_PRIORITY')
def update_ticket_priority(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_priority_id = request.POST.get('priority_id')
            if new_priority_id:
                new_priority = get_object_or_404(TicketPriority, id=new_priority_id)
                ticket.priority = new_priority
                ticket.save()
                create_agent_activity(request.user.user_instances.first(), ticket, f"priority_changed_to_{new_priority.code}")
                return JsonResponse({'success': True, 'message': 'Ticket priority updated successfully.'})
            else:
                return JsonResponse({'success': False, 'error': 'No priority ID provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_ASSIGN_TICKET')
def update_ticket_agent(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_agent_id = request.POST.get('agent_id')
            if new_agent_id and new_agent_id != '0': # Check for '0' as unassigned
                new_agent = get_object_or_404(UserInstance, id=new_agent_id)
                ticket.agent = new_agent
                create_agent_activity(request.user.user_instances.first(), ticket, f"agent_assigned_to_{new_agent.user.email}")
            else:
                ticket.agent = None # Set to None for unassigned
                create_agent_activity(request.user.user_instances.first(), ticket, "agent_unassigned")
            ticket.save()
            return JsonResponse({'success': True, 'message': 'Ticket agent updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_UPDATE_TICKET_TYPE')
def update_ticket_type(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_type_id = request.POST.get('type_id')
            if new_type_id:
                new_type = get_object_or_404(TicketType, id=new_type_id)
                ticket.type = new_type
                ticket.save()
                create_agent_activity(request.user.user_instances.first(), ticket, f"type_changed_to_{new_type.code}")
                return JsonResponse({'success': True, 'message': 'Ticket type updated successfully.'})
            else:
                return JsonResponse({'success': False, 'error': 'No type ID provided.'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_ASSIGN_TICKET_GROUP')
def update_ticket_group(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_group_id = request.POST.get('group_id')
            if new_group_id and new_group_id != '0': # Check for '0' as unassigned
                new_group = get_object_or_404(SupportGroup, id=new_group_id)
                ticket.supportGroup = new_group
                create_agent_activity(request.user.user_instances.first(), ticket, f"group_changed_to_{new_group.name}")
            else:
                ticket.supportGroup = None # Set to None for unassigned
                create_agent_activity(request.user.user_instances.first(), ticket, "group_unassigned")
            ticket.save()
            return JsonResponse({'success': True, 'message': 'Ticket group updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_ASSIGN_TICKET_GROUP') # Assuming team assignment is part of group assignment privilege
def update_ticket_team(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_team_id = request.POST.get('team_id')
            if new_team_id and new_team_id != '0': # Check for '0' as unassigned
                new_team = get_object_or_404(SupportTeam, id=new_team_id)
                ticket.supportTeam = new_team
                create_agent_activity(request.user.user_instances.first(), ticket, f"team_changed_to_{new_team.name}")
            else:
                ticket.supportTeam = None # Set to None for unassigned
                create_agent_activity(request.user.user_instances.first(), ticket, "team_unassigned")
            ticket.save()
            return JsonResponse({'success': True, 'message': 'Ticket team updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
def update_ticket_team(request, ticket_id):
    if request.method == 'POST':
        try:
            ticket = get_object_or_404(Ticket, id=ticket_id)
            new_team_id = request.POST.get('team_id')
            if new_team_id and new_team_id != '0': # Check for '0' as unassigned
                new_team = get_object_or_404(SupportTeam, id=new_team_id)
                ticket.supportTeam = new_team
            else:
                ticket.supportTeam = None # Set to None for unassigned
            ticket.save()
            return JsonResponse({'success': True, 'message': 'Ticket team updated successfully.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method.'}, status=405)

@admin_login_required
@permission_required('ROLE_AGENT_EDIT_TICKET')
def ticket_view(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    threads = ticket.threads.all().order_by('createdAt')

    if request.method == 'POST':
        agent_instance = request.user.user_instances.first()
        if 'add_tag' in request.POST:
            tag_id = request.POST.get('tag_id')
            if tag_id:
                tag = get_object_or_404(Tag, id=tag_id)
                ticket.supportTags.add(tag)
                create_agent_activity(agent_instance, ticket, f"added_tag_{tag.name}")
                messages.success(request, f"Tag '{tag.name}' added successfully.")
            return redirect('ticket_view', ticket_id=ticket.id)

        if 'remove_tag' in request.POST:
            tag_id = request.POST.get('tag_id')
            if tag_id:
                tag = get_object_or_404(Tag, id=tag_id)
                ticket.supportTags.remove(tag)
                create_agent_activity(agent_instance, ticket, f"removed_tag_{tag.name}")
                messages.success(request, f"Tag '{tag.name}' removed successfully.")
            return redirect('ticket_view', ticket_id=ticket.id)

        if 'add_label' in request.POST:
            label_id = request.POST.get('label_id')
            if label_id:
                label = get_object_or_404(SupportLabel, id=label_id, user=agent_instance)
                ticket.supportLabels.add(label)
                create_agent_activity(agent_instance, ticket, f"added_label_{label.name}")
                messages.success(request, f"Label '{label.name}' added successfully.")
            return redirect('ticket_view', ticket_id=ticket.id)

        if 'remove_label' in request.POST:
            label_id = request.POST.get('label_id')
            if label_id:
                label = get_object_or_404(SupportLabel, id=label_id)
                ticket.supportLabels.remove(label)
                create_agent_activity(agent_instance, ticket, f"removed_label_{label.name}")
                messages.success(request, f"Label '{label.name}' removed successfully.")
            return redirect('ticket_view', ticket_id=ticket.id)

        if 'reply_form' in request.POST:
            reply_form = ThreadForm(request.POST)
            if reply_form.is_valid():
                if not reply_form.cleaned_data['message']:
                    messages.error(request, 'Reply message cannot be empty.')
                else:
                    thread = reply_form.save(commit=False)
                    thread.ticket = ticket
                    thread.user = agent_instance
                    thread.threadType = 'reply'
                    thread.createdBy = 'agent'
                    thread.save()
                    create_agent_activity(agent_instance, ticket, 'agent_replied')
                    from .email_utils import send_reply_email
                    send_reply_email(ticket, thread, reply_form.cleaned_data.get('send_to_collaborators_cc_bcc'))
                    if reply_form.cleaned_data['status']:
                        ticket.status = reply_form.cleaned_data['status']
                        ticket.save()
                    messages.success(request, 'Reply added successfully.')
                    return redirect('ticket_view', ticket_id=ticket.id)
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'note_form' in request.POST:
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                if not note_form.cleaned_data['message']:
                    messages.error(request, 'Note message cannot be empty.')
                else:
                    thread = note_form.save(commit=False)
                    thread.ticket = ticket
                    thread.user = agent_instance
                    thread.threadType = 'note'
                    thread.createdBy = 'agent'
                    thread.save()
                    create_agent_activity(agent_instance, ticket, 'agent_added_note')
                    if note_form.cleaned_data['status']:
                        ticket.status = note_form.cleaned_data['status']
                        ticket.save()
                    messages.success(request, 'Note added successfully.')
                    return redirect('ticket_view', ticket_id=ticket.id)
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'forward_form' in request.POST:
            forward_form = ForwardForm(request.POST)
            if forward_form.is_valid():
                if not forward_form.cleaned_data['message']:
                    messages.error(request, 'Forward message cannot be empty.')
                else:
                    thread = Thread.objects.create(
                        ticket=ticket,
                        user=agent_instance,
                        threadType='forward',
                        createdBy='agent',
                        message=forward_form.cleaned_data['message']
                    )
                    create_agent_activity(agent_instance, ticket, 'agent_forwarded_ticket')
                    if forward_form.cleaned_data['status']:
                        ticket.status = forward_form.cleaned_data['status']
                        ticket.save()
                    from .email_utils import send_forward_email
                    try:
                        send_forward_email(
                            ticket,
                            thread, 
                            forward_form.cleaned_data['to'],
                            forward_form.cleaned_data['subject']
                        )
                        messages.success(request, 'Ticket forwarded successfully and email sent.')
                    except Exception as e:
                        messages.error(request, f'Ticket forwarded, but failed to send email: {e}')

                    return redirect('ticket_view', ticket_id=ticket.id)
            else:
                messages.error(request, 'Please correct the errors below.')
        elif 'collaborator_form' in request.POST:
            collaborator_form = CollaboratorForm(request.POST)
            if collaborator_form.is_valid():
                emails = collaborator_form.cleaned_data['emails']
                ticket = get_object_or_404(Ticket, id=ticket_id)

                added_count = 0
                for email in emails:
                    user_instance = get_or_create_user_instance(email)
                    if user_instance not in ticket.collaborators.all():
                        ticket.collaborators.add(user_instance)
                        create_agent_activity(agent_instance, ticket, f"added_collaborator_{user_instance.user.email}")
                        added_count += 1

                if added_count > 0:
                    messages.success(request, f'{added_count} collaborator(s) added successfully.')
                else:
                    messages.info(request, 'No new collaborators were added.')
                return redirect('ticket_view', ticket_id=ticket.id)
            else:
                messages.error(request, 'Please correct the errors below for collaborators.')
        elif 'remove_collaborator_id' in request.POST:
            collaborator_id = request.POST.get('remove_collaborator_id')
            ticket = get_object_or_404(Ticket, id=ticket_id)
            try:
                user_instance_to_remove = UserInstance.objects.get(id=collaborator_id)
                ticket.collaborators.remove(user_instance_to_remove)
                create_agent_activity(agent_instance, ticket, f"removed_collaborator_{user_instance_to_remove.user.email}")
                messages.success(request, f'Collaborator {user_instance_to_remove.user.email} removed successfully.')
            except UserInstance.DoesNotExist:
                messages.error(request, 'Collaborator not found.')
            except Exception as e:
                messages.error(request, f'Error removing collaborator: {e}')
            return redirect('ticket_view', ticket_id=ticket.id)

    reply_form = ThreadForm()
    note_form = NoteForm()
    forward_form = ForwardForm()
    collaborator_form = CollaboratorForm()

    statuses = TicketStatus.objects.all()
    priorities = TicketPriority.objects.all()
    agents = UserInstance.objects.filter(supportRole__code='ROLE_AGENT')
    ticket_types = TicketType.objects.all()
    groups = SupportGroup.objects.all()
    teams = SupportTeam.objects.all()
    tags = Tag.objects.all()
    labels = SupportLabel.objects.filter(user=request.user.user_instances.first())

    context = {
        'view': 'Ticket View',
        'user': request.user,
        'ticket': ticket,
        'threads': threads,
        'reply_form': reply_form,
        'note_form': note_form,
        'forward_form': forward_form,
        'collaborator_form': collaborator_form,
        'statuses': statuses,
        'priorities': priorities,
        'agents': agents,
        'ticket_types': ticket_types,
        'groups': groups,
        'teams': teams,
        'tags': tags,
        'labels': labels,
    }
    return render(request, 'ticket_view.html', context)
