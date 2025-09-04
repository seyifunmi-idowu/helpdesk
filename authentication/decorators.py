from django.shortcuts import redirect
from django.urls import reverse
from authentication.models import UserInstance, SupportRole
from functools import wraps


ADMIN_ROLES = ['ROLE_SUPER_ADMIN', 'ROLE_ADMIN', 'ROLE_AGENT']


def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login')) # Redirect to admin login

        # Check if the user has an admin/agent UserInstance
        try:
            user_instance = UserInstance.objects.get(user=request.user)
            admin_roles = ADMIN_ROLES
            if user_instance.supportRole and user_instance.supportRole.code in admin_roles:
                return view_func(request, *args, **kwargs)
        except UserInstance.DoesNotExist:
            pass # User has no UserInstance, or not an admin/agent one

        # If not an admin/agent, redirect to admin login or an unauthorized page
        return redirect(reverse('login')) # Or a specific unauthorized page
    return wrapper

def customer_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login')) # Redirect to customer login

        # Check if the user has a customer UserInstance
        try:
            user_instance = UserInstance.objects.get(user=request.user)
            if user_instance.supportRole and user_instance.supportRole.code == 'ROLE_CUSTOMER':
                return view_func(request, *args, **kwargs)
        except UserInstance.DoesNotExist:
            pass # User has no UserInstance, or not a customer one

        # If not a customer, redirect to customer login or an unauthorized page
        return redirect(reverse('login')) # Or a specific unauthorized page
    return wrapper


def has_permission(user_instance, privilege_code):
    """
    Checks if a UserInstance has a specific privilege.
    """
    if not user_instance:
        return False

    # Super admin always has all permissions
    if user_instance.supportRole and user_instance.supportRole.code in ADMIN_ROLES:
        return True

    for privilege_set in user_instance.supportPrivileges.all():
        if privilege_set.privileges and privilege_set.privileges.get(privilege_code) is True:
            return True
    return False

def permission_required(privilege_codes):
    """
    Decorator to check if the logged-in user has the specified privileges.
    Redirects to dashboard if not authenticated or lacks permission.
    """
    if not isinstance(privilege_codes, (list, tuple)):
        privilege_codes = [privilege_codes] # Ensure it's always a list

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(reverse('login')) # Redirect to login page

            try:
                user_instance = UserInstance.objects.get(user=request.user)
            except UserInstance.DoesNotExist:
                return redirect(reverse('dashboard')) # Redirect to dashboard or a generic error page

            # Check if user has all required privileges
            for code in privilege_codes:
                if not has_permission(user_instance, code):
                    return redirect(reverse('dashboard')) # Redirect to dashboard

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
