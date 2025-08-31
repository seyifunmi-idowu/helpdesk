from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from django.http import JsonResponse
from django.db import models
from .models import Workflow, TicketType, Tag, SavedReplies, PreparedResponse
from .forms import WorkflowForm, TicketTypeForm, TagForm, SavedReplyForm, PreparedResponseForm
from authentication.models import UserInstance, SupportGroup, SupportTeam
from .constants import PREPARED_RESPONSE_ACTIONS, EMAIL_TEMPLATES, PRIORITIES, STATUSES

@login_required
def workflow_list(request):
    workflows = Workflow.objects.all()
    context = {
        "view": "Workflows",
        "user": request.user,
        "workflows": workflows
    }
    return render(request, "workflow_list.html", context)

@login_required
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

@login_required
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

@login_required
def workflow_delete(request, workflow_id):
    workflow = get_object_or_404(Workflow, pk=workflow_id)
    if request.method == 'POST':
        workflow.delete()
        messages.success(request, f"Workflow '{workflow.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('workflow_list')


@login_required
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

@login_required
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

@login_required
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

@login_required
def ticket_type_delete(request, ticket_type_id):
    ticket_type = get_object_or_404(TicketType, pk=ticket_type_id)
    if request.method == 'POST':
        ticket_type.delete()
        messages.success(request, f"Ticket Type '{ticket_type.code}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('ticket_type_list')

@login_required
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

@login_required
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

@login_required
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

@login_required
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if request.method == 'POST':
        tag.delete()
        messages.success(request, f"Tag '{tag.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('tag_list')

@login_required
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

@login_required
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

@login_required
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

@login_required
def saved_reply_delete(request, saved_reply_id):
    saved_reply = get_object_or_404(SavedReplies, pk=saved_reply_id)
    if request.method == 'POST':
        saved_reply.delete()
        messages.success(request, f"Saved Reply '{saved_reply.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('saved_reply_list')

@login_required
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

@login_required
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

@login_required
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

@login_required
def prepared_response_delete(request, prepared_response_id):
    prepared_response = get_object_or_404(PreparedResponse, pk=prepared_response_id)
    if request.method == 'POST':
        prepared_response.delete()
        messages.success(request, f"Prepared Response '{prepared_response.name}' deleted successfully.")
    else:
        messages.error(request, "Invalid request method.")
    return redirect('prepared_response_list')

# API Views
@login_required
def get_agents(request):
    agents = UserInstance.objects.filter(supportRole__code='ROLE_AGENT').values('id', name=models.F('user__firstName'))
    return JsonResponse(list(agents), safe=False)

@login_required
def get_groups(request):
    groups = SupportGroup.objects.all().values('id', 'name')
    return JsonResponse(list(groups), safe=False)

@login_required
def get_teams(request):
    teams = SupportTeam.objects.all().values('id', 'name')
    return JsonResponse(list(teams), safe=False)

@login_required
def get_tags(request):
    tags = Tag.objects.all().values('id', 'name')
    return JsonResponse(list(tags), safe=False)

@login_required
def get_ticket_types(request):
    ticket_types = TicketType.objects.all().values('id', name=models.F('code'))
    return JsonResponse(list(ticket_types), safe=False)

@login_required
def get_priorities(request):
    return JsonResponse(PRIORITIES, safe=False)

@login_required
def get_statuses(request):
    return JsonResponse(STATUSES, safe=False)

@login_required
def get_email_templates(request):
    return JsonResponse(EMAIL_TEMPLATES, safe=False)
