from django import forms
from .models import EmailTemplate

class EmailTemplateForm(forms.ModelForm):
    class Meta:
        model = EmailTemplate
        fields = ['name', 'subject', 'body', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'style': 'width: 100%;'}),
            'subject': forms.TextInput(attrs={'style': 'width: 100%;'}),
            'body': forms.Textarea(attrs={'class': 'summernote'}),
        }