from django import forms
from ticket.models import TicketType, TicketPriority

class PublicTicketForm(forms.Form):
    email = forms.EmailField(label='Your Email', max_length=255)
    subject = forms.CharField(label='Subject', max_length=255)
    message = forms.CharField(label='Message', widget=forms.Textarea)
    ticket_type = forms.ModelChoiceField(queryset=TicketType.objects.all(), label='Ticket Type')
    ticket_priority = forms.ModelChoiceField(queryset=TicketPriority.objects.all(), label='Ticket Priority')
