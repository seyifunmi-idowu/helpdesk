from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

class EmailManager:

    @staticmethod
    def send_agent_invite_email(user, invite_link):
        """
        Sends the initial invitation email to a new agent.
        """
        subject = "You're invited to join the Helpdesk"
        # In the future, we can create a nice HTML template for this.
        # For now, a plain text message is clear and effective.
        message = f"""
        Hello {user.firstName},

        You have been invited to join the helpdesk.
        Please set your password by visiting the following link:
        {invite_link}

        Thanks,
        The Admin Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )

    @staticmethod
    def send_password_reset_email(user, reset_link):
        """
        Sends a password reset link to an existing user.
        """
        subject = "Reset your password"
        message = f"""
        Hello {user.firstName},

        Please reset your password by visiting the following link:
        {reset_link}

        If you did not request a password reset, please ignore this email.

        Thanks,
        The Admin Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
