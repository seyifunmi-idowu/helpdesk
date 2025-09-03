from django import forms
from .models import UvSwiftmailer, UvMailbox, UvEmailSettings, EmailTemplate

class UvSwiftmailerForm(forms.ModelForm):
    class Meta:
        model = UvSwiftmailer
        fields = '__all__'
        widgets = {
            'password': forms.PasswordInput(render_value=True),
        }

class UvMailboxForm(forms.ModelForm):
    class Meta:
        model = UvMailbox
        fields = '__all__'
        widgets = {
            'imap_password': forms.PasswordInput(render_value=True),
        }

class UvEmailSettingsForm(forms.ModelForm):
    class Meta:
        model = UvEmailSettings
        fields = '__all__'

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = '__all__'
