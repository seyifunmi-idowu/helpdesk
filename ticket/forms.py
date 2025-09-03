from django import forms
from .models import Workflow, TicketType, Tag, SavedReplies, PreparedResponse, Thread, TicketStatus, TicketPriority
from authentication.models import SupportGroup, SupportTeam
import re

class WorkflowForm(forms.ModelForm):
    conditions = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter JSON for conditions'}), required=False)
    actions = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter JSON for actions'}), required=False)

    class Meta:
        model = Workflow
        fields = ['name', 'description', 'conditions', 'actions', 'status', 'is_predefind']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Workflow Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_predefind': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_conditions(self):
        data = self.cleaned_data['conditions']
        if data:
            try:
                import json
                json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Conditions must be valid JSON.")
        return data

    def clean_actions(self):
        data = self.cleaned_data['actions']
        if data:
            try:
                import json
                json.loads(data)
            except json.JSONDecodeError:
                raise forms.ValidationError("Actions must be valid JSON.")
        return data

class TicketTypeForm(forms.ModelForm):
    class Meta:
        model = TicketType
        fields = ['code', 'description', 'isActive']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Code'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'isActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tag Name'}),
        }

class SavedReplyForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=SupportGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Groups"
    )
    teams = forms.ModelMultipleChoiceField(
        queryset=SupportTeam.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Teams"
    )

    class Meta:
        model = SavedReplies
        fields = ['name', 'subject', 'message', 'isPredefind', 'templateFor', 'groups', 'teams']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Reply Name'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}),
            'message': forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 10, 'placeholder': 'Message'}), # Add summernote class
            'isPredefind': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'templateFor': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Template For (e.g., email, chat)'}),
        }

class PreparedResponseForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=SupportGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Groups"
    )
    teams = forms.ModelMultipleChoiceField(
        queryset=SupportTeam.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Teams"
    )

    class Meta:
        model = PreparedResponse
        fields = ['name', 'description', 'type', 'groups', 'teams']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prepared Response Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description'}),
            'type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Type (e.g., public, private)'}),
        }

class ThreadForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=TicketStatus.objects.all(), required=False)
    send_to_collaborators_cc_bcc = forms.BooleanField(
        label="Send to Collaborators (CC/BCC)",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    class Meta:
        model = Thread
        fields = ['message', 'status'] # These are model fields, new fields are form fields
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 5, 'placeholder': 'Enter your reply...'}),
        }

class NoteForm(forms.ModelForm):
    status = forms.ModelChoiceField(queryset=TicketStatus.objects.all(), required=False)

    class Meta:
        model = Thread
        fields = ['message', 'status']
        widgets = {
            'message': forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 5, 'placeholder': 'Enter your note...'}),
        }

class ForwardForm(forms.Form):
    to = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'To'}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 5, 'placeholder': 'Enter your message...'}))
    status = forms.ModelChoiceField(queryset=TicketStatus.objects.all(), required=False)

class CollaboratorForm(forms.Form):
    emails = forms.CharField(
        label="Collaborator Emails (comma-separated)",
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter comma-separated email addresses (e.g., email1@example.com, email2@example.com)'
        }),
        help_text="Enter comma-separated email addresses. New customer accounts will be created for non-existent emails."
    )

    def clean_emails(self):
        emails_string = self.cleaned_data['emails']
        email_list = [email.strip() for email in emails_string.split(',') if email.strip()]

        # Basic email validation regex
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

        for email in email_list:
            if not re.match(email_regex, email):
                raise forms.ValidationError(f"'{email}' is not a valid email address.")
        return email_list


from .models import Ticket # Import Ticket model
from authentication.models import UserInstance, SupportGroup, SupportTeam, User # Import UserInstance for customer/agent selection

class TicketForm(forms.ModelForm):
    # Custom field for customer email, as customer is a UserInstance
    customer_email = forms.EmailField(
        label="Customer Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Customer Email Address'}),
        help_text="Enter the customer's email address. A new account will be created if it doesn't exist."
    )

    # Initial message for the ticket
    initial_message = forms.CharField(
        label="Initial Message",
        widget=forms.Textarea(attrs={'class': 'form-control summernote', 'rows': 5, 'placeholder': 'Enter the initial message for the ticket...'}),
        required=True
    )

    class Meta:
        model = Ticket
        fields = [
            'subject', 'status', 'priority', 'type',
            'agent', 'supportGroup', 'supportTeam',
            # 'customer' is handled by customer_email field
        ]
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ticket Subject'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'priority': forms.Select(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'agent': forms.Select(attrs={'class': 'form-control'}),
            'supportGroup': forms.Select(attrs={'class': 'form-control'}),
            'supportTeam': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate choices for agent, status, priority, type, group, team
        self.fields['agent'].queryset = UserInstance.objects.filter(supportRole__code='ROLE_AGENT')
        self.fields['status'].queryset = TicketStatus.objects.all()
        self.fields['priority'].queryset = TicketPriority.objects.all()
        self.fields['type'].queryset = TicketType.objects.all()
        self.fields['supportGroup'].queryset = SupportGroup.objects.all()
        self.fields['supportTeam'].queryset = SupportTeam.objects.all()

        # Make agent, group, team optional with a blank choice
        self.fields['agent'].empty_label = "Unassigned"
        self.fields['supportGroup'].empty_label = "Not Assigned"
        self.fields['supportTeam'].empty_label = "Not Assigned"

    def clean_customer_email(self):
        email = self.cleaned_data['customer_email']
        # Basic email validation is already done by forms.EmailField
        return email

    def save(self, commit=True):
        ticket = super().save(commit=False)

        # Handle customer creation/retrieval
        customer_email = self.cleaned_data['customer_email']
        # Assuming get_or_create_user_instance is available (from services.py)
        # This will need to be imported in views.py when using this form
        from ticket.services import get_or_create_user_instance
        customer_instance = get_or_create_user_instance(customer_email)
        ticket.customer = customer_instance

        if commit:
            ticket.save()
        return ticket
