from django.shortcuts import redirect
from django.urls import reverse
from authentication.models import UserInstance, SupportRole

def admin_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('login')) # Redirect to admin login

        # Check if the user has an admin/agent UserInstance
        try:
            user_instance = UserInstance.objects.get(user=request.user)
            admin_roles = ['ROLE_SUPER_ADMIN', 'ROLE_ADMIN', 'ROLE_AGENT']
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
