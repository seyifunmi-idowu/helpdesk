from authentication.models import User, UserInstance, SupportRole
from django.utils import timezone
import re

def get_or_create_user_instance(email_address, full_name=None):
    # Clean up email address
    email_address = email_address.strip().lower()

    # Try to find existing User
    user, created_user = User.objects.get_or_create(
        email=email_address,
        defaults={
            'firstName': full_name.split(' ')[0] if full_name else 'Unknown',
            'lastName': ' '.join(full_name.split(' ')[1:]) if full_name and len(full_name.split(' ')) > 1 else '',
            'isEnabled': True,
            'is_active': True,
        }
    )

    # Get or create ROLE_CUSTOMER SupportRole
    customer_role, _ = SupportRole.objects.get_or_create(code='ROLE_CUSTOMER')

    # Try to find existing UserInstance
    user_instance, created_instance = UserInstance.objects.get_or_create(
        user=user,
        source='email',  # Assuming 'email' as source for fetched users
        defaults={
            'isActive': True,
            'isVerified': True,
            'supportRole': customer_role,
        }
    )
    return user_instance