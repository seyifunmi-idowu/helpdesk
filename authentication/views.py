from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings

from .services import PrivilegeService, GroupService, TeamService
from .constants import PRIVILEGE_CHOICES
from .models import UserInstance, SupportTeam, SupportGroup, User, SupportRole
from .email import EmailManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse


@login_required
def dashboard(request):
    user = request.user
    context = {"view": "Dashboard", "user": user}
    return render(request, "dashboard.html", context)

@login_required
def privilege_list(request):
    privileges = PrivilegeService.get_all_privileges()
    context = {
        "view": "Privileges",
        "user": request.user,
        "privileges": privileges
    }
    return render(request, "privileges_list.html", context)

@login_required
def privilege_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        privileges_list = request.POST.getlist('privileges')

        if name:
            PrivilegeService.create_privilege(name, description, privileges_list)
            messages.success(request, f"Privilege set '{name}' created successfully.")
            return redirect('privilege_list')
        else:
            messages.error(request, "Name is a required field.")

    context = {
        "view": "Privileges",
        "user": request.user,
        "privilege_choices": PRIVILEGE_CHOICES
    }
    return render(request, "privileges_create.html", context)

@login_required
def privilege_edit(request, privilege_id):
    privilege = PrivilegeService.get_privilege_by_id(privilege_id)
    if not privilege:
        messages.error(request, "Privilege set not found.")
        return redirect('privilege_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        privileges_list = request.POST.getlist('privileges')

        if name:
            PrivilegeService.update_privilege(privilege_id, name, description, privileges_list)
            messages.success(request, f"Privilege set '{name}' updated successfully.")
            return redirect('privilege_list')
        else:
            messages.error(request, "Name is a required field.")

    context = {
        "view": "Privileges",
        "user": request.user,
        "privilege": privilege,
        "privilege_choices": PRIVILEGE_CHOICES
    }
    return render(request, "privileges_edit.html", context)

@login_required
def privilege_delete(request, privilege_id):
    if request.method == 'POST':
        privilege = PrivilegeService.get_privilege_by_id(privilege_id)
        if privilege:
            PrivilegeService.delete_privilege(privilege_id)
            messages.success(request, f"Privilege set '{privilege.name}' deleted successfully.")
        else:
            messages.error(request, "Privilege set not found.")
    return redirect('privilege_list')

@login_required
def group_list(request):
    groups = GroupService.get_all_groups()
    context = {
        "view": "Groups",
        "user": request.user,
        "groups": groups
    }
    return render(request, "group_list.html", context)

@login_required
def group_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        user_ids = request.POST.getlist('users')
        team_ids = request.POST.getlist('teams')

        if name:
            GroupService.create_group(name, description, is_active, user_ids, team_ids)
            messages.success(request, f"Group '{name}' created successfully.")
            return redirect('group_list')
        else:
            messages.error(request, "Name is a required field.")

    users = UserInstance.objects.filter(isActive=True)
    teams = SupportTeam.objects.filter(isActive=True)
    context = {
        "view": "Groups",
        "user": request.user,
        "users": users,
        "teams": teams
    }
    return render(request, "group_create.html", context)

@login_required
def group_edit(request, group_id):
    group = GroupService.get_group_by_id(group_id)
    if not group:
        messages.error(request, "Group not found.")
        return redirect('group_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        user_ids = request.POST.getlist('users')
        team_ids = request.POST.getlist('teams')

        if name:
            GroupService.update_group(group_id, name, description, is_active, user_ids, team_ids)
            messages.success(request, f"Group '{name}' updated successfully.")
            return redirect('group_list')
        else:
            messages.error(request, "Name is a required field.")

    users = UserInstance.objects.filter(isActive=True)
    teams = SupportTeam.objects.filter(isActive=True)
    context = {
        "view": "Groups",
        "user": request.user,
        "group": group,
        "users": users,
        "teams": teams
    }
    return render(request, "group_edit.html", context)

@login_required
def group_delete(request, group_id):
    if request.method == 'POST':
        group = GroupService.get_group_by_id(group_id)
        if group:
            GroupService.delete_group(group_id)
            messages.success(request, f"Group '{group.name}' deleted successfully.")
        else:
            messages.error(request, "Group not found.")
    return redirect('group_list')

# Team Views
@login_required
def team_list(request):
    teams = TeamService.get_all_teams()
    context = {
        "view": "Teams",
        "user": request.user,
        "teams": teams
    }
    return render(request, "team_list.html", context)

@login_required
def team_create(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        user_ids = request.POST.getlist('users')
        group_ids = request.POST.getlist('groups')

        if name:
            TeamService.create_team(name, description, is_active, user_ids, group_ids)
            messages.success(request, f"Team '{name}' created successfully.")
            return redirect('team_list')
        else:
            messages.error(request, "Name is a required field.")

    users = UserInstance.objects.filter(isActive=True)
    groups = SupportGroup.objects.filter(isActive=True)
    context = {
        "view": "Teams",
        "user": request.user,
        "users": users,
        "groups": groups
    }
    return render(request, "team_create.html", context)

@login_required
def team_edit(request, team_id):
    team = TeamService.get_team_by_id(team_id)
    if not team:
        messages.error(request, "Team not found.")
        return redirect('team_list')

    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        user_ids = request.POST.getlist('users')
        group_ids = request.POST.getlist('groups')

        if name:
            TeamService.update_team(team_id, name, description, is_active, user_ids, group_ids)
            messages.success(request, f"Team '{name}' updated successfully.")
            return redirect('team_list')
        else:
            messages.error(request, "Name is a required field.")

    users = UserInstance.objects.filter(isActive=True)
    groups = SupportGroup.objects.filter(isActive=True)
    context = {
        "view": "Teams",
        "user": request.user,
        "team": team,
        "users": users,
        "groups": groups
    }
    return render(request, "team_edit.html", context)

@login_required
def team_delete(request, team_id):
    if request.method == 'POST':
        team = TeamService.get_team_by_id(team_id)
        if team:
            TeamService.delete_team(team_id)
            messages.success(request, f"Team '{team.name}' deleted successfully.")
        else:
            messages.error(request, "Team not found.")
    return redirect('team_list')


@login_required
def agent_invite(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        firstName = request.POST.get('firstName')
        lastName = request.POST.get('lastName')

        if not email or not firstName:
            messages.error(request, "Email and First Name are required.")
            return render(request, "agent_invite.html", {"view": "Agents"})

        if User.objects.filter(email=email).exists():
            messages.error(request, f"A user with the email '{email}' already exists.")
            return render(request, "agent_invite.html", {"view": "Agents"})

        # Create the user with an unusable password
        user = User.objects.create_user(email=email, firstName=firstName, lastName=lastName)
        user.set_unusable_password()
        user.save()

        # Create the user instance and assign the agent role
        agent_role, _ = SupportRole.objects.get_or_create(code='ROLE_AGENT')
        UserInstance.objects.create(user=user, supportRole=agent_role, isActive=True, source='website')

        # Generate password set link (using Django's password reset mechanism)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        invite_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Send the invitation email via the EmailManager
        EmailManager.send_agent_invite_email(user, invite_link)

        messages.success(request, f"Invitation sent successfully to {email}. The email content will be printed to the console.")
        return redirect('dashboard') # Or wherever you want to redirect after invite

    context = {
        "view": "Agents",
        "user": request.user
    }
    return render(request, "agent_invite.html", context)


def page404(request):
    user = request.user
    context = {"view": "Dashboard", "user": user}
    return render(request, "404.html", context)
