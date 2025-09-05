import imaplib
import email
from django.core.management.base import BaseCommand
from django.conf import settings
from settings.models import UvMailbox, WebsiteKnowledgebase
from ticket.models import Ticket, Thread, TicketStatus, TicketPriority, TicketType
from django.db import models
from authentication.models import User, UserInstance, SupportRole
from django.utils import timezone
import re


class Command(BaseCommand):
  help = 'Fetches emails from configured mailboxes and creates tickets.'

  def _get_or_create_user_instance(self, email_address, full_name=None):
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
    if created_user:
      self.stdout.write(self.style.SUCCESS(f'Created new User: {user.email}'))

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
    if created_instance:
      self.stdout.write(self.style.SUCCESS(f'Created new UserInstance for: {user.email}'))

    return user_instance

  def handle(self, *args, **options):
    self.stdout.write(self.style.SUCCESS('Starting email fetching process...'))

    # Get or create default ticket status, priority, and type
    default_status, _ = TicketStatus.objects.get_or_create(code='Open', defaults={'description': 'Open Ticket'})
    default_priority, _ = TicketPriority.objects.get_or_create(code='Low', defaults={'description': 'Low Priority'})
    default_type, _ = TicketType.objects.get_or_create(code='Question', defaults={'description': 'General Question'})

    mailboxes = UvMailbox.objects.filter(is_enabled=True)

    if not mailboxes.exists():
      self.stdout.write(self.style.WARNING('No active mailboxes configured. Exiting.'))
      return

    # Get blacklist settings
    try:
        website_kb = WebsiteKnowledgebase.objects.first()
        if website_kb:
            blacklist = website_kb.black_list or []
        else:
            blacklist = []
    except Exception as e:
        self.stdout.write(self.style.ERROR(f"Could not load blacklist settings: {e}"))
        blacklist = []

    for mailbox in mailboxes:
      self.stdout.write(self.style.SUCCESS(f'Connecting to mailbox: {mailbox.name} ({mailbox.email})'))
      try:
        # Connect to IMAP server
        if mailbox.imap_encryption == 'ssl':
          mail = imaplib.IMAP4_SSL(mailbox.imap_host, mailbox.imap_port)
        else:  # 'tls' or 'null' - for simplicity, using IMAP4 for non-SSL
          mail = imaplib.IMAP4(mailbox.imap_host, mailbox.imap_port)

        mail.login(mailbox.imap_username, mailbox.imap_password)
        mail.select('inbox')  # Select the inbox

        status, email_ids = mail.search(None, 'ALL')  # Search for all emails (for testing)
        if status != 'OK':
          self.stdout.write(self.style.ERROR(f'Failed to search emails for {mailbox.email}: {status}'))
          continue

        email_ids = email_ids[0].split()
        latest_email_ids = email_ids[-10:]
        # latest_email_ids = email_ids
        for email_id in latest_email_ids:
          status, msg_data = mail.fetch(email_id, '(RFC822)')
          if status != 'OK':
            self.stdout.write(self.style.ERROR(f'Failed to fetch email {email_id} for {mailbox.email}: {status}'))
            continue

          msg = email.message_from_bytes(msg_data[0][1])

          # Extract email details
          subject = msg['subject'] if msg['subject'] else '(No Subject)'
          from_header = msg['from']
          message_id = msg['Message-ID'] if 'Message-ID' in msg else None

          # Parse email date
          received_at = None

          # 1. Try to get INTERNALDATE from IMAP
          status, date_data = mail.fetch(email_id, '(INTERNALDATE)')
          if status == 'OK' and date_data and date_data[0]:
              try:
                  date_str_match = re.search(r'INTERNALDATE "([^"]+)"', date_data[0].decode())
                  if date_str_match:
                      date_str = date_str_match.group(1)
                      from email.utils import parsedate_to_datetime
                      parsed_date = parsedate_to_datetime(date_str)
                      if parsed_date:
                          if parsed_date.tzinfo is None:
                              # Assume local timezone if no tzinfo, then convert to UTC
                              received_at = timezone.make_aware(parsed_date, timezone.get_current_timezone()).astimezone(timezone.utc)
                          else:
                              received_at = parsed_date.astimezone(timezone.utc)
              except Exception as e:
                  self.stdout.write(self.style.WARNING(f'Could not parse INTERNALDATE from "{date_data[0].decode()}": {e}'))

          # 2. If INTERNALDATE fails, fall back to 'Date' header
          if not received_at:
              date_header = msg['Date'] if 'Date' in msg else None
              if date_header:
                  try:
                      from email.utils import parsedate_to_datetime
                      parsed_date = parsedate_to_datetime(date_header)
                      if parsed_date:
                          if parsed_date.tzinfo is None:
                              # Assume local timezone if no tzinfo, then convert to UTC
                              received_at = timezone.make_aware(parsed_date, timezone.get_current_timezone()).astimezone(timezone.utc)
                          else:
                              received_at = parsed_date.astimezone(timezone.utc)
                  except Exception as e:
                      self.stdout.write(self.style.WARNING(f'Could not parse Date header "{date_header}": {e}'))

          # 3. If all else fails, use current time
          if not received_at:
              received_at = timezone.now()

          # Parse from_address to get name and email
          from_name = None
          from_email = None
          if from_header:
            # Fixed regex pattern - properly closed string
            match = re.match(r'^(.*?)<(.*?)>
, from_header)
            if match:
              from_name = match.group(1).strip().strip('"')
              from_email = match.group(2).strip()
            else:
              from_email = from_header.strip()
              from_name = from_email.split('@')[0]  # Fallback to local part of email

          # --- Blacklist Check ---
          if from_email:
              from_email_lower = from_email.lower()
              if from_email_lower in blacklist:
                  self.stdout.write(self.style.WARNING(f"'{from_email}' is in the blacklist. Skipping."))
                  continue
          # --- End Blacklist Check ---

          # Extract email body
          html_body = None
          plain_body = None

          for part in msg.walk():
              ctype = part.get_content_type()
              cdispo = str(part.get('Content-Disposition'))

              # skip attachments
              if cdispo and 'attachment' in cdispo:
                  continue

              charset = part.get_content_charset() or 'utf-8'

              if ctype == 'text/html':
                  try:
                      html_body = part.get_payload(decode=True).decode(charset)
                  except Exception:
                      html_body = part.get_payload(decode=True).decode('latin-1', errors='ignore')
              elif ctype == 'text/plain':
                  try:
                      plain_body = part.get_payload(decode=True).decode(charset)
                  except Exception:
                      plain_body = part.get_payload(decode=True).decode('latin-1', errors='ignore')

          body = html_body or plain_body

          # Fallback for non-multipart messages that are not text/plain or text/html
          if not body and not msg.is_multipart():
              try:
                  body = msg.get_payload(decode=True).decode(msg.get_content_charset() or 'utf-8')
              except (UnicodeDecodeError, AttributeError):
                  body = msg.get_payload(decode=True).decode('latin-1', errors='ignore')  # Fallback

          body = body or ""

          self.stdout.write(self.style.SUCCESS(f'Fetched email from {from_email} with subject: {subject}'))

          # Check for duplicate thread using Message-ID
          if message_id and Thread.objects.filter(messageId=message_id).exists():
            self.stdout.write(self.style.WARNING(f'Skipping duplicate email with Message-ID: {message_id}'))
            continue

          # --- Threading Logic for Incoming Emails ---
          in_reply_to = msg['In-Reply-To'] if 'In-Reply-To' in msg else None
          references = msg['References'] if 'References' in msg else None

          # Try to find an existing ticket based on In-Reply-To or References
          existing_ticket = None
          if in_reply_to:
              existing_ticket = Ticket.objects.filter(
                  threads__messageId=in_reply_to
              ).first()

          if not existing_ticket and references:
              # Split references into individual message IDs
              ref_ids = references.split()
              for ref_id in ref_ids:
                  existing_ticket = Ticket.objects.filter(
                      models.Q(threads__messageId=ref_id) | models.Q(reference_ids__contains=ref_id)
                  ).first()
                  if existing_ticket:
                      break # Found a matching ticket

          # Get or create UserInstance for the sender
          customer_user_instance = self._get_or_create_user_instance(from_email, from_name)

          try: # Start of the try block for ticket/thread creation
              if existing_ticket:
                  # If ticket found, add new thread to it
                  current_ticket = existing_ticket
                  self.stdout.write(self.style.SUCCESS(f'Found existing Ticket ID: {current_ticket.id} for reply.'))
              else:
                  # No existing ticket found, create a new one
                  current_ticket = Ticket.objects.create(
                      subject=subject,
                      source='email',
                      customer=customer_user_instance,
                      mailboxEmail=mailbox.email,
                      status=default_status,
                      priority=default_priority,
                      type=default_type,
                      createdAt=received_at,
                      updatedAt=timezone.now(),
                      reference_ids=references # Store references for future threading
                  )
                  self.stdout.write(self.style.SUCCESS(f'Created new Ticket: {current_ticket.subject} (ID: {current_ticket.id})'))

              # Extract and add CC/BCC as collaborators (existing logic, ensure it uses current_ticket)
              cc_headers = msg.get_all('Cc', [])
              bcc_headers = msg.get_all('Bcc', [])

              all_cc_bcc_emails = []
              for header_value in cc_headers + bcc_headers:
                  for name, addr in email.utils.getaddresses([header_value]):
                      if addr:
                          all_cc_bcc_emails.append(addr)

              for cc_bcc_email in all_cc_bcc_emails:
                  try:
                      collaborator_user_instance = self._get_or_create_user_instance(cc_bcc_email)
                      if collaborator_user_instance != customer_user_instance and \
                         collaborator_user_instance not in current_ticket.collaborators.all():
                          current_ticket.collaborators.add(collaborator_user_instance)
                          self.stdout.write(self.style.SUCCESS(f'Added {cc_bcc_email} as collaborator to Ticket ID: {current_ticket.id}'))
                  except Exception as collab_e:
                      self.stdout.write(self.style.ERROR(f'Error adding CC/BCC {cc_bcc_email} as collaborator: {collab_e}'))

              # Create Thread for the current_ticket
              Thread.objects.create(
                  ticket=current_ticket,
                  user=customer_user_instance,
                  source='email',
                  message=body,
                  threadType='incoming_email',
                  messageId=message_id,
                  createdAt=received_at,
                  updatedAt=timezone.now(),
              )
              self.stdout.write(self.style.SUCCESS(f'Created new Thread for Ticket ID: {current_ticket.id}'))

          except Exception as create_e:
              self.stdout.write(self.style.ERROR(f'Error creating ticket/thread for {from_email}: {create_e}'))
              # Optionally, mark email as unseen or move to error folder if ticket creation fails

          # Mark email as seen (optional, depending on requirements)
          # mail.store(email_id, '+FLAGS', '\Seen')

          if mailbox.delete_after_fetch:
            mail.store(email_id, '+FLAGS', '\Deleted')
            mail.expunge()  # Permanently delete

        mail.close()
        mail.logout()
        self.stdout.write(self.style.SUCCESS(f'Successfully processed mailbox: {mailbox.email}'))

      except Exception as e:
        self.stdout.write(self.style.ERROR(f'Error processing mailbox {mailbox.email}: {e}'))

    self.stdout.write(self.style.SUCCESS('Email fetching process completed.'))
