from django import forms
from .models import Workflow, TicketType, Tag, SavedReplies, PreparedResponse, Thread, TicketStatus
from authentication.models import SupportGroup, SupportTeam

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

    class Meta:
        model = Thread
        fields = ['message', 'status']
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
