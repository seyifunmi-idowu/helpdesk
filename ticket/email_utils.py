from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from ticket.models import Thread # Import Thread model
import uuid # Added this import

def send_reply_email(ticket, thread, send_to_collaborators_cc_bcc=False):
    subject = f"Reply to your ticket #{ticket.id}: {ticket.subject}"
    html_message = thread.message
    plain_message = None

    to_recipients = [ticket.customer.user.email]
    cc_recipients = []
    bcc_recipients = []

    # Add agent to CC if assigned
    if ticket.agent and ticket.agent.user.email != ticket.customer.user.email:
        cc_recipients.append(ticket.agent.user.email)

    # Add collaborators to CC/BCC if selected
    if send_to_collaborators_cc_bcc:
        for collaborator in ticket.collaborators.all():
            if collaborator.user.email not in to_recipients and \
               collaborator.user.email not in cc_recipients and \
               collaborator.user.email not in bcc_recipients:
                cc_recipients.append(collaborator.user.email)

    # Ensure no duplicate recipients
    to_recipients = list(set(to_recipients))
    cc_recipients = list(set(cc_recipients))
    bcc_recipients = list(set(bcc_recipients))

    # --- Threading Headers ---
    headers = {}
    # Get all message IDs for this ticket to build References header
    all_thread_message_ids = [
        t.messageId for t in ticket.threads.all().order_by('createdAt') if t.messageId
    ]

    # Find the Message-ID of the last incoming email to set In-Reply-To
    last_incoming_thread = ticket.threads.filter(threadType='incoming_email').order_by('-createdAt').first()
    if last_incoming_thread and last_incoming_thread.messageId:
        headers['In-Reply-To'] = last_incoming_thread.messageId
        # Ensure the last incoming message ID is in references
        if last_incoming_thread.messageId not in all_thread_message_ids:
            all_thread_message_ids.append(last_incoming_thread.messageId)

    if all_thread_message_ids:
        headers['References'] = ' '.join(all_thread_message_ids)
    # --- End Threading Headers ---

    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        to_recipients,
        cc=cc_recipients,
        bcc=bcc_recipients,
        headers=headers # Pass the custom headers
    )
    email.content_subtype = "html"

    try:
        email.send(fail_silently=False)
        print(f"Email sent for ticket {ticket.id} to {to_recipients}, CC: {cc_recipients}, BCC: {bcc_recipients}")
    except Exception as e:
        print(f"Failed to send email for ticket {ticket.id}: {e}")

        # Log the error or handle it appropriately

def send_forward_email(ticket, thread, to_email_addresses, subject):
    html_message = thread.message # The message from the forward form

    to_recipients = [email.strip() for email in to_email_addresses.split(',') if email.strip()]

    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        to_recipients,
    )
    email.content_subtype = "html"

    try:
        email.send(fail_silently=False)
        print(f"Forward email sent for ticket {ticket.id} to {to_recipients}")
    except Exception as e:
        print(f"Failed to send forward email for ticket {ticket.id}: {e}")
        raise # Re-raise the exception so the view can catch it and display a message

def send_initial_ticket_email(ticket, initial_thread):
    subject = ticket.subject
    html_message = initial_thread.message # The initial message from the form

    to_recipients = [ticket.customer.user.email]

    # Generate a unique Message-ID
    message_id = f"<{uuid.uuid4()}@{settings.EMAIL_HOST.split(':')[-1]}>" # Use EMAIL_HOST for domain

    headers = {'Message-ID': message_id}

    email = EmailMessage(
        subject,
        html_message,
        settings.DEFAULT_FROM_EMAIL,
        to_recipients,
        headers=headers # Pass the custom headers
    )
    email.content_subtype = "html"

    try:
        email.send(fail_silently=False)
        print(f"Initial ticket email sent for ticket {ticket.id} to {to_recipients} with Message-ID: {message_id}")
        return message_id # Return the generated Message-ID
    except Exception as e:
        print(f"Failed to send initial ticket email for ticket {ticket.id}: {e}")
        raise # Re-raise the exception so the view can catch it and display a message
