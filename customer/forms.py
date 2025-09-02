from django import forms
from ticket.models import TicketType, TicketPriority
from authentication.models import User, UserInstance
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm


class PublicTicketForm(forms.Form):
    email = forms.EmailField(label='Your Email', max_length=255)
    subject = forms.CharField(label='Subject', max_length=255)
    message = forms.CharField(label='Message', widget=forms.Textarea)
    ticket_type = forms.ModelChoiceField(queryset=TicketType.objects.all(), label='Ticket Type')
    ticket_priority = forms.ModelChoiceField(queryset=TicketPriority.objects.all(), label='Ticket Priority')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['firstName', 'lastName', 'email', 'timezone', 'timeformat']
        widgets = {
            'firstName': forms.TextInput(attrs={'class': 'form-control'}),
            'lastName': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'readonly': 'readonly'}), # Email usually not editable
            'timezone': forms.TextInput(attrs={'class': 'form-control'}),
            'timeformat': forms.TextInput(attrs={'class': 'form-control'}),
        }


class UserInstanceProfileForm(forms.ModelForm):
    class Meta:
        model = UserInstance
        fields = ['profileImage', 'contactNumber', 'designation', 'signature']
        widgets = {
            'profileImage': forms.FileInput(attrs={'class': 'form-control-file'}),
            'contactNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'designation': forms.TextInput(attrs={'class': 'form-control'}),
            'signature': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class PasswordChangeForm(forms.Form):
    new_password1 = forms.CharField(
        label="New password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
        help_text="Enter your new password."
    )
    new_password2 = forms.CharField(
        label="New password confirmation",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as before, for verification."
    )

    def clean_new_password2(self):
        password2 = self.cleaned_data.get('new_password2')
        password1 = self.cleaned_data.get('new_password1')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, user):
        user.set_password(self.cleaned_data["new_password1"])
        user.save()
        return user