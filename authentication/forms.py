from django import forms
from .models import User, UserInstance, SupportRole, SupportPrivilege, SupportGroup, SupportTeam


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'firstName', 'lastName']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'firstName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'lastName': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
        }


class UserInstanceForm(forms.ModelForm):
    # Choices for ticketAccessLevel
    TICKET_ACCESS_LEVEL_CHOICES = [
        ('global', 'Global Access'),
        ('group', 'Group Access'),
        ('team', 'Team Access'),
        ('individual', 'Individual Access'),
    ]

    profileImage = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control-file'}))
    contactNumber = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Number'}))
    designation = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Designation'}))
    signature = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Signature', 'rows': 3}))
    isActive = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    supportRole = forms.ModelChoiceField(
        queryset=SupportRole.objects.all(),
        required=False,
        empty_label="Select agent role",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    supportPrivileges = forms.ModelMultipleChoiceField(
        queryset=SupportPrivilege.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    supportGroups = forms.ModelMultipleChoiceField(
        queryset=SupportGroup.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    supportTeams = forms.ModelMultipleChoiceField(
        queryset=SupportTeam.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    ticketAccessLevel = forms.ChoiceField(
        choices=TICKET_ACCESS_LEVEL_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = UserInstance
        fields = [
            'profileImage', 'designation', 'contactNumber', 'signature', 'isActive',
            'supportRole', 'supportPrivileges', 'supportGroups', 'supportTeams', 'ticketAccessLevel'
        ]
