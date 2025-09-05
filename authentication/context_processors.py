from .decorators import has_permission as actual_has_permission # Rename to avoid conflict
from .models import UserInstance
from authentication.constants import PRIVILEGE_CHOICES # Import PRIVILEGE_CHOICES


def permission_context(request):
    """
    Context processor to add a dictionary of user's permissions to all templates.
    """
    user_permissions = {}
    user_instance = None

    if request.user.is_authenticated:
        try:
            user_instance = UserInstance.objects.filter(user=request.user).first()
        except UserInstance.DoesNotExist:
            pass # User has no UserInstance

    # Populate user_permissions dictionary
    # Iterate through all possible privilege codes
    for category_privileges in PRIVILEGE_CHOICES.values():
        for code in category_privileges.keys():
            user_permissions[code] = actual_has_permission(user_instance, code)

    return {
        'perms': user_permissions # Use a simpler name like 'perms'
    }
